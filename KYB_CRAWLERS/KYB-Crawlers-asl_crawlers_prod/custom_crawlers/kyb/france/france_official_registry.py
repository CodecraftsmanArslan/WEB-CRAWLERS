"""Set System Path"""
import sys
from pathlib import Path
import traceback
from CustomCrawler import CustomCrawler
import json
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
from bs4 import BeautifulSoup
import requests, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    'WARNINGS_WEB_HOOK': os.getenv('KYB_WARNINGS_WEB_HOOK'),
}

meta_data = {
    'SOURCE' :'Infogreffe',
    'COUNTRY' : 'France',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.infogreffe.fr/recherche-entreprise-dirigeant/recherche-avancee", 
                        "Source Description": "Infogreffe is an online platform and service provided by the French commercial courts that offers access to business and legal information about registered companies in France. It serves as a central database and information resource for individuals, businesses, and professionals seeking information on French companies."},
    'URL' : 'https://www.infogreffe.fr/recherche-entreprise-dirigeant/recherche-avancee',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "France Official Registry"
}

ZIP_CODES = json.load(open('kyb/france/input/zip_codes.json'))
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

france_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  france_crawler.get_requests_helper()

selenium_helper =  france_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)


def get_effective_beneficiaries(id):
    additional_detail = [] 
    data = []
    url = f"https://www.api.infogreffe.fr/athena/detail-entreprises/detail_entreprises/{id}/fonctions?filtre_natures=BENEFICIAIRE_EFFECTIF"
    response = request_helper.make_request(url, method="GET")
    if response is not None:
        json_data = response.json()
        if 'data' in json_data:
            for item in json_data['data']:
                data.append({
                    # 'type': 'effective_beneficiaries_information',
                    'file_url': f"https://www.api.infogreffe.fr/athena/personnes-morales-api-document/personnes_morales/documents/beneficiaires_effectifs?id_entreprise={item['id_entreprise']}&type_document=EXTRAIT"
                })
        if len(data) > 0:
            additional_detail.append({
                'type': 'effective_beneficiaries_information',
                'data': data
            })
    return additional_detail

def get_financial_analysis(id):
    additional_detail = []
    data = []
    url = f"https://www.api.infogreffe.fr/athena/detail-entreprises/detail_entreprises/{id}/chiffres_cles"
    response = request_helper.make_request(url, method="GET")
    if response is not None:
        json_data = response.json()
        for item in json_data:
            if 'date_cloture' in item and item['date_cloture'] is not None and item['date_cloture'] != "":
                data.append({
                    'years': item['date_cloture'],
                    'turnover': item['chiffre_affaire'] if item['chiffre_affaire'] is not None else '',
                    'result': item['resultat'] if item['resultat'] is not None else '',
                    'workforce': item['effectif'] if item['effectif'] is not None else 'NC'
                })
        if len(data) > 0:
            additional_detail.append({
                'type': 'financial_analysis',
                'data': data
            })
    return additional_detail

def get_mang_member_part(id_entreprise):
    people_detail = []
    url = f"https://www.api.infogreffe.fr/athena/detail-entreprises/detail_entreprises/{id_entreprise}/fonctions?filtre_natures=ORGANE"
    response = request_helper.make_request(url, method="GET")
    if response is not None:
        json_data = response.json()
        if 'data' in json_data:
            for member in json_data['data']:
                try:
                    name = f"{member['personne_physique']['premier_prenom']} {member['personne_physique']['nom_patronymique']}"
                    if name.strip() != "":
                        people_detail.append({
                            'name': name,
                            'designation': member['organe']['qualite']['libelle'] if 'organe' in member and 'qualite' in member['organe'] and 'libelle' in member['organe']['qualite'] else ''
                        })
                except:
                    pass
    return people_detail

# Check if a command-line argument is provided
if len(sys.argv) > 1:
    start_number = sys.argv[1]
else:
    start_number = "83390"

