"""Import required library"""
import sys, traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler

meta_data = {
    'SOURCE' :'Chamber of Commerce',
    'COUNTRY' : 'Aruba',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://my.arubachamber.com/register/zoeken?q=%%5Bobject%%20KeyboardEvent%%5D", 
                        "Source Description": "The Chamber of Commerce in Aruba is responsible for registering businesses, maintaining the business registry, providing information and support to entrepreneurs, and promoting economic development on the island. It serves as a vital institution for businesses and entrepreneurs in Aruba, ensuring proper documentation and compliance with legal requirements for companies operating on the island."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://my.arubachamber.com/register/zoeken?q=%5Bobject%20KeyboardEvent%5D'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Aruba Chamber of Commerce"
}
aruba_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = aruba_crawler.get_requests_helper()

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv
SKIP = int(arguments[1]) if len(arguments)>1 else 0

def crawl():
    i = 1000
    skip = 0

    API_URL_ = f'https://api.arubachamber.com/api/v1/bedrijf/public/search?searchTerm=&take=10&skip={skip}&includeActief=true&includeInactief=true'
    response = request_helper.make_request(API_URL_)
    json_data = response.json()
    skip = SKIP
    while skip <= json_data['totalRowCount']:
        print(skip)
        API_URL = f'https://api.arubachamber.com/api/v1/bedrijf/public/search?searchTerm=&take={i}&skip={skip}&includeActief=true&includeInactief=true'
        res = request_helper.make_request(API_URL)
        STATUS_CODE = res.status_code
        DATA_SIZE = len(res.content)
        CONTENT_TYPE = res.headers['Content-Type'] if 'Content-Type' in res.headers else 'N/A'
        json_data = res.json()
        
        skip += 1000

        registation_number = []
        for data in json_data['resultSet']:
            data_registation_number = data['dossiernummer']['registratienummer']
            registation_number.append(data_registation_number)
    
        for number in registation_number:
            
            DATA_API = f"https://api.arubachamber.com/api/v1/bedrijf/public/HANDELSREGISTER/{number}/0"
        
            data_response = request_helper.make_request(DATA_API)
            try:
                if data_response is not None:
                    data_res = data_response.json()
            except:
                print("API response is None on this number", number)
                pass
             
            OBJ = {
                    "aliases":data_res['bedrijfsnaam'].replace("%","%%"),
                    "name":data_res['handelsnaam'].replace("%","%%"),
                    "status":data_res['status'],
                    "status_date":data_res['datumIngangStatus'],
                    "jurisdiction":data_res['statutaireZetel'] if data_res['statutaireZetel'] != None else "",
                    "incorporation_date":data_res['datumVestiging'].replace("T00:00:00Z",""),
                    "registration_number":str(data_res['nummer']),
                    "industries":data_res['hoofdbranch'].replace("-",""),
                    "description":data_res["doelstellingNL"] if data_res['doelstellingNL'] != None else "",
                    "addresses_detail": [
                        {
                            "type": "general_address",
                            "address": str(str(data_res['vestigingAdres']['gacCode']).replace("None","").replace("NULL","").replace("NONE","")+' '+ str(data_res['vestigingAdres']['gacStraatnaam']).replace("None","").replace("NULL","").replace("NONE","")+' '+str(data_res['vestigingAdres']['zone']).replace("None","").replace("NULL","").replace("NONE","")).strip()
                        } 
                    ],
                    "additional_detail":[
                        {
                        "type":"capital_information",
                        "data":[
                            {
                                "Social":str(data_res['kapitaalMaatschappelijk']).replace("None",""),
                                "Posted":str(data_res["kapitaalGeplaatst"]).replace("None",""),
                                "Deposited":str(data_res["kapitaalGestort"]).replace("None",""),
                                "start_date":data_res["kapitaalBeginBoekjaar"] if data_res["kapitaalBeginBoekjaar"] != None else "",
                                "end_date":data_res["kapitaalEindBoekjaar"] if data_res["kapitaalEindBoekjaar"] != None else "",
                            }
                        ]
                        }
                    ],
                    "people_detail":[
                        {
                            "name":people_detail["naam"],
                            "nationality":people_detail["geboorteland"] if people_detail["geboorteland"] != None else "",
                            "designation":people_detail["functie"],
                            "meta_detail":{
                            "birthplace":people_detail["geboorteplaats"] if people_detail["geboorteplaats"] != None else "",
                            "title":people_detail['titel'] if people_detail['titel'] != None else "",
                            "authority":people_detail["bevoegdheid"] if people_detail['bevoegdheid'] != None else ""
                            },
                            "appointment_date":people_detail["ingangsDatum"].replace("T00:00:00Z","")
                        }for people_detail in data_res['bestuur']
                    ]
                }
            
            OBJ =  aruba_crawler.prepare_data_object(OBJ)
            ENTITY_ID = aruba_crawler.generate_entity_id(OBJ['registration_number'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = OBJ["incorporation_date"]
            ROW = aruba_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            aruba_crawler.insert_record(ROW)

    return STATUS_CODE,DATA_SIZE, CONTENT_TYPE

try:
    STATUS_CODE,DATA_SIZE, CONTENT_TYPE = crawl()
    
    aruba_crawler.end_crawler()
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    aruba_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    aruba_crawler.db_log(log_data)
