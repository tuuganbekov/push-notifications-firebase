from pymongo import MongoClient
from django.conf import settings


def get_mongo_client():
    client = MongoClient(
        f'mongodb://{settings.MONGO_HOST}:{settings.MONGO_PORT}/'
    )
    client = client[settings.MONGO_NAME]
    return client
