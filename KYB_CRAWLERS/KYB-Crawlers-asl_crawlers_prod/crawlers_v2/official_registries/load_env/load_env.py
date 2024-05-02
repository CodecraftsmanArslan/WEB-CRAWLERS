import os
from dotenv import load_dotenv
load_dotenv()
ENV = {
    'HOST': os.getenv('SEARCH_DB_HOST'),
    'PORT': os.getenv('SEARCH_DB_PORT'),
    'USER': os.getenv('SEARCH_DB_USERNAME'),
    'PASSWORD': os.getenv('SEARCH_DB_PASSWORD'),
    'DATABASE': os.getenv('SEARCH_DB_NAME'),
    'ENVIRONMENT': os.getenv('ENVIRONMENT'),
    'SLACK_CHANNEL_NAME': os.getenv("KYB_SLACK_CHANNEL_NAME"),
    'WARNINGS_CHANNEL_NAME': os.getenv("KYB_WARNINGS_CHANNEL_NAME"),
    'PLATFORM': os.getenv('PLATFORM'),
    'SERVER_IP': os.getenv('SERVER_IP'),
    'SLACK_WEB_HOOK': os.getenv('KYB_SLACK_WEB_HOOK'),
    'WARNINGS_WEB_HOOK': os.getenv('KYB_WARNINGS_WEB_HOOK')
}
