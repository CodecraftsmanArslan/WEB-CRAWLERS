from typing import List
from DBHelper import DBHelper
from SlackNotifyKYB import SlackNotifier
from LoggerKYB import Logger
from object_prepare import create_data_object
from requests import Session
import shortuuid
import json
from datetime import datetime
import socket
import inspect
from random import random
from math import floor,ceil

class CustomCrawler:
    RECORDS_BANK = []
    SERVER_IP = None
    is_requests = False
    is_selenium = False
    def __init__(self, meta_data: dict, config: dict, ENV: dict) -> bool:
        """
        Description: Initializes the CustomCrawler object with metadata, configuration, and environment variables.
        @param:
        - meta_data (dict): Dictionary containing crawler metadata.
        - config (dict): Dictionary containing crawler configuration.
        - ENV (dict): Dictionary containing environment variables.
        @Return:
        - bool: True if initialization is successful, False otherwise.
        """
        assert (
                    type(meta_data['SOURCE']) == str and
                    type(meta_data['SOURCE_TYPE']) == str and
                    type(meta_data['COUNTRY']) == str and
                    type(meta_data['CATEGORY']) == str and
                    type(meta_data['ENTITY_TYPE']) == str and
                    type(meta_data['SOURCE_DETAIL']) == dict and
                    type(meta_data['URL']) == str and
                    type(config['TRANSLATION_REQUIRED']) == bool and 
                    type(config['PROXY_REQUIRED']) == bool and 
                    type(config['PROXY_REQUIRED']) == bool
                )
        frame = inspect.currentframe().f_back
        module_path = inspect.getmodule(frame).__file__

        self.CRAWLER_CODE_NAME = module_path.replace('/','.')

        if self.CRAWLER_CODE_NAME.find('custom_crawlers.kyb') !=-1:
            self.CRAWLER_CODE_NAME = self.CRAWLER_CODE_NAME[self.CRAWLER_CODE_NAME.find('custom_crawlers.kyb'):]
        else:
            self.CRAWLER_CODE_NAME = 'custom_crawlers.kyb.'+self.CRAWLER_CODE_NAME

        self.SOURCE_TYPE = meta_data['SOURCE_TYPE']
        self.SOURCE = meta_data['SOURCE']
        self.COUNTRY = meta_data['COUNTRY']
        self.CATEGORY = meta_data['CATEGORY']
        self.ENTITY_TYPE = meta_data['ENTITY_TYPE']
        self.SOURCE_DETAIL = meta_data['SOURCE_DETAIL']
        self.URL = meta_data['URL']

        try:
            ENV['SERVER_IP'] = socket.gethostbyname(socket.gethostname())
        except:
            ENV['SERVER_IP'] = socket.gethostbyname('')
        self.SERVER_IP = ENV['SERVER_IP']
        self.TRANSLATION_REQUIRED = config['TRANSLATION_REQUIRED']
        self.crawler_name = config['CRAWLER_NAME']
        self.PROXY_REQUIRED = config['PROXY_REQUIRED']
        self.slack_notifier = SlackNotifier(config['CRAWLER_NAME'],ENV=ENV)
        self.db_helper = DBHelper(config['CRAWLER_NAME'],config['TRANSLATION_REQUIRED'],ENV=ENV,notify=self.slack_notifier)
        self.logger = Logger(config['CRAWLER_NAME'],ENV=ENV)
        self.ENVIRONMENT = ENV['ENVIRONMENT']
        if str(self.ENVIRONMENT).lower() != 'local':
            self.slack_notifier.crawler_start()

    def get_a_random_proxy(self,raw=False):
        """
        Description: Retrieves a random proxy server from the proxy list.
        @param:
        - raw (bool, optional): If True, returns the raw proxy string. If False (default), returns formatted proxy.
        @return:
        - str: Formatted proxy server string.
        """
        from proxies_list import PROXIES
        rand = floor(random() * len(PROXIES)) or ceil(random() * len(PROXIES))
        proxy = PROXIES[rand]
        if raw:
            return proxy
        else:
            host, port, username, password = proxy.split(':')
            proxy_server = f'{username}:{password}@{host}:{port}'
            return proxy_server
    def get_a_random_US_proxy(self,raw=False):
        """
        Description: Retrieves a random US proxy server from the US_PROXIES list.
        @param:
        - raw (bool, optional): If True, returns the raw proxy string. If False (default), returns formatted proxy.
        @return:
        - str: Formatted US proxy server string.
        """
        from proxies_list import US_PROXIES
        rand = floor(random() * len(US_PROXIES)) or ceil(random() * len(US_PROXIES))
        proxy = US_PROXIES[rand]
        if raw:
            return proxy
        else:
            host, port, username, password = proxy.split(':')
            proxy_server = f'{username}:{password}@{host}:{port}'
            return proxy_server
    
    def get_selenium_helper(self): 
        """
        Retrieves and sets up a Selenium helper object for the crawler.
        @return:
        - object: Selenium helper object.
        """
        import selenium_helper
        selenium_helper.setup_notify(self.slack_notifier)
        return selenium_helper

    def get_requests_helper(self):
        """
        Retrieves and sets up a Requests helper object for the crawler.
        @return:
        - object: Requests helper object.
        """
        import request_helper
        request_helper.setup_notify(self.slack_notifier)
        return request_helper
    
    def get_requests_session(self) -> Session:
        """
        Retrieves and sets up a Requests session object for the crawler.
        @return:
        - Session: Requests session object.
        """
        import request_helper
        request_helper.setup_notify(self.slack_notifier)
        return request_helper.create_requests_session()
    
    def generate_entity_id(self, reg_number:str=None, company_name:str=None) -> str:
        """
        Generates a unique entity ID based on registration number and company name.
        @param:
        - reg_number (str, optional): Registration number of the entity.
        - company_name (str, optional): Name of the company.
        @return:
        - str: Unique entity ID.
        """
        if reg_number and company_name:
           uuid = shortuuid.uuid(f'{reg_number}-{company_name}-{self.crawler_name}')
           return uuid
        elif reg_number and not company_name:
            uuid = shortuuid.uuid(f'{reg_number}-{self.crawler_name}')
            return uuid
        else:
            if company_name:
                uuid = shortuuid.uuid(f'{company_name}-{self.crawler_name}')
                return uuid
            else:
                print("couldn''t generate shortuuid")
                return None
        
    def prepare_data_object(self,obj) -> dict:
        """
        Prepares the data object for processing and insertion into the database.
        @param:
        - obj (dict): Data object to be prepared.
        @return:
        - dict: Prepared data object.
        """
        obj['country_name'] = self.COUNTRY
        prepared_obj = create_data_object(obj,self.crawler_name)
        return prepared_obj
    
    def replace_percentage(self, data:dict) -> dict:
        """
        Recursively tracks paths within the data dictionary and processes its values.
        @param:
        - data (dict): Data dictionary to be processed.
        @return:
        - dict: Processed data dictionary.
        """
        for each in data:
            if data[each] == "" or data[each] == " " or each == 'aliases' or data[each] == "N/A" or data[each] == None or each == "crawler_name" or each == "country_name":
                continue
            if isinstance(data[each], str):
                data[each] = data[each].replace("%","%%")
                
                if data[each].strip().replace(" ","") == "" or data[each].isnumeric():
                    continue
            if isinstance(data[each], dict):
                data[each] = self.replace_percentage(data[each])
            if isinstance(data[each], list):
                items = data[each]
                results = []
                for idx, item in enumerate(items):
                    item_ = self.replace_percentage(item)
                    results.append(item_)
                data[each] = results

        return data

    def prepare_row_for_db(self,ENTITY_ID:str,NAME:str,BIRTH_INCORPORATION_DATE:list,DATA:dict) -> list:
        """
        Prepares a row for insertion into the database.
        @param:
        - ENTITY_ID (str): Unique entity ID.
        - NAME (str): Name of the entity.
        - BIRTH_INCORPORATION_DATE (list): List containing birth or incorporation dates.
        - DATA (dict): Processed data dictionary.
        @return:
        - list: Prepared row for database insertion.
        """
        DATA = self.replace_percentage(DATA)
        
        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps([BIRTH_INCORPORATION_DATE]),
                json.dumps([self.CATEGORY]), json.dumps([self.COUNTRY]), self.ENTITY_TYPE, 
                json.dumps([]), json.dumps(DATA,ensure_ascii=False).replace("'", "''").encode('utf-8').decode(), self.SOURCE, json.dumps(self.SOURCE_DETAIL,ensure_ascii=False).replace("'", "''").encode('utf-8').decode(), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'en', True]
        return ROW
    
    def insert_record(self,record:list) -> bool:
        """
        Inserts a single record into the database.
        @param:
        - record (list): Record to be inserted into the database.
        @return:
        - bool: True if the insertion is successful, False otherwise.
        """
        return self.db_helper.insert_records(records=[record])

    def insert_many_records(self,records:List[list]) -> bool:
        """
        Inserts multiple records into the database.
        @param:
        - records (list): List of records to be inserted into the database.
        @return:
        - bool: True if the insertion is successful, False otherwise.
        """
        return self.db_helper.insert_records(records=records)
    
    def end_crawler(self):
        """
        Notifies the completion of the crawler and updates the SlackNotifier object.
        """
        self.slack_notifier.crawler_completed(self.db_helper.get_total_inserted_records())
    
    def db_log(self, data):
        """
        Logs data into the database and notifies Slack in case of errors.
        @param:
        - data (dict): Data to be logged.
        @return:
        - None
        """
        data['number_of_records'] = self.db_helper.get_total_inserted_records()
        if data['status'] in ('fail','faulty') and str(self.ENVIRONMENT).lower() != 'local':
                error_message = self.logger.get_error_message(type(data['error']).__name__) if data['status'] == 'fail' else 'No Error'
                self.slack_notifier.notify({
                    "event": data['status'],
                    "message": {
                        "source_type": data['source_type'],
                        "source_url": data['url'],
                        **({"error_message": (error_message)} if data['status'] == 'fail' else {}),
                        "num_records": str(data['number_of_records']),
                        "status": data['status'],
                        
                    }
                })
        return self.logger.log(data)

    def db_crawler_stats(self, data):
        """
        Description: Logs crawler statistics data into the database.
        @param:
        - data (dict): Dictionary containing crawler statistics data.
        @return:
        - None
        """
        return self.logger.crawler_stats_log(data)