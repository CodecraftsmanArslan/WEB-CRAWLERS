import sys, traceback, time, re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
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
    for i in range(start_num,60):
        print("\nCurrent Number", i)
        url = f"https://repo-prod.revenuedev.org/api/block/AF/?q=&name=&from={12*i}&size=12&status=&code=&description=&sort=date_created:-1"

        headers = {
        'Cookie': 'connect.sid=s%3ALqj_pudoRDQ-kebRYXYfh4of4WhzezOj.QnBWYFpxTd6KjlZCa3WpanlXuukWXmyhnySIrbOnc2Y'
        }

        response = request_helper.make_request(url,headers=headers).json()
        base_url="https://afghanistan.revenuedev.org/block/"
        result_list = []
        cordi=[]
        for u1 in response["records"]:
            id=u1["mcas_id"]
            url=base_url+str(id)
            m1_url=request_helper.make_request(url)
            r1=request_helper.make_request(f"https://repo-prod.revenuedev.org/api/block/AF/{id}").json()
            name=r1["name"] 
            cod=r1["code"]
            des=r1["description"] 
            exp=r1["expires_on"] if r1["expires_on"] is not None else ""
            dat=r1["date_created"].split("T")[0]
            sta=r1["status"]

            for u in r1["plot"]["polygons"][0]["points"]:
                n1=str(u["latitude"])
                n2=str(u["longitude"])
                cor=n1+" "+n2
                cordi.append(cor)

            coordinate_str = ", ".join(cordi)
            additional_detail = []  
            if coordinate_str:  
                additional_detail_ = {
                            "type":"coordinates_information",
                            "data":[
                                {
                                    "coordinate":coordinate_str
                                }
                            ]
                        }
                additional_detail.append(additional_detail_)

            OBJ={
                "name":name,
                "registration_date":dat,
                "status":sta,
                "inactive_date":exp.split('T')[0],
                "aliases":name,
                "company_code":cod,
                "description":des,
                "additional_detail":additional_detail
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