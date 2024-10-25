import requests
import firebase_admin
from django.db import transaction
from google.auth.transport.requests import Request
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response
from firebase_admin import credentials, messaging

from django.conf import settings
from loguru_conf import logger
from notifications.models import UserDevice, Notification, UserNotification
from notifications import serializers


# SERVICE_ACCOUNT_FILE = settings.BASE_DIR / 'serviceAccount.json'

# SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
# creds_json = json.dumps(settings.CREDS_FIREBASE, indent=4)
# credentials = service_account.Credentials.from_service_account_info(
#     json.loads(creds_json), scopes=SCOPES
# )
# cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
# firebase_admin.initialize_app(cred)


def get_access_token():
    credentials.refresh(Request())
    return credentials.token


def send_notification(data):
    try:
        message_title = data.get("title", "Обновление")
        message_description = data.get("description", "Обновите приложение Mega24")
        device_id = data.get("device_id")
        user_device = UserDevice.objects.get(device_id=device_id)
        access_token = get_access_token()

        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json; UTF-8',
        }

        message = {
            'message': {
                'token': user_device.push_notification_token,
                'notification': {
                    'title': message_title,
                    'body': message_description,
                }
            }
        }
        logger.debug(f"send message dict: {message}")

        response = requests.post(
            settings.RESPONSE_URL,
            headers=headers,
            json=message,
            verify=False
        )
        logger.debug(f"firebase response: {response.status_code}")
        logger.debug(f"firebase response body0 (text): {response.text}")
        logger.debug(f"firebase response body (json): {response.json()}")

        if response.status_code == 200:
            return {"success": True, "result": response.json()}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}
    

def send_notif(data):
    user_device = UserDevice.objects.get(device_id=data.get("device_id")).push_notification_token
    logger.debug(f"data: {data}")
    logger.debug(f"token: {user_device}")
    message = messaging.Message(
        notification=messaging.Notification(
            title=data.get("title"),
            body=data.get("body"),
        ),
        token=user_device,
    )

    # Send the message
    try:
        response = messaging.send(message)
        logger.debug(f'Successfully sent message: {response}')
        logger.debug(f'Successfully sent message (type): {type(response)}')
        logger.debug(f'Successfully sent message (dir): {dir(response)}')
        return {"sent": True}
    except firebase_admin.exceptions.FirebaseError as e:
        logger.debug(f'Error sending message: {str(e)}')
        return {"sent": False}
    

def send_notif_all(data, topic):
    user_devices = UserDevice.objects.filter(
        allow_notifications=True
    ).values_list('push_notifications')
    logger.debug(f"data: {data}")
    logger.debug(f"token: {user_devices}")
    message = messaging.Message(
        notification=messaging.Notification(
            title=data.get("title"),
            body=data.get("body"),
        ),
        topic=topic,
    )

    # Send the message
    try:
        response = messaging.send(message)
        logger.debug(f'Successfully sent message: {response}')
        logger.debug(f'Successfully sent message (type): {type(response)}')
        logger.debug(f'Successfully sent message (dir): {dir(response)}')
        return {"sent": True}
    except firebase_admin.exceptions.FirebaseError as e:
        logger.debug(f'Error sending message: {str(e)}')
        return {"sent": False}

class NotificationService:
    model = Notification

    def get_serializer(self, data, instance=None):
        if instance:
            return serializers.NotificationSerializer(instance, data=data)
        return serializers.NotificationSerializer(data=data)

    @transaction.atomic
    def _save_data(self, serializer: ModelSerializer):
        if serializer.is_valid():
            instance = serializer.save()
            return instance
        else:
            raise ValueError("Invalid data")

    def get_or_create_device_id(self, data):
        device_id = data.get("device_id")
        if device_id:
            user_device = UserDevice.objects.get_or_create(data)
            return user_device.id
        return None

    def execute(self, data, instance=None):
        device_id = self.get_or_create_device_id(data)
        if device_id:
            data['device_id'] = device_id

        serializer = self.get_serializer(data=data, instance=instance)
        instance = self._save_data(serializer)
        return instance


class UserDeviceService:
    model = UserDevice

    def get_serializer(self, data, instance=None):
        if instance:
            return serializers.UserDeviceSerializer(instance, data=data)
        return serializers.UserDeviceSerializer(data=data)

    @transaction.atomic
    def _save_data(self, serializer: ModelSerializer):
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            return instance
        else:
            raise ValueError("Invalid data")

    def get_or_create_device(self, data):
        device_id = data.get('device_id')
        if not device_id:
            raise ValueError("Device ID is required")
        try:
            instance = UserDevice.objects.get(device_id=device_id)
            created = False
        except UserDevice.DoesNotExist:
            instance = None
            created = True

        return instance, created

    def update_device(self, instance, data):
        serializer = self.get_serializer(data=data, instance=instance)
        if serializer.is_valid(raise_exception=True):
            instance = self._save_data(serializer)
            return instance
        else:
            raise ValueError("Invalid data")

    def create_device(self, data):
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance = self._save_data(serializer)
            return instance
        else:
            raise ValueError("Invalid data")

    def execute(self, data):
        instance, created = self.get_or_create_device(data)
        if created:
            return self.create_device(data)

        return self.update_device(instance, data)


class UserNotificationService:
    model = UserNotification

    def get_serializer(self, data, instance=None):
        if instance:
            return serializers.UserNotificationSerializer(instance, data=data)
        return serializers.UserNotificationSerializer(data=data)

    @transaction.atomic
    def _save_data(self, serializer: ModelSerializer):
        if serializer.is_valid():
            instance = serializer.save()
            return instance
        else:
            raise ValueError("Invalid data")

    def execute(self, data, instance=None):
        serializer = self.get_serializer(data=data, instance=instance)
        instance = self._save_data(serializer)
        return instance
