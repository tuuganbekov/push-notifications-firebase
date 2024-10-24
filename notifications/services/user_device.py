import requests
from firebase_admin import messaging
from rest_framework import serializers, status

from generics.services import BaseService
from loguru_conf import logger
from notifications.models import UserDevice, Topic

session = requests.Session()
session.trust_env = False


class UserDeviceService(BaseService):
    def subscribe_to_topic(self, user: UserDevice, host: str) -> None:
        '''
            Structures of topics:
             - все: all,
             - тариф: rtpl_372,
             - билл гр: bill_corp or bill_individ
        '''
        topics = [
            "all",
            # f"rtpl_{user.rtpl_id}",
            "bill_corp" if user.bill_group == 1 else "bill_individ",
        ]
        
        if "test" not in host:
            prefix = "prod_"
        else:
            prefix = ""
        for topic in topics:
            logger.debug(f"topic in topics: {prefix}{topic}")
            response = messaging.subscribe_to_topic(
                user.push_notification_token, f"{prefix}{topic}"
            )
            if response.success_count == 1:
                logger.debug(
                    f"Successfully subscribed to topic '{prefix}{topic}': {user.subs_id} - {user.device_id}"
                )
            else:
                logger.debug(
                    f"Errors while subscribing to a topic '{prefix}{topic}': {response.errors}"
                )
        

    def execute(self, serializer: serializers.BaseSerializer) -> tuple:
        request = self.context.get("request")
        host = request.get_host()
        logger.debug(f"host in exec: {host}")
        validated_data = serializer.validated_data
        logger.debug(f"validated data: {validated_data}")
        try:
            instance = UserDevice.objects.get(
                device_id=validated_data.get("device_id")
            )
            instance = UserDevice.objects.update_by_device_id(instance, validated_data)
            logger.debug(f"updated: {instance}")
            self.subscribe_to_topic(instance, host)
            return {"message": "Updated successfully"}, status.HTTP_200_OK
        except UserDevice.DoesNotExist:
            instance = UserDevice.objects.create(**serializer.validated_data)
            self.subscribe_to_topic(instance, host)
            return {"message": "Created successfully"}, status.HTTP_200_OK
