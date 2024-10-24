from celery import shared_task
from firebase_admin import messaging

from loguru_conf import logger
from utils import create_data_by_topic


@shared_task(bind=True, max_retries=3, default_retry_delay=600)
def send_notification_by_topic(self, topic: str, data: dict):
    logger.debug(f"Topic: {topic} Data: {data}")
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=data['title'],
                body=data['body'],
            ),
            topic=topic,
        )

        # response = messaging.send(message)
        response = 12312312312312312331
        create_data_by_topic(data, str(response), topic)
        logger.info(f"Successfully sent message to topic {topic}: {response}")
    except Exception as exc:
        logger.error(f"Error sending notification to topic {topic}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=600)
def send_notification_by_topic_last(self, message: messaging.Message) -> None:
    logger.debug(f"Topic: {message.topic} Data: {message.notification.title} {message.notification.body}")
    try:
        response = messaging.send(message)
        logger.info(f"Successfully sent message to topic {message.notification.title}: {response}")
    except Exception as exc:
        logger.error(f"Error sending notification to topic {message.topic}: {exc}")
        raise self.retry(exc=exc)
