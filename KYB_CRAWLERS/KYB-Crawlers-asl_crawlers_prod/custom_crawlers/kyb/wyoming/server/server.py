import cv2
import numpy as np
import zipfile
import subprocess
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os
import psycopg2
import shortuuid
import json
from datetime import datetime

load_dotenv()


conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()


def insert_data(data):
    i = 0
    for row in data:
        i += 1
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,
                image,data,source,source_details,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}',
                '{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) 
                    DO UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', 
                    image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb WHEN NOT '{6}'::jsonb <@ reports.image 
                    THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}',is_format_updated='{13}'
                """.format(*row)
        cursor.execute(query)
        conn.commit()
        print('INSERTED RECORD ', i)

def img2txt(img_path):
    img = cv2.imread(img_path)
    _, binary_image = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    eroded_image = cv2.erode(binary_image, kernel, iterations=1)
    dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)
    img2 = cv2.subtract(dilated_image,img)
    cv2.imwrite('processed.png',img2)
    command = ['tesseract', 'processed.png', 'stdout', '--psm', '8', '-c', 'tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', '--dpi', '70']
    captcha_text = subprocess.check_output(command).decode().replace(" ", "").rstrip()
    return captcha_text


# base64_data = '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'
# image_data = base64.b64decode(base64_data)

from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_string():
    data = request.get_json()
    if not data or 'img' not in data:
        return jsonify({'error': 'Invalid request. Please provide a "img" parameter.'}), 400
    
    input_string = data['img']
    base64_img = input_string.split(',')[1]
    image_data = base64.b64decode(base64_img)
    image = Image.open(BytesIO(image_data))
    image.save('captcha.png')
    captcha_text = img2txt('captcha.png')
    return jsonify({'result': captcha_text})



# Constants
SOURCE = "Wyoming Secretary of State''s Office"
COUNTRY = ['Wyoming']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://wyobiz.wyo.gov/Business/FilingSearch.aspx", 
                 "Source Description": "This website provides business filing search page that allows users to search for business filings and access information on registered businesses in Wyoming. Users can search using various parameters, including business name, registered agent name, and file number."}
IMAGES = []

@app.route('/insert', methods=['POST'])
def insert_into_db():
    data = request.get_json()
    NAME = data['name']
    print(f'processing {NAME}')
    BIRTH_INCORPORATION_DATE = [data["initial_date"].replace('/','-')]
    ENTITY_ID = shortuuid.uuid(f"{data['id']}-wyoming_kyb_crawler")
    
    DATA = {
            "name": data['name'],
            "status": data['status'],
            "registration_number": data["id"],
            "registration_date": data['initial_date'].replace('/','-'),
            **({"dissolution_date": data["inactive_date"].replace('/','-')} if data["inactive_date"] else {}),
            "type": data["filing_type"],
            "crawler_name": "custom_crawlers.kyb.wyomnig_kyb",
            "country_name": COUNTRY[0],
            "company_fetched_data_status": "",
            "jurisdiction": data["formation"],
            "additional_detail": [
                {
                    "type": "public_notes",
                    "data": [{"public_note": pub_note.strip()} for pub_note in data['public_notes'] if pub_note.find('No Public Notes Found')==-1]
                }
            ] if len(data['public_notes'])>0 and data['public_notes'][0].find('No Public Notes Found')==-1 else [],
            "fillings_detail": [
                                    {
                                        "title": history['h_title'], 
                                        "date": history['h_date'].replace('/','-'),
                                        "file_url": f"https://wyobiz.wyo.gov/Business/GetImages.aspx?sid={history['FILE_NUMBERS']['number1']}&stid={history['FILE_NUMBERS']['number2']}",
                                        **({"description": history['h_change'].strip()} if history['h_change'].strip()!='' else {}),
                                    } 
                        for history in data['history_data']],
            "addresses_detail": [
            {
                "type": "registered_address",
                "address": data["office_address"],
                "description": "Registered principal address",
                "meta_detail": {}
            } if data["office_address"] and data["office_address"].strip().lower() != 'null' else None,
            {
                "type": "mail_address",
                "address": data["mail_address"],
                "description": "Mailing address",
                "meta_detail": {}
            } if data["mail_address"] and data["mail_address"].strip().lower() != 'null' else None
            ],
            "meta_detail": {
                **({"annual_returns_status": data["standing"]} if 'standing' in data else {}),
                "authorities_action": data["standing_other"],
                **({"latest_ar_year": data['additional_details']["latest_ar_year"]} if 'latest_ar_year' in data['additional_details'] else {}),
                **({"ar_exempt": data['additional_details']['ar_exempt']} if 'ar_exempt' in data['additional_details'] else {}),
                **({"license_tax": data['additional_details']['tax_paid']} if 'tax_paid' in data['additional_details'] else {})
            },
            "people_detail": [
                {
                    "designation": "registered_agent",
                    "name": data['additional_details']['registered_agent']['name'],
                    **({"address": data['additional_details']['registered_agent']['address'].replace('null','').replace('Null','').replace('NULL','')} if data['additional_details']['registered_agent']['address'] and data['additional_details']['registered_agent']['address'].strip().lower()!='null' else {}),
                    "meta_detail": {
                                    "registered_agent_availability": data["standing_ra"]
                                    }
                } if data['additional_details']['registered_agent']['name'] else None,
                {
                    **({"name": data['parties']['name_type'].split('(')[0].strip()} if 'name_type' in data['parties'] else {}),
                    **({"designation": data['parties']['name_type'].split('(')[1].strip()[:-1]} if 'name_type' in data['parties'] else {}),
                    **({"organization": data['parties']['organization'].replace('Organization:','').strip()} if 'organization' in data['parties'] and data['parties']['organization'].replace('Organization:','').strip() else {}),
                    **({"address": data['parties']['address'].replace('Address:','').strip()} if 'address' in data['parties'] and data['parties']['address'].replace('Address:','').strip() else {})
                } if 'name_type' in data['parties'] and data['parties']['name_type'].split('(')[0].strip() else None
            ]
        }
    
    DATA["addresses_detail"] = [e for e in DATA['addresses_detail'] if e]
    DATA['people_detail'] = [e for e in DATA['people_detail'] if e]
    
    ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
        json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
        SOURCE,json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
    insert_data([ROW])

    return jsonify({'result': 'added'})

if __name__ == '__main__':
    app.run()