flag = True
try:
    for zip_code in ZIP_CODES:
        if flag and start_number != zip_code:
            continue
        flag = False
        print('ZIP_CODE: ', zip_code)
        for letter in range(ord('a'), ord('z')+1):
            print(chr(letter))
            url = f"https://www.api.infogreffe.fr/athena/recherche-api/recherche/entreprises_etablissements?nom_entreprise={chr(letter)}&critere_geographique={zip_code}&limit=10000&offset=0"
            response = request_helper.make_request(url, method="GET")
            STATUS_CODE = response.status_code
            DATA_SIZE = len(response.content)
            CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
            data = response.json()

            if 'data' not in data:
                continue

            for item in data['data']:
                try:
                    additional_detail = []
                    people_detail = []
                    print("Zip Code: ", start_number)
                    NAME = item["nom_entreprise"].replace("%", "%%") if item["nom_entreprise"] is not None else ""
                    registration_number = item["numero_identification"]
                    cancellation_date = item["date_radiation"]
                    adresse_declaree = item['adresse']['adresse_declaree']
                    activite_naf = []
                    if 'activite_naf' in item and "code" in item['activite_naf']:
                        additional_detail.append({
                            'type': 'industry_detail',
                            'data': [{
                                "code": item["activite_naf"]["code"],
                                "activity": item["activite_naf"]["libelle"]
                            }]
                        })
                    office_address = [
                        adresse_declaree["ligne1"],
                        adresse_declaree["ligne2"],
                        adresse_declaree["ligne3"],
                        adresse_declaree["code_postal"],
                        adresse_declaree["bureau_distributeur"]
                    ]

                    address = ", ".join(filter(None, office_address))
                    addreses_detail = []
                    addreses_detail.append({
                        "type": "office_address",
                        "address": address,
                    })
                    
                    cancellation_date = item["date_radiation"] if "date_radiation" in item and item["date_radiation"] != None else ""

                    registration_date = item["date_immatriculation"] if "date_immatriculation" in item else ""
                    
                    additional_detail = []
                    additional_detail.append({
                        "type": "industry_detail",
                        "data": [{
                            "code": item["activite_naf"]["code"] if item["activite_naf"] and "code" in item["activite_naf"] else "",
                            "name": item["activite_naf"]['libelle'] if item["activite_naf"] and "libelle" in item["activite_naf"] else ""
                        }] 
                    })
                    trade_name = ""
                    taught = ""
                    type_ = item["type_entite"] if "type_entite" in item else ""
                    additional_detail.extend(get_financial_analysis(item['id_entreprise']))
                    additional_detail.extend(get_effective_beneficiaries(item['id_entreprise']))
                    people_detail.extend(get_mang_member_part(item['id_entreprise']))
                    establishments_url = f"https://www.api.infogreffe.fr/athena/etablissements/etablissements?id_entreprise={item['id_entreprise']}&inclure_fermes=true&limit=3&offset=0"
                    establishments_response = request_helper.make_request(establishments_url, method="GET")
                    if establishments_response is not None:
                        establishments_data = establishments_response.json()
                        est_data = []
                        for establishment_data in establishments_data['data']:
                            establishments_type = establishment_data["type_etablissement"] if "type_etablissement" in establishment_data else ""
                            establishment_number = int(registration_number) + establishment_data["nic"] if "nic" in establishment_data and establishment_data["nic"] != None else ""
                            trade_name = establishment_data['nom_commercial']
                            taught = establishment_data['enseigne']

                            adresse_declaree = establishment_data["adresse"]["adresse_declaree"]
                            establishments_address_parts = [
                                adresse_declaree['ligne1'] if adresse_declaree and 'ligne1' in adresse_declaree else None,
                                adresse_declaree['ligne2'] if adresse_declaree and 'ligne2' in adresse_declaree else None,
                                adresse_declaree['ligne3'] if adresse_declaree and 'ligne3' in adresse_declaree else None,
                                adresse_declaree['code_postal'] if adresse_declaree and 'code_postal' in adresse_declaree else None,
                                adresse_declaree['bureau_distributeur'] if adresse_declaree and 'bureau_distributeur' in adresse_declaree else None
                            ]
                            try:
                                industry_info = f"{establishment_data['activite_naf']['code']} - {establishment_data['activite_naf']['libelle']}"
                            except:
                                industry_info = ''
                            establishments_address = ', '.join(filter(None, establishments_address_parts))
                            establishments_name = NAME
                            nic = establishment_data['nic']
                            nic_padded = str(nic).zfill(5) if nic is not None else ""
                            est_data.append({
                                "deregistered_date": establishment_data['date_fermeture'] if 'date_fermeture' in establishment_data and establishment_data['date_fermeture'] is not None else '',
                                "name": establishments_name,
                                "type": establishments_type,
                                "branch_registration_number": f"{establishment_number} {nic_padded}",
                                "address": establishments_address.replace("%", "%%") if establishments_address is not None else "",
                                "industry_info": industry_info
                            })
                        additional_detail.append({
                            "type": "establishment_detail",
                            "data": est_data
                        })

                    detail_entreprises_url = f"https://www.api.infogreffe.fr/athena/detail-entreprises/detail_entreprises/{item['id_entreprise']}"
                    detail_entreprise_response = request_helper.make_request(detail_entreprises_url, method="GET")
                    if detail_entreprise_response.status_code == 200:
                        detail_entreprise_data = detail_entreprise_response.json()
                        tax_number = detail_entreprise_data['numero_tva_intracommunautaire'] if "numero_tva_intracommunautaire" in detail_entreprise_data and detail_entreprise_data['numero_tva_intracommunautaire'] is not None else ""
                        type = detail_entreprise_data['personne_morale']['forme_juridique']['libelle'] if detail_entreprise_data and 'personne_morale' in detail_entreprise_data and detail_entreprise_data['personne_morale'] and 'forme_juridique' in detail_entreprise_data['personne_morale'] and detail_entreprise_data['personne_morale']['forme_juridique'] and 'libelle' in detail_entreprise_data['personne_morale']['forme_juridique'] else ""
                        number_of_employees = detail_entreprise_data['effectif'] if "effectif" in detail_entreprise_data and detail_entreprise_data['effectif'] is not None else ""
                        try:
                            leader_name = f"{detail_entreprise_data['personne_physique']['premier_prenom']} {detail_entreprise_data['personne_physique']['nom_patronymique']}"
                            if leader_name.replace('None', '').strip() != "":
                                people_detail.append({
                                    'designation': 'leader',
                                    'name': leader_name
                                })
                        except:
                            pass
                    try:
                        people_detail = []
                        bs4_url = f"https://www.infogreffe.fr/entreprise/{NAME.lower().replace(' ', '-')}/{registration_number}/{item['id_entreprise']}"

                        driver.get(bs4_url)
                        time.sleep(10)
                        agree_button = driver.find_elements(By.ID, 'didomi-notice-agree-button')
                        if len(agree_button) > 0:
                            print("Agree to accept")
                            # Wait for the element to be clickable
                            wait = WebDriverWait(driver, 10)
                            btn = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))

                            # Interact with the element
                            btn.click()
                        time.sleep(5)
                        try:
                            element = driver.find_element(By.XPATH, "//*[contains(text(), 'Chiffre d') and contains(text(), 'affaires')]")
                            turnover = element.find_element(By.XPATH, "./following-sibling::div").text
                        except:
                            turnover = ""
                        try:
                            element = driver.find_element(By.XPATH, "//*[contains(text(), 'Forme juridique')]")
                            status = element.find_element(By.XPATH, "./following-sibling::div").text
                        except:
                            status = ""
                        try:
                            element = driver.find_element(By.XPATH, "//*[contains(text(), 'Effectif')]")
                            effective_detail = element.find_element(By.XPATH, "./following-sibling::div").text
                        except:
                            effective_detail = ""
                        try:
                            element = driver.find_element(By.XPATH, "//*[contains(text(), 'SIRET')]")
                            establishment_number = element.find_element(By.XPATH, "./following-sibling::div").text
                        except:
                            establishment_number = ""
                        try:
                            element = driver.find_element(By.XPATH, "//*[contains(text(), 'Procédure collective')]/following-sibling::div")
                            anchor_tag = element.find_element(By.TAG_NAME, 'a')
                            additional_detail.append({
                                'type': 'procedure_info',
                                'data': [{
                                    'title': element.text.split('\n')[0],
                                    'url': anchor_tag.get_attribute('href')
                                }]
                            })
                        except:
                            pass
                    except Exception as e:
                        print("Error", e)

                except Exception as e:
                    print("Error message:", traceback.format_exc())
                    continue

                DATA = {
                    "name": NAME,
                    "registration_number": registration_number,
                    "registration_date": registration_date,
                    "tax_number": tax_number,
                    "type": type,
                    "turn_over": turnover,
                    "number_of_employees": number_of_employees,
                    "cancellation_date": cancellation_date,
                    "additional_detail": additional_detail,
                    "addresses_detail": addreses_detail,
                    "people_detail": people_detail,
                    "trade_name": trade_name,
                    "taught": taught,
                    "establishment_number": establishment_number,
                    "status": status,
                    "effective_detail": effective_detail,
                    "cancellation_date": cancellation_date
                }
                ENTITY_ID = france_crawler.generate_entity_id(reg_number=registration_number)
                BIRTH_INCORPORATION_DATE = ''
                DATA = france_crawler.prepare_data_object(DATA)
                ROW = france_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)

                france_crawler.insert_record(ROW)
            
    driver.quit()
    log_data = {"status": 'success',
                     "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    france_crawler.db_log(log_data)
    france_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                     "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    france_crawler.db_log(log_data)
    
