from django.conf import settings
from pymongo import MongoClient

client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
database = client[settings.MONGO_DB_NAME]
movies = database['movies']


def check_database():
    client.admin.command('ping')


def ensure_indexes():
    movies.create_index([('created_at', -1)], name='created_at_desc')
