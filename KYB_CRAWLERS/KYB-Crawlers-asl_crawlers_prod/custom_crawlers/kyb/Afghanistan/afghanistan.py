import sys, traceback, time, re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import requests
from CustomCrawler import CustomCrawler



meta_data = {
    'SOURCE' :'Ministry of Industry and Commerce - Central Business Registry',
    'COUNTRY' : 'Afghanistan',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://afghanistan.revenuedev.org/owner", 
                        "Source Description": ""},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://afghanistan.revenuedev.org/owner'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Afghanistan Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

arguments = sys.argv
start_num = int(arguments[1]) if len(arguments)>1 else 0

Afghanistan_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  Afghanistan_crawler.get_requests_helper()

try:
    for i in range(start_num,80):
        print("\nCurrent Number",i)
        url = f"https://repo-prod.revenuedev.org/api/owners/AF/ws/-1?q=&name=&service_types.name=&type=&city=&hide_incomplete=&financials=&sort=name:1&from={12*i}&size=12&with_license=true"
        headers = {
            'Cookie': 'connect.sid=s%3ALqj_pudoRDQ-kebRYXYfh4of4WhzezOj.QnBWYFpxTd6KjlZCa3WpanlXuukWXmyhnySIrbOnc2Y'
        }

        response = request_helper.make_request(url,headers=headers).json()
        base_url = "https://afghanistan.revenuedev.org/owner/"
        additional_details = []
        objs_list = []
        for t in response["records"]:
            id = t["_id"]
            url = base_url + str(id)
            main_url = requests.get(url)
            r1 = request_helper.make_request(f"https://repo-prod.revenuedev.org/api/owners/AF/{id}").json()

            # //General
            incorporation_date = r1["incorporation_date"].replace("T08:00:00.000Z", "") if r1["incorporation_date"] is not None else ""
            company_name = r1["name"]
            registration_no = r1["registration_no"] if r1["registration_no"] is not None else ""
            phone = r1["phone"]
            address = r1["address"].strip() if r1["address"] is not None else ""
            description = r1["description"]
            tax_number = r1["tin"]  if r1["tin"] is not None else ""
            type_ = r1["type"]
            city = r1["city"] if r1["city"] is not None else ""
            complete_address = address + " " + city
            Service_Types = ''
            # Initialize an empty lic list for each owner
            lic = []
            additional_details = []
            # //license
            license_url = "https://afghanistan.revenuedev.org/license/"
            for t1 in r1["licenses"]:
                lice_id = t1["id"]
                lic_url = license_url + lice_id
                st_da = t1["start_date"].replace("T08:00:00.000Z", "") if t1["start_date"] is not None else ""
                try:
                    li = t1["lic_code"]
                except:
                    li = ""
                st = t1["status"]
                ty_ = t1["type"]
                for min in t1["minerals"]:
                    na = min["name"]

                pr = ""
                dt=[]
                try:
                    for prov in t1["regions"]:
                        pr=prov["name"].replace("Afghanistan Country"," ")
                        dt.append(pr)

                        
                except:
                    pass

                province_str = ", ".join(dt)

                license = {
                        "type": "licenses_information",
                        "data":[
                            {
                                "date": st_da.split('T')[0],
                                "license_number": li,
                                "license_url": lic_url,
                                "type": ty_,
                                "status": st,
                                "asset": na,
                                "province":province_str,
                                }
                            ]
                        }
                additional_details.append(license)  # Append each license to the lic list

            # //Beneficial_owner
            poli=""
            try:
                detail={}
                for bene in r1["persons"]:
                    full = bene["full_name"] if bene["full_name"] is not None else ""
                    date = bene["date_acquired"].replace("T08:00:00.000Z", "") if bene["date_acquired"] is not None else ""
                    share = bene["share_type"]  if bene["share_type"] is not None else ""
                    perec = str(bene["percentage"])+''+"%" if str(bene["percentage"]) is not None else ""
                    resi = bene["country_of_residence"] if bene["country_of_residence"] is not None else ""
                    citi = bene["country_of_citizenship"] if bene["country_of_citizenship"] is not None else ""
                    se = bene["sex"] if bene["sex"] is not None else ""
                    posi = bene["position"] if bene["position"] is not None else ""
                    poli = bene["political_affiliation"] 
                    if bene["political_affiliation"] is False:
                        poli = "No"
                    else:
                        poli = " "
                    web = bene["website"] if bene["website"] is not None else ""
                    detail = {
                        "type": "beneficial_owner",
                        "data":[
                            {
                                "name": full,
                                "date": date.split('T')[0],
                                "share_type": share,
                                "percentage": perec.replace("None%",""),
                                "residence": resi,
                                "nationality": citi,
                                "sex": se,
                                "position": posi,
                                "political_affiliation": poli
                            }
                        ] 
                    }
                    additional_details.append(detail)
            except Exception as e:
                pass
                # additional_details.append(detail)

            OBJ = {
                "name": company_name,
                "aliases":company_name,
                "incorporation_date": incorporation_date.split('T')[0],
                "tax_number": tax_number,
                "registration_number": registration_no,
                "type": type_,
                "addresses_detail": [
                    {
                    "type": "general_address",
                    "address": complete_address
                    }
                ],
                "contacts_detail": [
                    {
                    "type": "phone_number",
                    "value": phone
                    }
                ],
                "service_type": Service_Types,
                "description": description,
                "additional_detail": additional_details,
            }
            OBJ =  Afghanistan_crawler.prepare_data_object(OBJ)
            ENTITY_ID = Afghanistan_crawler.generate_entity_id(company_name=OBJ['name'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = ""
            ROW = Afghanistan_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            Afghanistan_crawler.insert_record(ROW)

    Afghanistan_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    Afghanistan_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    Afghanistan_crawler.db_log(log_data)
       









       

  

   










