"""Import required libraries"""

import warnings
import datetime
import os
import requests
import shortuuid
import copy
import json
import pandas as pd
from langdetect import detect
import country_converter as coco
from helpers.db_connection import PostgresConnection
from collections import defaultdict
from googletrans import Translator
import time
from requests.exceptions import RequestException
from dotenv import load_dotenv
converter = coco.CountryConverter()
translator = Translator()
warnings.filterwarnings('ignore')
load_dotenv()

class CrawlersFunctions:


    def language_handler(self, record, table):
        '''Description: This method checks if name in record is in english, and dumps a new record into database if name is not in english
        @param self
        @param record
        '''
        record = copy.deepcopy(record)
        english_check = True
        for letter in record[1]:
            if ord(letter) <= 127:
                pass
            else:
                english_check = False
                break
        if not english_check:
            try:
                parent_id = record[0]
                language = 'en'
                record[1] = translator.translate(record[1]).text
                record[0] = record[0].split(
                    '-')[0] + '-t-' + record[0].split('-')[1]
                query = f"INSERT INTO {table} (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,parent_id) VALUES ('{record[0]}','{record[1]}','{record[2]}','{record[3]}','{record[4]}','{record[5]}','{record[6]}','{record[7]}','{record[8]}','{record[9]}','{record[10]}','{record[11]}','{language}','{parent_id}')"
                self.db_connection(query)
            except:
                pass
        else:
            return

    def db_connection(self, query):
        '''Description: This method is used to execute the any queries
        @param self
        @param query
        '''
        db = PostgresConnection()
        conn = db.get_connection('SEARCH')
        cursor = conn.cursor()
        cursor = cursor.execute(query)
        conn.commit()

    def get_fatf(self):
        '''Description: This method is used to get records from database
        @param self
        @return dataframe that contains country code and description
        '''
        db = PostgresConnection()
        conn = db.get_connection('SEARCH')
        # Get the fatf from the database
        cursor = conn.cursor()
        query = "SELECT country_name, descriptions FROM fatf_profiles"
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['country_name', 'descriptions'])
        return df

    def create_listed_object(self, record, countries):
        '''Description: This method is used prepare an object records with array values
        1) Using records to get items
        2) Apply a array method on values to get array
        3) Get FATF countries profiles descriptions from database and store them.
        @param records
        @param countries
        @return data
        '''
        input_ = record
        data = defaultdict(list)
        for key, value in input_.items():
            if value != '':
                if type(value) == str:
                    value = json.loads(value, strict=False)
                list_of_updated_record = [(rec[0], [rec[1]])
                                          for rec in value.items()]
                data[key] = dict(list_of_updated_record)

        fatf_file_df = self.get_fatf()

        fatf_descriptions = []
        for country in countries:
            for index, row in fatf_file_df.iterrows():
                if row['country_name'] == country:
                    fatf_descriptions.append(row['descriptions'])
        data['AML FATF Profile'] = fatf_descriptions
        return data

    def transform_urdu_data(self, data, type_, url_, description_,p_name_):
        '''Description: This method transform the Urdu data
        1) prepare data format as per requirements
        2) Store in database
        @param data
        @param type_
        @param url_
        @param description_
        @return data:str
        '''
        raw_data = json.dumps(data[1].replace('[', ',').replace(
            ']', '') + ' ' + data[2].replace('[', ',').replace(']', '').replace("'", "")).replace("'", "''")
        source_details = json.dumps(
            {"Source URL": url_, "Source Description": description_, "Name": p_name_})
        countries = data[4]
        categories = data[3]
        entity_type = data[5]
        source = type_
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        source_url = url_
        return [raw_data, source_details, countries, categories, entity_type, source, created_at, updated_at, source_url]

    def check_language(self, data, type_, url_, description_, p_name_):
        '''Description: This method is used for detecting languages English/Urdu
        1) Check which type of language is in the data
        2) If language contain 'en' return English otherwise return Urdu
        @param data
        @param type_
        @param description_
        @param url_
        @return data
        '''
        name = data[1].lower()
        check = True
        for character in name:
            if 1791 >= ord(character) >= 1536:
                check = False
                break
        if check:
            return data, 'en'
        else:
            data = self.transform_urdu_data(data, type_, url_, description_,p_name_)
            return data, 'ur'

    def clean_country(self, country):
        '''
        Description: This method is used to clean name of countries and convert short code to full country names
        @param country:str
        @return country name
        '''
        country = country.split("['")[1].split("']")[0].replace('"', '')
        country_name = ''
        try:
            country_name = converter.convert(
                names=country, src='ISO2', to='name')
        except:
            country_name = ''
        return country_name

    def prepare_data(self, record, counter_, type_, url_name, entity_type_, countries_, category_, description_, p_name_):
        '''
        Description: This method is prepare data the whole data and append into an array
        1) If any records does not exist it store empty array
        2) prepare data complete and cleaned array then pass to get_records method that insert records into database
        @param record
        @param counter_
        @param type_
        @param url_name
        @param entity_type_
        @param countries_
        @param category_
        @param description_
        @param p_name_
        @return array
        '''
        arr = []
        arr.append(shortuuid.uuid(record['Summary']['Name']+url_name))
        try:
            arr.append(record['Summary']['Name'].title().replace("'", "''"))
        except:
            pass
        try:
            arr.append(json.dumps([])) if record['Summary']['Date of Birth/Incorporation'] == "" else arr.append(
                json.dumps([record['Summary']['Date of Birth/Incorporation']]))
        except KeyError:
            try:
                arr.append(json.dumps([])) if record['Summary']['Date of Birth'] == "" else arr.append(
                    json.dumps([record['Summary']['Date of Birth']]))
            except:
                arr.append(json.dumps([]))

        if category_ =='[]':
            arr.append(category_)
        else:
            arr.append(json.dumps([category_.upper()]))
        arr.append(json.dumps([country_.upper() for country_ in countries_]))
        arr.append(entity_type_.upper())
        arr.append(json.dumps([]))
        arr.append(json.dumps(self.create_listed_object(record, countries_)))
        source_details = {"Source URL": url_name,
                          "Source Description": description_, "Name": p_name_}
        arr.append(json.dumps(source_details))
        arr.append(p_name_ + "-" + type_)
        arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        try:
            arr.append(detect(arr[1]))
        except:
            arr.append('en')
        return arr

    def get_response(self, url_):
        '''Description: This method returns the response of url using different parameters
        @param url
        @return response
        '''
        try:
            response = requests.get(url_, stream=True, headers={
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}, timeout=300)
            
            if response.status_code == 200:
                return response 
            else:
                raise Exception('StatusCodeError')
        except:
            for i in range(int(os.getenv('NO_OF_PROXIES'))):
                    http_proxy = os.getenv('HTTP_PROXY_' + str(i+1))
                    https_proxy = os.getenv('HTTPS_PROXY_'+str(i+1))
                    response = requests.get(url_,stream=True,headers={
                        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'},
                        proxies={
                        'http': http_proxy,
                        'https': https_proxy
                    },
                    verify=os.getenv('VERIFY'), timeout=300)
                    
                    if response.status_code == 200:
                        update_query = """UPDATE sources SET is_proxy = true, updated_at = '{1}' WHERE url = '{0}'""".format(url_,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        self.db_connection(update_query)
            return response

