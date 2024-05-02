"""Import required library"""
import sys, traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler

meta_data = {
    'SOURCE' :'Registre National des Entreprises (RNE)',
    'COUNTRY' : 'Tunisia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.registre-entreprises.tn/rne-public/#/recherche-pm/recherche-resultat", 
                        "Source Description": "The Registre National des Entreprises (RNE), or National Business Registry, in Tunisia is a government institution responsible for maintaining and managing the business registers of the country. Its main role is to collect, register, and keep updated information about businesses operating in Tunisia."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.registre-entreprises.tn/rne-public/#/recherche-pm/recherche-resultat'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Tunisia Official Registry"
}

tunisia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  tunisia_crawler.get_requests_helper()

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

arguments = sys.argv
START_YEAR = int(arguments[1]) if len(arguments)>1 else 1995
def crawl():
    
    start_year = START_YEAR
    limit = 10
    API_URL = f'https://www.registre-entreprises.tn/rne-api/public/registres/pm?limit={limit}&idUnique=&identitePersonne=&etatRegistre=&anneeDeCreation={start_year}&bureauRegional=&nomSocieteFr=&nomSocieteAr=&nomCommercialFr=&nomCommercialAr=&nomResponsableFr=&nomResponsableAr=&detailActiviteFr=&detailActiviteAr=&rueSiegeFr=&rueSiegeAr=&notInStatusList=EN_COURS_CREATION'
    data_response = request_helper.make_request(API_URL)
    data_res = data_response.json()
    total = data_res['total']
    while start_year <= 2024:
        print("Current Year = ", start_year)
        API_URL_ = f'https://www.registre-entreprises.tn/rne-api/public/registres/pm?limit={total}&idUnique=&identitePersonne=&etatRegistre=&anneeDeCreation={start_year}&bureauRegional=&nomSocieteFr=&nomSocieteAr=&nomCommercialFr=&nomCommercialAr=&nomResponsableFr=&nomResponsableAr=&detailActiviteFr=&detailActiviteAr=&rueSiegeFr=&rueSiegeAr=&notInStatusList=EN_COURS_CREATION'
        data_response = request_helper.make_request(API_URL_)
        data_res = data_response.json()
        for data_ in data_res['registres']:
            register_number = data_['numRegistre']
            DATA_API = f'https://www.registre-entreprises.tn/rne-api/public/registres/pm/{register_number}'
            response = request_helper.make_request(DATA_API)
            all_data = response.json()
            code = all_data['codePostal'] if all_data['codePostal'] != None else ""
            villeFr = all_data['villeAr'] if all_data['villeAr'] != None else all_data['rueAr'] if all_data['rueAr'] != None else ""
            address = villeFr+''+code
            OBJ = {
                    "registration_number":register_number,
                    "name":all_data['denominationAr'] if all_data['denominationAr'] != None else "",
                    "aliases_lt":all_data['denominationLatin'] if all_data['denominationLatin'] != None else "",
                    "aliases_ar":all_data['denominationAr'] if all_data['denominationAr'] != None else "",
                    "type":all_data['objetActivitePrincipaleFr'] if all_data['objetActivitePrincipaleFr'] != None else all_data['objetActivitePrincipaleAr'] if all_data['objetActivitePrincipaleAr'] !=None else "",
                    "status":all_data['etatRegistreFr'] if all_data['etatRegistreFr'] != None else all_data['etatRegistreAr'] if all_data['etatRegistreAr'] != None else "",
                    "trade_name":all_data['nomCommercialFr'].replace(".","")if all_data['nomCommercialFr'] != None else all_data['nomCommercialAr'] if all_data['nomCommercialAr'] != None else "",
                    "unique_id": all_data['idUnique'] if all_data['idUnique'] != None else "",
                    "juridiction":all_data['juridictionAr'] if all_data['juridictionAr'] != None else "",
                    "registration_date":all_data['datePublication'] if all_data['datePublication'] != None else "",
                    "addresses_detail":[
                        {
                            "type": "headquater_address",
                            "address":address
                        },
                        {
                            "type":"social_address",
                            "address":all_data['rueAr'] if all_data['rueAr'] != None else ""
                        }
                    ],
                    "tax_status":all_data['situationFiscale']['nbMoisDefautFiscal'] if all_data['situationFiscale'] !=None else "",
                    "notification_date":all_data["situationFiscale"]['dateNotification'] if all_data["situationFiscale"] != None else "",
                    "commercial_name":all_data['nomCommercialAr'].replace(".","") if all_data['nomCommercialAr'] != None else "",
                    "update_date":all_data.get('dateEnregistrement',"") if all_data['dateEnregistrement'] != None else "",
                }
                
            OBJ =  tunisia_crawler.prepare_data_object(OBJ)
            ENTITY_ID = tunisia_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
            NAME = OBJ['name'].replace("%","%%") 
            BIRTH_INCORPORATION_DATE = OBJ['registration_date']
            ROW = tunisia_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            tunisia_crawler.insert_record(ROW)
        start_year += 1

    return STATUS_CODE,DATA_SIZE, CONTENT_TYPE

try:
    STATUS_CODE,DATA_SIZE, CONTENT_TYPE = crawl()
    tunisia_crawler.end_crawler()
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    tunisia_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    tunisia_crawler.db_log(log_data)
