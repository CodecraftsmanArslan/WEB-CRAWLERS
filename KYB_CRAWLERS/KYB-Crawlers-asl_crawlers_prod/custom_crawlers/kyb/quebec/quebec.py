"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from datetime import datetime
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
ARGUMENT = sys.argv

meta_data = {
    'SOURCE': 'International Registries, Inc',
    'COUNTRY': 'Quebec',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.registreentreprises.gouv.qc.ca/RQAnonymeGR/GR/GR03/GR03A2_19A_PIU_RechEnt_PC/PageRechSimple.aspx?T1.CodeService=S00436&Clng=F&WT.co_f=22fd9cf9e710717554b1680487218676",
                      "Source Description": "The Business Registrar is notably responsible for maintaining the business register; the gateway to any company wishing to do business in Quebec."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.registreentreprises.gouv.qc.ca/RQAnonymeGR/GR/GR03/GR03A2_19A_PIU_RechEnt_PC/PageRechSimple.aspx?T1.CodeService=S00436&Clng=F&WT.co_f=22fd9cf9e710717554b1680487218676'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Quebec Official Registry" 
}

quebec_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)

selenium_helper = quebec_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True, Nopecha=False, timeout=300)
URL = "https://www.quebec.ca/entreprises-et-travailleurs-autonomes/migration-registraire"


wait = WebDriverWait(driver, 10)  # You can adjust the timeout (10 seconds in this example)


start_number = int(ARGUMENT[1]) if len(ARGUMENT) > 1 else 1140000000
end_number = int(ARGUMENT[2]) if len(ARGUMENT) > 1 else 3400000000

#Open Webpage
driver.get(URL)
time.sleep(3)
print("Website Opened!")
company_button = driver.find_element(By.XPATH, '//a[text()="Rechercher une entreprise au registre"]')
company_button.click()
time.sleep(3)
search_page_button = driver.find_element(By.XPATH, '//a[text()="Accéder au service - Rechercher une entreprise"]')
search_page_button.click()
time.sleep(3)
driver.switch_to.window(driver.window_handles[1])
print("Search Page Opened!")

#Search for data
def search(number):
    input_checkbox = driver.find_element(By.XPATH, '//input[@type="checkbox"]').get_attribute("checked")
    if input_checkbox == "true":
        pass
    else:
        # input_checkbox = driver.find_element(By.XPATH, '//input[@type="checkbox"]')
        input_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@type="checkbox"]')))
        input_checkbox.click()
        time.sleep(1)
    search_field = driver.find_element(By.XPATH, '//input[@title="Nom"]')
    search_field.clear()
    search_field.send_keys(number)
    search_field.send_keys(Keys.RETURN)
    time.sleep(5)

def if_error():
    while True:
        print("Website down. Retrying...")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(300)
        search_page_button = driver.find_element(By.XPATH, '//a[text()="Accéder au service - Rechercher une entreprise"]')
        search_page_button.click()
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[1])
        if len(driver.find_element(By.XPATH, '//input[@title="Nom"]')) > 0:
            break
        else:
            continue

#Basic logic
def crawl():
    for i in range(start_number, end_number):
        search_query = i
        while True:
            try:
                search(number=i)
                if "Aucun dossier n'a été retrouvé pour cette recherche." in driver.page_source:
                    print(f"No data found for: {search_query}")
                    break
                if "État de renseignements" in driver.page_source:
                    print(f"Scraping data for: {search_query}")
                    get_data()
                    back_button = driver.find_element(By.XPATH, '//input[@value="Retour aux résultats"]')
                    back_button.click()
                    time.sleep(3)
                    break
            except:
                if_error()
                continue

