"""Set System Path"""
import sys
from pathlib import Path
from CustomCrawler import CustomCrawler
import json
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

ENV =  {
            'HOST': os.getenv('SEARCH_DB_HOST'),
            'PORT': os.getenv('SEARCH_DB_PORT'),
            'USER': os.getenv('SEARCH_DB_USERNAME'),
            'PASSWORD': os.getenv('SEARCH_DB_PASSWORD'),
            'DATABASE': os.getenv('SEARCH_DB_NAME'),
            'ENVIRONMENT': os.getenv('ENVIRONMENT'),
            'SLACK_CHANNEL_NAME': os.getenv("KYB_SLACK_CHANNEL_NAME"),
            'WARNINGS_CHANNEL_NAME': os.getenv("KYB_WARNINGS_CHANNEL_NAME"),
            'PLATFORM':os.getenv('PLATFORM'),
            'SERVER_IP': os.getenv('SERVER_IP'),
            'SLACK_WEB_HOOK': os.getenv('KYB_SLACK_WEB_HOOK'),
            'WARNINGS_WEB_HOOK': os.getenv('KYB_WARNINGS_WEB_HOOK')            
        }

meta_data = {
    'SOURCE' :'Infogreffe',
    'COUNTRY' : 'France',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.infogreffe.fr/recherche-entreprise-dirigeant/recherche-avancee", 
                        "Source Description": "Infogreffe is an online platform and service provided by the French commercial courts that offers access to business and legal information about registered companies in France. It serves as a central database and information resource for individuals, businesses, and professionals seeking information on French companies."},
    'SOURCE_TYPE': 'HTML',
    'URL' : ''
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "France Official Registry"
}
ZIP_CODES = [123,12312,42]
france_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
sel_helper =  france_crawler.get_selenium_helper()
proxy = france_crawler.get_a_random_proxy()
print(proxy)
driver = sel_helper.create_seleniumwire_driver(headless=False,proxy=True, proxy_server=proxy)
driver.get('https://www.wdfi.org/apps/corpsearch/Results.aspx?type=Simple&q=a')
from time import sleep

sleep(400)