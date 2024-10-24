import requests
import firebase_admin
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from firebase_admin import messaging
from rest_framework import status

from config.mongo import get_mongo_client
from generics.services import BaseService
from loguru_conf import logger
from notifications.models import UserDevice
from system_msg import (
    REQUIRED_FIELD,
    USER_NOT_FOUND,
    NOTIFACTIONS_DISALLOWED,
)


session = requests.Session()
session.trust_env = False


class NotifyUserService(BaseService):
    def __validate_fields(self, data: dict) -> tuple:
        msg = {"message": {}}
        error_message = [REQUIRED_FIELD]
        for i in ["title", "body", "subs_id"]:
            if i not in data.keys():
                msg[i] = error_message
        
        if len(msg["message"]):
            return False, msg
        return True, msg
    
    def send_notification(self, data: dict, devices: list):
        devices = devices["data"]
        logger.debug(f"send notification: {data}")
        logger.debug(f"send notification devices: {devices}")
        client = get_mongo_client()
        collection = client["notifications"]
        
        # send notification to fcm
        tokens = [
            device['push_notification_token'] for device in devices
        ]
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=data.get("title"),
                body=data.get("body"),
            ),
            tokens=tokens,
        )
        try:
            response = messaging.send_multicast(message)
            # response = "asdlfnlan2l12ndasdf"
            logger.debug(f'Successfully sent message: {response}')
        except firebase_admin.exceptions.FirebaseError as e:
            logger.debug(f'Error sending message: {str(e)}')
            return {"sent": False}
        
        # save result to mongodb
        doc = {
                # "message_id": f"{response.text}",
                "message_id": f"{response}",
                "title": data.get("title"),
                "push_body": data.get("body"),
                "sent_subs": tokens,
                "subs_received": []
        }
        # res = collection.insert_one(doc)
        res = 200
        logger.debug(f"save to mongo: {res}")
    
    def check_notifications_allowed(self, data: dict) -> tuple[bool, dict]:
        result = {
            "msg": "",
            "data": []
        }
        subs_id = data.get("subs_id")
        users = UserDevice.objects.filter(subs_id=subs_id)
        if not users:
            result["msg"] = {"message": USER_NOT_FOUND}
            return False, result
        users = users.filter(allow_notifications=True)
        if users:
            result["data"] = users.values("push_notification_token", "device_id")
            return True, result
        result["msg"] = {"message": NOTIFACTIONS_DISALLOWED}
        return False, result
            
    def execute(self) -> tuple:
        request = self.context.get("request")
        language = request.headers.get("Accept-Language", "ru")
        translation.activate(language)
        
        # request data is valid
        is_valid, msg = self.__validate_fields(request.data)
        if not is_valid:
            return msg, status.HTTP_400_BAD_REQUEST
        
        # get users and check if notifications are allowed
        allowed, devices = self.check_notifications_allowed(request.data)
        logger.debug(f"if allowed: {allowed}, msg: {devices}")
        if not allowed:
            return devices["msg"]
        
        # send notification
        self.send_notification(request.data, devices)
        return {"msg": "ok"}, status.HTTP_200_OK


class NotificationRecievedService(BaseService):
    def receive_notification(self, data):
        message_id = data.get("message_id")
        client = get_mongo_client()
        collection = client["notifications"]
        document = collection.find_one(
            {"message_id": data.get("message_id")}
        )
        logger.debug(document)
        result = collection.update_one(
            {"message_id": message_id},
            {
                "$push": {
                    "subs_received": data.get("push_notification_token")
                }
            }
        )
        logger.debug(f"result of update document: {result}")
        if result.matched_count > 0:
            return {
                "message": f"Successfully updated the document with message_id: {message_id}"
                }, status.HTTP_200_OK
        else:
            return {
                "message": f"No document found with the specified message_id: {message_id}"
                }, status.HTTP_404_NOT_FOUND

    def execute(self):
        request = self.context.get("request")
        data = request.data
        data, status_code = self.receive_notification(data)
        return data, status_code
