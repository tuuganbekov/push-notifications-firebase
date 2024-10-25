import pytz
from datetime import datetime
from django.conf import settings
from firebase_admin import messaging

from loguru_conf import logger
from notifications.models import UserDevice
from config.mongo import get_mongo_client


def batch_subscribe_to_topic(device_tokens, topic, batch_size=1000):
    for i in range(0, len(device_tokens), batch_size):
        batch = device_tokens[i:i+batch_size]
        response = messaging.subscribe_to_topic(batch, topic)
        logger.debug(f'Successfully subscribed {response.success_count} device(s) to topic "{topic}".')
        if response.failure_count > 0:
            for error in response.errors:
                logger.debug(f'Error subscribing to topic: {error.reason}')


def subscribe_all(environment: str, topic="all") -> None:
    all_users = UserDevice.objects.all()
    if environment != "test":
        prefix = "prod_"
    else:
        prefix = ""
    for user in all_users:
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


def create_data_by_topic(
        data: dict,
        response_id: str,
        topic: str = None,
) -> None:
    """
    Create document in mongodb
    Goal: monitor sent notifications and get statistics
    """
    client = get_mongo_client()
    collection = client["notifications"]
    by_topic = True if topic else False
    doc = {
        "response": response_id,
        "notification_id": data["notification_id"],
        "title": data["title"],
        "push_body": data["body"],
        "sent_subs": [],
        "subs_received": [],
        "by_topic": by_topic,
        "topic_name": topic,
        "date": datetime.now(pytz.timezone(settings.TIME_ZONE))
    }
    logger.debug(f"Mongo doc: {doc}")
    res = collection.insert_one(doc)
    logger.debug(f"save to mongo: {res}")


def get_env(request):
    host = request.get_host()
    if "test" in host or "localhost" in host or "127.0.0.1" in host:
        env = ""
    else:
        env = "prod_"
    return env
