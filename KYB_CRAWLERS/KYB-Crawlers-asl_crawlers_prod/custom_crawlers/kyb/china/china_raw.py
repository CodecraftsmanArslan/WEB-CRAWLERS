"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

"""Import required libraries"""
import urllib.parse
import shortuuid
import json
import pandas as pd
import datetime
from helpers.logger import Logger
import os
import traceback
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from helpers.crawlers_helper_func import CrawlersFunctions


load_dotenv()
'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()

'''Global Variables'''
DATA_SIZE = 0


def get_records(source_type, entity_type, country, category, url, name, description):
    '''
        Description: This function is used to read complete HTML page content, and dump it into reports_raw table in raw form.
        @param source_type: string
        @param entity_type: string
        @param country: List[string]
        @param category: List[string]
        @param url: string
        @param metadata: Dict
        @param name: string
        @param description: string
        @return num_records:1
        @return status:string
    '''
    try:
        page = crawlers_functions.get_response(url)
        file_name = f'{os.path.dirname(os.getcwd())}/crawlers_metadata/downloads/html/{shortuuid.uuid(url)}.html'
        with open(file_name, 'wb') as file:
            file.write(page.content)
        data_size = len(page.content)
        content_type = page.headers['Content-Type'] if 'Content-Type' in page.headers else 'N/A'
        status_code = page.status_code
        if status_code != 200:
            raise ConnectionError('unable to connect')
        soup = BeautifulSoup(page.content, 'html.parser',
                             from_encoding="utf-8")
        body = soup.find('body')
        insertion_data = [
            json.dumps(body.text.replace("'", "''").replace(
                '"', '""').replace('\n', '').replace('(', '').replace(')', '') if body else str(page.content).replace("'", "''").replace(
                '"', '""').replace('\n', '').replace('(', '').replace(')', '')),
            json.dumps(
                {"Source URL": url.replace(
                '"', '""'), "Source Description": description.replace("'","''"), "Name": name}),
            json.dumps([country.title()]),
            json.dumps([] if category == '[]' else [category.title()]),
            entity_type.title(),
            name + '-' + source_type,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            url.replace("'", "''")
        ]
        query = """INSERT INTO reports_raw (raw_data, source_details, countries, categories, entity_type, source, created_at, updated_at, source_url) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}') ON CONFLICT (source_url) DO UPDATE SET updated_at='{7}';""".format(*insertion_data)
        if insertion_data[0] != "":
            crawlers_functions.db_connection(query)
            return 1, "success", [], '', data_size, content_type, status_code, file_name, ''
        else:
            return 0, "empty", [], '', data_size, content_type, status_code, file_name, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, 0, 'N/A', "", '' ,str(tb).replace("'","''")


'''
Description: HTML Raw Data Crawler trigger
'''

if __name__ == '__main__':
    '''
    Description: HTML Crawler for China
    '''
    name = 'National Enterprise Bankruptcy Information Disclosure Platform'
    description = "The National Enterprise Bankruptcy Information Disclosure Platform is a government-run platform in China that provides information about bankruptcies of Chinese enterprises. The platform is maintained by the State Administration for Market Regulation and is designed to promote transparency and accountability in bankruptcy proceedings."
    entity_type = 'Company/Organization'
    source_type = 'RAW_HTML'
    countries = 'China'
    category = 'Bankruptcy'
    urls_list = pd.read_csv('.//kyb/china/inputs/china_raw_urls.csv')
    for url in urls_list.iterrows():
        url = url[1][0]
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url, name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
        logger.log()