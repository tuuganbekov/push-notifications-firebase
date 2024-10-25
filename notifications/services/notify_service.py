import requests
import firebase_admin
from django.db.models import QuerySet
from django.utils import translation
from firebase_admin import messaging
from rest_framework import status
from pymongo.synchronous.collection import Collection

from config.mongo import get_mongo_client
from generics.services import BaseService
from loguru_conf import logger
from notifications.models import UserDevice, Notification
from notifications.serializers import NotificationSerializer
from system_msg import (
    REQUIRED_FIELD,
    USER_NOT_FOUND,
    NOTIFACTIONS_DISALLOWED,
)
from utils import get_env

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


class NotificationsListService(BaseService):
    def get_notification_ids(
            self,
            subs_id: str,
            user: UserDevice,
            collection: Collection,
            env: str
    ) -> list:
        """
        Get notification ids from mongo db by subs_id
        """
        bill_group = f"{env}bill_corp" if user.bill_group == 1 else f"{env}bill_individ"
        logger.debug(f"bill group: {bill_group}")
        query = {
            "$or": [
                {"$and": [{"by_topic": True}, {"topic_name": f"{env}all"}]},
                {"$and": [{"by_topic": True}, {"topic_name": bill_group}]},
                {"$and": [{"by_topic": False}, {"sent_subs": {"$in": [subs_id]}}]}
            ]
        }
        docs = collection.find(
            query, {"_id": 0, "notification_id": 1, "subs_received": 1}
        )
        notifications = list(docs)
        logger.debug(f"list of docs: {notifications}")
        return notifications

    def check_if_received(self, subs_id: str, data: list[dict]) -> dict:
        result = {}
        for doc in data:
            if subs_id in doc["subs_received"]:
                result[str(doc["notification_id"])] = True
            else:
                result[str(doc["notification_id"])] = False
        logger.debug(f"check if received: {result}")
        return result

    def filter_notifications(self, data: dict) -> QuerySet:
        data = data.keys()
        notifications = Notification.objects.filter(id__in=data)
        logger.debug(f"notifications: {notifications}")
        return notifications

    def prepare_json(self, data: QuerySet, docs: dict) -> list:
        serializer = NotificationSerializer(data, many=True)
        data = serializer.data
        result = [
            {**notification, 'subs_received': docs[str(notification["id"])]}
            for notification in data
        ]
        logger.debug(f"result: {result}")
        return result

    def execute(self) -> tuple[list, int]:
        client = get_mongo_client()
        request = self.context.get("request")
        env = get_env(request)
        subs_id = request.query_params.get("subs_id")
        user = UserDevice.objects.get(subs_id=subs_id)
        notification_col = client["notifications"]
        logger.debug(f"type of notif collec: {type(notification_col)}")
        data = self.get_notification_ids(subs_id, user, notification_col, env)
        docs = self.check_if_received(subs_id, data)
        notifications = self.filter_notifications(docs)
        res_data = self.prepare_json(notifications, docs)
        return res_data, status.HTTP_200_OK