#Scrape data
def get_data():
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    def find_div(tag, string):
        the_div = soup.find(tag, string=string)
        the_div = the_div.find_next_sibling() if the_div else ""
        return the_div
    def find_data(div,string):
        the_data = div.find("span", string=string)
        the_data = the_data.parent.find_next_sibling().text.strip() if the_data else ""
        return the_data
    def find_input_data(p_div, string):
        the_div = p_div.find("span", string=string)
        if the_div:
            the_data = the_div.parent.find_next_sibling().get("value")
            return the_data
    
    all_merger_data = []
    all_activity_data = []
    all_share_holder_data = []
    all_est_data = []
    all_doc_ret_data = []
    all_name_data = []
    all_domicile_data = []
    all_previous_name_data = []
    all_legal_data = []
    all_update_date_data = []
    all_cont_data = []
    all_employee_data = []
    all_people_detail = []
    
    company_identification = find_div("h3", "Identification de l'entreprise")
    if company_identification:
        registration_number = find_data(company_identification, "Numéro d'entreprise du Québec (NEQ)")
        the_name = find_data(company_identification, "Nom")
        if the_name == "":
            name_first = find_data(company_identification, "Nom de famille")
            name_last = find_data(company_identification, "Prénom")
            the_name = name_first + " " + name_last
        other_language_name = find_data(company_identification, "Version du nom dans une autre langue")

    home_address_div = find_div("h3", "Adresse du domicile")
    if home_address_div:
        home_address = find_data(home_address_div, "Adresse ").replace("\n", " ")
        
    address_domicile_div = find_div("h3", "Adresse du domicile élu")
    if address_domicile_div:
        company_name = find_data(address_domicile_div, "Nom de l'entreprise")
        family_name = find_data(address_domicile_div, "Nom de famille")
        first_name = find_data(address_domicile_div, "Prénom")
        full_name = (first_name + " " + family_name).strip()
        domicile_address = find_data(address_domicile_div.find_next_sibling(), "Adresse ").replace("\n", " ")
        if domicile_address == "" and company_name == "" and full_name == "":
            domicile_address_div = find_div("h3", "Adresse du domicile élu")
            domicile_address = find_data(domicile_address_div, "Adresse ")
        domicile_dict = {
            "name": full_name,
            "company_name": company_name,
        }
        domicile_people_dict = {
            "designation": "legal_representative",
            "name": full_name
        }
        if full_name or company_name:
            all_domicile_data.append(domicile_dict)
            all_people_detail.append(domicile_people_dict)

    business_address_div = find_div("h3", "Adresse professionnelle")
    if business_address_div:
        business_address = find_data(business_address_div, "Adresse ")
    else:
        business_address = ""

    registration_div = find_div("h3", "Immatriculation")
    if registration_div:
        registration_date = registration_div.find("span", string="Date d'immatriculation")
        registration_date = registration_date.parent.find_next_sibling().get("value")
        reg_status = find_data(registration_div, "Statut")
        update_status_date = registration_div.find("span", string="Date de mise à jour du statut")
        update_status_date = update_status_date.parent.find_next_sibling().get("value")

    legal_status_div = find_div("h3", "Forme juridique")
    if legal_status_div:
        legal_status = find_data(legal_status_div, "Forme juridique")
        incorporation_date = find_data(legal_status_div, "Date de la constitution")
        legal_diet = find_data(legal_status_div, "Régime constitutif")
        current_diet = find_data(legal_status_div, "Régime courant")
        legal_dict = {
            "legal_diet": legal_diet,
            "current_diet": current_diet
        }
        if legal_diet or current_diet:
            all_legal_data.append(legal_dict)

    update_dates_div = find_div("h3", "Dates des mises à jour")
    if update_dates_div:
        info_status_update = update_dates_div.find("span", string="Date de mise à jour de l'état de renseignements")
        info_status_update = info_status_update.parent.find_next_sibling().get("value")
        last_anual_update = find_data(update_dates_div, "Date de la dernière déclaration de mise à jour annuelle")
        filing_declaration_2023 = update_dates_div.find("span", string="Date de fin de la période de production de la déclaration de mise à jour annuelle de 2023")
        filing_declaration_2023 = filing_declaration_2023.parent.find_next_sibling().get("value")
        filing_declaration_2022 = update_dates_div.find("span", string="Date de fin de la période de production de la déclaration de mise à jour annuelle de 2022")
        filing_declaration_2022 = filing_declaration_2022.parent.find_next_sibling().get("value")
        update_date_dict = {
            "info_status_update": info_status_update,
            "last_annual_update": last_anual_update,
            "2023_filing_declaration": filing_declaration_2023,
            "2022_filing_declaration": filing_declaration_2022
        }
        if info_status_update or last_anual_update or filing_declaration_2022 or filing_declaration_2023:
            all_update_date_data.append(update_date_dict)

    proxy_div = find_div("h3", "Fondé de pouvoir")
    if proxy_div:
        proxy_name = find_data(proxy_div, "Nom")
        proxy_address = find_data(proxy_div, "Adresse du domicile")
        proxy_dict = {
            "designation": "representative",
            "name": proxy_name,
            "address": proxy_address
        }
        if proxy_name or proxy_address:
            all_people_detail.append(proxy_dict)

    merger_div = find_div("h3", "Fusion, scission et conversion")
    if merger_div:
        if "La personne morale a fait l'objet de fusion(s)." in merger_div.text:
            merger_table = merger_div.find_next_sibling()
            all_merger_rows = merger_table.find_all("tr")
            for merger_row in all_merger_rows[1:]:
                merger_data = merger_row.find_all("td")
                merger_kind = merger_data[0].text
                applicable_law = merger_data[1].text
                merger_date = merger_data[2].text
                merger_name_address = merger_data[3].text
                merger_component = merger_data[4].text
                merger_resultant = merger_data[5].text
                merger_dict = {
                    "kind": merger_kind,
                    "law": applicable_law,
                    "date": merger_date,
                    "name_and_address": merger_name_address.replace("\n", " "),
                    "component_id": merger_component,
                    "resultant_id": merger_resultant
                }
                all_merger_data.append(merger_dict)

    continuation_div = find_div("h3", "Continuation et autre transformation")
    if continuation_div:
        if "La personne morale a fait l'objet d'une continuation." in continuation_div.text:
            continuation_data_div = continuation_div.find_next_sibling()
            cont_law = find_data(continuation_data_div, "Loi applicable").replace("\n", " ")
            cont_date = continuation_data_div.find("span", string="Date de la continuation ou autre transformation")
            cont_date = cont_date.parent.find_next_sibling().get("value") if cont_date else ""
            cont_dict = {
                "law": cont_law,
                "date": cont_date
            }
            if cont_law or cont_date:
                all_cont_data.append(cont_dict)

    activity_and_employee_div = find_div("h3", "Activités économiques et nombre de salariés")
    if activity_and_employee_div:
        all_activities = activity_and_employee_div.find_all("h3")
        for activity in all_activities[:-1]:
            activity_data = activity.find_next_sibling()
            activity_code = find_input_data(activity_data, "Code d'activité économique (CAE)")
            if activity_code:
                activity_code = activity_code.replace("null", "")
            activity_activity = find_data(activity_data, "Activité")
            activity_description = find_data(activity_data, "Précisions (facultatives)")
            activity_dict = {
                "activity_code": activity_code,
                "activity": activity_activity,
                "description": activity_description
            }
            if activity_code or activity_activity or activity_description:
                all_activity_data.append(activity_dict)

    all_employees = find_div("h3", "Nombre de salariés")
    if all_employees:
        employee_count = find_input_data(all_employees, "Nombre de salariés au Québec")
        no_french_text = "Proportion de salariés qui "
        all_span = all_employees.find_all("span")
        for span in all_span:
            if no_french_text in span.text:
                employees_cant_speak_french = span.parent.find_next_sibling().get("value")
            else:
                employees_cant_speak_french = ""
        employee_dict = {
            "employee_count": employee_count,
            "propotion_of_non_spoken_french_employees": employees_cant_speak_french
        }
        if employee_count or employees_cant_speak_french:
            all_employee_data.append(employee_dict)
        
    shareholders_div_ = soup.find("h3", string="Actionnaires")
    if shareholders_div_:
        shareholders_div__ = shareholders_div_.find_next_siblings()
        for shareholders_div in shareholders_div__:
            if shareholders_div.name == "fieldset":
                shareholder_name = find_data(shareholders_div, "Nom")
                if shareholder_name == "":
                    shareholder_first_name = find_data(shareholders_div, "Nom de famille")
                    shareholder_second_name = find_data(shareholders_div, "Prénom")
                    shareholder_name = (shareholder_second_name + " " + shareholder_first_name).strip()
                shareholder_address = find_data(shareholders_div, "Adresse du domicile")
                shareholder_dict = {
                    "name": shareholder_name,
                    "address": shareholder_address
                }
                shareholder_people = {
                    "designation": "shareholder",
                    "name": shareholder_name,
                    "address": shareholder_address
                }
                if shareholder_name or shareholder_address:
                    all_share_holder_data.append(shareholder_dict)
                    all_people_detail.append(shareholder_people)
            else:
                break

    admin_div_ = find_div("h3", "Liste des administrateurs")
    if admin_div_:
        admin_div__ = admin_div_.find_all("fieldset")
        for admin_div in admin_div__:
            admin_first_name = find_data(admin_div, "Prénom")
            admin_surname = find_data(admin_div, "Nom de famille")
            admin_full_name = admin_first_name + " " + admin_surname
            admin_start_date = find_input_data(admin_div, "Date du début de la charge")
            admin_start_date = admin_start_date if admin_start_date else ""
            admin_end_date = find_input_data(admin_div, "Date de fin de la charge")
            admin_end_date = admin_end_date if admin_end_date else ""
            admin_current_function = find_data(admin_div, "Fonctions actuelles")
            admin_home_address = find_data(admin_div, "Adresse du domicile")
            admin_business_address = find_data(admin_div, "Adresse professionnelle")
            admin_dict = {
                "name": admin_full_name,
                "appointment_date": admin_start_date,
                "termination_date": admin_end_date,
                "designation": admin_current_function,
                "address": admin_home_address,
                "meta_detail": {
                    "business_address": admin_business_address
                }
            }
            if admin_first_name or admin_start_date or admin_end_date or admin_current_function or admin_home_address:
                all_people_detail.append(admin_dict)

    leaders_not_members_div = soup.find("h3", string="Dirigeants non membres du conseil d'administration")
    if leaders_not_members_div:
        leaders_div_ = leaders_not_members_div.find_next_siblings()
        for leaders_div in leaders_div_:
            if leaders_div.name == "fieldset":
                leaders_first_name = find_data(leaders_div, "Prénom")
                leaders_surname = find_data(leaders_div, "Nom de famille")
                leaders_full_name = leaders_first_name + " " + leaders_surname
                leaders_current_function = find_data(leaders_div, "Fonctions actuelles")
                leaders_home_address = find_data(leaders_div, "Adresse du domicile")
                leaders_business_address = find_data(leaders_div, "Adresse professionnelle")
                leaders_dict = {
                    "name": leaders_full_name,
                    "designation": leaders_current_function,
                    "address": leaders_home_address,
                    "meta_detail": {
                        "business_address": leaders_business_address
                    }
                }
                if leaders_first_name or leaders_current_function or leaders_home_address:
                    all_people_detail.append(leaders_dict)
            else:
                break
    
    establishment_div = find_div("h2", "Établissements")
    if establishment_div:
        establishment_table = establishment_div.find("table")
        if establishment_table:
            est_rows = establishment_table.find_all("tr")
            for est_row in est_rows[1:]:
                est_data = est_row.find_all("td")
                est_number = est_data[0].text.split("-")[0].replace("(holdings)", "").strip()
                est_name = est_data[0].text.split("-")[1].split("(")[0].strip()
                est_title = est_data[0].text.replace(est_number, "").replace(est_name, "").replace("-", "").replace("(", "").replace(")", "").strip()
                est_address = est_data[1].text.strip()
                est_activity = est_data[2].text.split("(")[0].strip()
                est_act_code = est_data[2].text.replace(est_activity, "").strip()
                est_dict = {
                    "number": est_number,
                    "name": est_name,
                    "title": est_title,
                    "address": est_address,
                    "activity": est_activity,
                    "code": est_act_code
                }
                if est_number or est_name or est_address or est_activity:
                    all_est_data.append(est_dict)
    
    documents_retained_div = find_div("h3", "Documents conservés")
    if documents_retained_div:
        doc_ret_table = documents_retained_div.find("table")
        if doc_ret_table:
            doc_ret_rows = doc_ret_table.find_all("tr")
            for doc_ret_row in doc_ret_rows[1:]:
                doc_ret_data = doc_ret_row.find_all("td")
                doc_type = doc_ret_data[0].text
                doc_date = doc_ret_data[1].text
                doc_ret_dict = {
                    "filing_type": doc_type,
                    "date": doc_date
                }
                if doc_type or doc_date:
                    all_doc_ret_data.append(doc_ret_dict)
    
    name_index = find_div("h2", "Index des noms")
    name_index= name_index.find_next_sibling() if name_index else ""
    if name_index:
        name_index_update_date = find_input_data(name_index, "Date de mise à jour de l'index des noms")
    else:
        name_index_update_date = ""

    name_table_div = name_index.find_next_sibling()
    if name_table_div.name == "h3":
        name_table_ = name_table_div.find_next_sibling()
        name_table = name_table_.find("table")
        if name_table:
            name_rows = name_table.find_all("tr")
            for name_row in name_rows[1:]:
                name_data = name_row.find_all("td")
                if len(name_data) >= 5:
                    name_name = name_data[0].text.strip()
                    name_another_lang = name_data[1].text.strip()
                    name_date_dec = name_data[2].text.strip()
                    name_withdrawal_date = name_data[3].text.strip()
                    name_situation = name_data[4].text.strip()
                    name_dict = {
                        "name": name_name,
                        "meta_detail": {
                            "name_in_foreign_language": name_another_lang,
                            "declaration_withdrawn": name_withdrawal_date,
                            "name_status": name_situation
                        },
                        "update_date": name_date_dec
                    }
                    if name_name or name_another_lang or name_date_dec or name_situation:
                        all_name_data.append(name_dict)
                else:
                    name_name = name_data[0].text.strip()
                    name_date_dec = name_data[1].text.strip()
                    name_withdrawal_date = name_data[2].text.strip()
                    name_situation = name_data[3].text.strip()
                    name_dict = {
                        "name": name_name,
                        "meta_detail": {
                            "declaration_withdrawn": name_withdrawal_date,
                            "name_status": name_situation
                        },
                        "update_date": name_date_dec
                    }
                    if name_name or name_another_lang or name_date_dec or name_situation:
                        all_name_data.append(name_dict)
    
    previous_name_table_div_ = name_table_.find_next_sibling()
    if previous_name_table_div_.name == "h3" and previous_name_table_div_.text == "Autres noms utilisés au Québec":
        previous_name_table_div = previous_name_table_div_.find_next_sibling()
        previous_name_table = previous_name_table_div.find("table")
        if previous_name_table:
            previous_name_rows = previous_name_table.find_all("tr")
            for previous_name_row in previous_name_rows[1:]:
                previous_name_data = previous_name_row.find_all("td")
                previous_name_name = previous_name_data[0].text.strip()
                previous_name_another_lang = previous_name_data[1].text.strip()
                previous_name_date_dec = previous_name_data[2].text.strip()
                previous_name_withdrawal_date = previous_name_data[3].text.strip()
                previous_name_situation = previous_name_data[4].text.strip()
                previous_name_dict = {
                    "name": previous_name_name,
                    "previous_name_in_foreign_language": previous_name_another_lang,
                    "declaration_withdrawn": previous_name_withdrawal_date,
                    "previous_name_status": previous_name_situation,
                    "update_date": previous_name_date_dec
                }
                if previous_name_name or previous_name_another_lang or previous_name_date_dec or previous_name_situation:
                    all_previous_name_data.append(previous_name_dict)

    OBJ = {
        "registration_number": registration_number,
        "name": the_name,
        "name_in_foreign": other_language_name,
        "registration_date": registration_date,
        "status": reg_status,
        "status_updated": update_status_date,
        "type": legal_status,
        "incorporation_date": incorporation_date,
        "addresses_detail": [
            {
                "type": "home_address",
                "address": home_address
            },
            {
                "type": "business_address",
                "address": business_address
            },
            {
                "type": "legal_address",
                "address": domicile_address
            }
        ],
        "additional_detail": [
            {
                "type": "domicile_info",
                "data": all_domicile_data
            },
            {
                "type": "legal_framework",
                "data": all_legal_data
            },
            {
                "type": "update_dates",
                "data": all_update_date_data
            },
            {
                "type": "merger_split_conversion_info",
                "data": all_merger_data
            },
            {
                "type": "transformation_details",
                "data": all_cont_data
            },
            {
                "type": "activities_info",
                "data": all_activity_data
            },
            {
                "type": "employees_info",
                "data": all_employee_data
            },
            {
                "type": "shareholders_info",
                "data": all_share_holder_data
            },
            {
                "type": "establishment_info",
                "data": all_est_data
            },
            {
                "type": "aliases_info",
                "data": all_previous_name_data
            }
        ],
        "people_detail": all_people_detail,
        "fillings_detail": all_doc_ret_data,
        "previous_names_detail": all_name_data,
        "name_index_updated": name_index_update_date
    }

    OBJ = quebec_crawler.prepare_data_object(OBJ)
    ENTITY_ID = quebec_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
    NAME = OBJ['name'].replace("%","%%")
    BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
    ROW = quebec_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
    quebec_crawler.insert_record(ROW)

try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    quebec_crawler.db_log(log_data)
    quebec_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    quebec_crawler.db_log(log_data)