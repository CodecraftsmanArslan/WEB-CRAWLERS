# Import necessary libraries
from datetime import datetime
import sys
import traceback
import re
import os
import asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from CustomCrawler import CustomCrawler
from load_env.load_env import ENV

# Define metadata
meta_data = {
    'SOURCE': 'Corporate Registry of Prince Edward Island, Canada',
    'COUNTRY': 'Prince Edward Island',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {
        "Source URL": "https://www.princeedwardisland.ca/en/feature/pei-business-corporate-registry#/service/BusinessAPI/BusinessSearch",
        "Source Description": "Corporate Services is responsible for the registration of corporations and business names in PEI. Businesses of all types can reserve names, register, and manage their registry account information."
    },
    'URL': 'https://www.princeedwardisland.ca/en/feature/pei-business-corporate-registry#/service/BusinessAPI/BusinessSearch',
    'SOURCE_TYPE': 'HTML'
}

# Define crawler configuration
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Prince Edward Island Original Registry'
}

# Initialize a set to store missing numbers
missing_numbers = set()
custom_path = os.path.dirname(os.getcwd())+ "/prince_edward_island"
# Initialize variables
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

# Create a CustomCrawler object
prince_edward_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = prince_edward_crawler.get_requests_helper()
arguments = sys.argv
business_number = int(arguments[1]) if len(arguments) > 1 else 0000
end_business_number = 999999

try:

    # Loop through business numbers
    for number in range(business_number, end_business_number):
        print("Business Number=", number)

        corporate_url = 'https://wdf.princeedwardisland.ca/api/workflow'
        payload = {"appName": "LegacyBusiness", "featureName": "LegacyBusiness",
                   "metaVars": {"service_id": 'null', "save_location": 'null'},
                   "queryVars": {"service": "LegacyBusiness", "activity": "LegacyBusinessView",
                                 "business_number": f"{number}", "business_type": "9"},
                   "queryName": "LegacyBusinessView"}
        headers={"Content-Type": "application/json"}
        loop = asyncio.get_event_loop()
        headers = {"Content-Type": "application/json"}
        registry_original_response = request_helper.make_request(corporate_url, method="POST",json=payload)
        STATUS_CODE = registry_original_response.status_code
        DATA_SIZE = len(registry_original_response.content)
        CONTENT_TYPE = registry_original_response.headers['Content-Type'] if 'Content-Type' in registry_original_response.headers else 'N/A'

        # Check for 500 status code and handle accordingly
        if registry_original_response.status_code == 500:
            print("No data found -", number)
            with open(f"{custom_path}/failed_record.txt", "a") as file:
                file.write(str(number) + ",\n")
            continue
        # Extract and process original data
        original_data = registry_original_response.json()

        # Extract and process people details
        try:
            people_detail = []
            pattern = r"([A-Za-z]+ [A-Za-z]+) - ([A-Za-z, ]+)"
            Officers = re.findall(pattern, original_data['data']['data']['keyValuePairs']['Officer(s)'])
            for officer in Officers:
                offices = {"name": officer[0], "designation": officer[1]}
                people_detail.append(offices)

            # Extract names and designations
            Director_pattern = r"([A-Za-z]+ [A-Za-z]+)\n"
            names = re.findall(Director_pattern, original_data['data']['data']['keyValuePairs']['Director(s)'])
            designations = ["director"] * len(names)
            for name, designation in zip(names, designations):
                people_detail.append({"name": name, "designation": designation})

            # Extract names of shareholders
            Shareholders_name = re.findall(Director_pattern, original_data['data']['data']['keyValuePairs']['Shareholder(s)'])
            shareholders_designations = ["shareholders"] * len(Shareholders_name)
            for Shareholders_name, shareholders_designations in zip(Shareholders_name, shareholders_designations):
                people_detail.append({"name": Shareholders_name, "designation": shareholders_designations})

        except:
            people_detail = []

        # Extract chief agent data
        if original_data['data']['data']['keyValuePairs'].get('Chief Agent', "") != "":
            agent = {
                "name": original_data['data']['data']['keyValuePairs'].get('Chief Agent', "").split("\n")[0].strip(),
                "address": "".join(original_data['data']['data']['keyValuePairs'].get('Chief Agent', "").split("\n")[1:]).replace("\n", " ").strip(),
                "designation": "cheif_agent"
            }
            people_detail.append(agent)

        # Create an object for the data
        OBJ = {
            "name": original_data['data']['data']['keyValuePairs'].get('Entity Name', ""),
            "registration_number": original_data['data']['data']['keyValuePairs'].get('Registration Number', ""),
            "type": original_data['data']['data']['keyValuePairs'].get('Business Type', ""),
            "registration_date": original_data['data']['data']['keyValuePairs'].get('Registration Date', ""),
            "status": original_data['data']['data']['keyValuePairs'].get('Status', ""),
            "object_type": "original_registry",
            "end_date": original_data['data']['data']['keyValuePairs'].get('Expiry Date', ""),
            "jurisdiction": original_data['data']['data']['keyValuePairs'].get('Jurisdiction of Incorporation', ""),
            "amalgamated_name": original_data['data']['data']['keyValuePairs'].get('Amalgamated Name', ""),
            "industries": original_data['data']['data']['keyValuePairs'].get('Business In', "").replace("n/a", ""),
            "category": original_data['data']['data']['keyValuePairs'].get("Business Out", "").replace("n/a", ""),
            "last_return_date": original_data['data']['data']['keyValuePairs'].get("Last Return Date", ""),
            "addresses_detail": [
                {
                    "type": "general_address",
                    "address": original_data['data']['data']['keyValuePairs'].get("Address", "").replace("\n", " ")
                }
            ],
            "people_detail": people_detail
        }
        # Prepare the data object
        OBJ = prince_edward_crawler.prepare_data_object(OBJ)
        param = OBJ.get("name", "") + OBJ.get("object_type", "")
        ENTITY_ID = prince_edward_crawler.generate_entity_id(OBJ['registration_number'], param)
        NAME = OBJ['name'].replace("%", "%%")
        BIRTH_INCORPORATION_DATE = OBJ.get("incorporation_date", "")
        ROW = prince_edward_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)

        # Insert the record
        prince_edward_crawler.insert_record(ROW)

    # End the crawler
    prince_edward_crawler.end_crawler()

    # Log crawler data
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "", "crawler": "HTML","ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    prince_edward_crawler.db_log(log_data)

except Exception as e:
    # Handle exceptions
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"), "crawler": "HTML"}

    # Log error data
    prince_edward_crawler.db_log(log_data)

