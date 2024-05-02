"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from dateutil import parser


meta_data = {
    'SOURCE' :'Finnish Patent and Registration Office (PRH)',
    'COUNTRY' : 'Finland',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://virre.prh.fi/novus/home?execution=e1s79#search-result", 
                        "Source Description": "The Finnish Patent and Registration Office (PRH) is a government agency in Finland responsible for registering and protecting intellectual property rights, including patents, trademarks, and designs. Additionally, it handles the registration and maintenance of businesses and organizations in Finland, providing essential services for business owners and entrepreneurs."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://virre.prh.fi/novus/home?execution=e1s79#search-result'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Finland Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

finland_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  finland_crawler.get_requests_helper()
selenium_helper = finland_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False, proxy=False)

end_number = 5099999

arguments = sys.argv
start_number = int(arguments[1]) if len(arguments)>1 else 1

all_range_num = [f"{str(i).zfill(7)}" for i in range(start_number, end_number + 1)]

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str


def crawl():
    for number in all_range_num:
        search_url = 'https://virre.prh.fi/novus/home'
        driver.get(search_url)
        time.sleep(5)
        DATA_SIZE = len(driver.page_source)
        while True:
            if len( driver.find_elements(By.ID,'criteriaText')) == 0:
                driver.refresh()
                time.sleep(5)
            else:
                break
        search_field = driver.find_element(By.ID,'criteriaText')
        search_field.send_keys(number)
        time.sleep(2)
        search = driver.find_element(By.XPATH,'//*[@id="form-group-wrapper-input"]/div/span/button')
        search.click()
        time.sleep(5)
        if "Y-tunnusta ei löydy." in driver.page_source:
            print(f"Skipping Y-ID: {number}")
            continue
        
        print(f"Scraping data for Y-ID: {number}")
        # Define the keys you want to use for data extraction
        keys = ["Nimi", "Y-tunnus", "Kaupparekisterinumero", "Kotipaikka", "Yritysmuoto", "Yrityksen kieli", 
                "Rekisteröintiajankohta", "Lakkaamisajankohta", "Viimeisin rekisteröintiajankohta", 
                "Yrityksen tiedot järjestelmässä alkaen", "Yrityksen tila", "Yrityksellä on yrityskiinnityksiä", 
                "Yrityksellä on edunsaajatietoja","Postiosoite","Käyntiosoite","Puhelin","Sähköposti","Www"]

        if len(driver.find_elements(By.XPATH, '//a[@title="Näytä/piilota historia"]')) > 0:
            previous_name_button = driver.find_element(By.XPATH, '//a[@title="Näytä/piilota historia"]')
            previous_name_button.click()
            time.sleep(5)

        main_soup = BeautifulSoup(driver.page_source, "html.parser")

        data_dict = {}
        for key in keys:
            try:
                value = main_soup.find("td", string=key).find_next_sibling().text.strip()
                data_dict[key] = value
            except:
                data_dict[key] = ""
            
        
            previous_name_rows = main_soup.find_all("tr", class_="child-row")
            all_previous_names = []
            if previous_name_rows:
                for previous_name_row in previous_name_rows:
                    all_previous_name_cells = previous_name_row.find_all("td")
                    previous_name = all_previous_name_cells[1].text
                    previous_date = all_previous_name_cells[2].text
                    previous_name_dict = {
                        "name": previous_name,
                        "update_date": format_date(previous_date)
                    }
                    all_previous_names.append(previous_name_dict)

        all_aux_name_data = []
        all_discontinued_names = []

        if len(driver.find_elements(By.XPATH, '//a[text()="Toiminimet"]')) > 0:
            tiominimet = driver.find_element(By.XPATH, '//a[text()="Toiminimet"]')
            tiominimet.click()
            time.sleep(5)
            try:
                discontinued_names_button = driver.find_elements(By.XPATH, '//a[@title="Näytä/piilota historia"]')[1]
                discontinued_names_button.click()
                time.sleep(5)
            except:
                pass

            tiominimet_soup = BeautifulSoup(driver.page_source, "html.parser")
            
            if len(tiominimet_soup.find_all("td", string="Rinnakkaistoiminimi")) > 1:
                parallel_name_sweden = tiominimet_soup.find_all("td", string="Rinnakkaistoiminimi")[0]
                parallel_name_sweden = parallel_name_sweden.find_next_sibling().text.strip().split("(ruotsi)")[0].strip() if parallel_name_sweden else ""
                parallel_name_english = tiominimet_soup.find_all("td", string="Rinnakkaistoiminimi")[1]
                parallel_name_english = parallel_name_english.find_next_sibling().text.strip().split("(englanti)")[0].strip() if parallel_name_english else ""
            else:
                parallel_name_sweden = tiominimet_soup.find_all("td", string="Rinnakkaistoiminimi")
                parallel_name_sweden = parallel_name_sweden[0].find_next_sibling().text.strip().split("(ruotsi)")[0].strip() if parallel_name_sweden else ""
                parallel_name_english = ""

            auxilary_name = tiominimet_soup.find("td", string=re.compile("Aputoiminimi"))
            auxilary_name = auxilary_name.find_next_sibling().text.strip() if auxilary_name else ""

            if len(tiominimet_soup.find_all("td", string="Aputoiminimen käännös")) > 1:
                translated_auxilary_name = tiominimet_soup.find_all("td", string="Aputoiminimen käännös")[0]
                translated_auxilary_name = translated_auxilary_name.find_next_sibling().text.strip().split("(ruotsi)")[0].strip() if translated_auxilary_name else ""
                translated_auxilary_name_english = tiominimet_soup.find_all("td", string="Aputoiminimen käännös")[1]
                translated_auxilary_name_english = translated_auxilary_name_english.find_next_sibling().text.strip().split("(englanti)")[0].strip() if translated_auxilary_name_english else ""
            else:
                translated_auxilary_name = tiominimet_soup.find_all("td", string="Aputoiminimen käännös")
                translated_auxilary_name = translated_auxilary_name[0].find_next_sibling().text.strip().split("(ruotsi)")[0].strip() if translated_auxilary_name else ""
                translated_auxilary_name_english = ""

            if len(tiominimet_soup.find_all("td", string="Aputoiminimi")) > 2:
                auxilary_name_2 = tiominimet_soup.find_all("td", string="Aputoiminimi")[1]
                auxilary_name_2 = auxilary_name_2.find_next_sibling().text if auxilary_name_2 else ""
                auxilary_name_3 = tiominimet_soup.find_all("td", string="Aputoiminimi")[2]
                auxilary_name_3 = auxilary_name_3.find_next_sibling().text if auxilary_name_3 else ""
            elif len(tiominimet_soup.find_all("td", string="Aputoiminimi")) > 1:
                auxilary_name_2 = tiominimet_soup.find_all("td", string="Aputoiminimi")[1]
                auxilary_name_2 = auxilary_name_2.find_next_sibling().text if auxilary_name_2 else ""
                auxilary_name_3 = ""
            else:
                auxilary_name_2 = ""
                auxilary_name_3 = ""

            aux_name_dict = {
                "parallel_name_sweden": parallel_name_sweden,
                "parallel_name_english": parallel_name_english,
                "auxiliary_name": auxilary_name,
                "translated_auxiliary_name": translated_auxilary_name,
                "translated_auxiliary_name_english": translated_auxilary_name_english,
                "auxiliary_name_2": auxilary_name_2,
                "auxiliary_name_3": auxilary_name_3
            }

            all_aux_name_data.append(aux_name_dict)

            discontinued_name_rows = tiominimet_soup.find_all("tr", class_="child-row")
            if discontinued_name_rows:
                for discontinued_name_row in discontinued_name_rows[1:]:
                    all_dnr_td = discontinued_name_row.find_all("td")
                    if "Aputoiminimi" not in all_dnr_td[0].text:
                        p_name_dict = {
                            "parallel_name": all_dnr_td[1].text.strip().replace("(englanti)", "").replace("(ruotsi)", "").replace("\n", " ").strip() if all_dnr_td[1] else "",
                            "date": format_date(all_dnr_td[2].text.strip()) if all_dnr_td[2] else ""
                        }
                        all_discontinued_names.append(p_name_dict)
                    else:
                        break

            discontinued_aux_name_rows = tiominimet_soup.find_all("tr", class_="child-row")
            if discontinued_aux_name_rows:
                for discontinued_aux_name_row in discontinued_aux_name_rows[1:]:
                    all_dnr_td = discontinued_aux_name_row.find_all("td")
                    if "Aputoiminimi" in all_dnr_td[0].text:
                        next_data = discontinued_aux_name_row.find_next_sibling()
                        next_data_cells = next_data.find_all("td")
                        a_name_dict = {
                            "auxiliary_name": next_data_cells[1].text.strip().replace("(englanti)", "").replace("(ruotsi)", "").replace("\n", " ").strip() if all_dnr_td[1] else "",
                            "date": format_date(next_data_cells[2].text.strip()) if all_dnr_td[2] else ""
                        }
                        all_discontinued_names.append(a_name_dict)
                    else:
                        continue

        if len(driver.find_elements(By.XPATH, '//a[text()="Toimialat"]')) > 0:
            toimialat_button = driver.find_element(By.XPATH, '//a[text()="Toimialat"]')
            toimialat_button.click()
            time.sleep(5)
            if len(driver.find_elements(By.XPATH, '//a[@title="Näytä/piilota historia"]')) > 0:
                previous_industry_button = driver.find_element(By.XPATH, '//a[@title="Näytä/piilota historia"]')
                previous_industry_button.click()
                time.sleep(5)

            industry_soup = BeautifulSoup(driver.page_source, "html.parser")
            all_previous_industry_details = []
            main_industry = industry_soup.find("td", string="Toimiala").find_next_sibling().text.strip().capitalize()
            all_previous_industries_rows = industry_soup.find_all("tr", class_="child-row")
            for previous_industry_row in all_previous_industries_rows:
                all_previous_industry_cells = previous_industry_row.find_all("td")
                previous_industry_dict = {
                    "industry": all_previous_industry_cells[1].text.strip(),
                    "date": format_date(all_previous_industry_cells[2].text.strip())
                }
                all_previous_industry_details.append(previous_industry_dict)

        OBJ = {
            "name":data_dict['Nimi'],
            "registration_number":data_dict['Y-tunnus'],
            "jurisdiction":data_dict['Kotipaikka'],
            "type":data_dict['Yritysmuoto'],
            "company_language":data_dict['Yrityksen kieli'],
            "registration_date":format_date(data_dict['Rekisteröintiajankohta'].replace(".","-")),
            "latest_registration_date":format_date(data_dict['Viimeisin rekisteröintiajankohta'].replace(".","-")),
            "status":data_dict['Yrityksen tila'],
            "has_business_mortgages":data_dict['Yrityksellä on yrityskiinnityksiä'],
            "has_beneficiary_information":data_dict['Yrityksellä on yrityskiinnityksiä'],
            "industries": main_industry,
            "addresses_detail":[
                {
                    "type":"postal_address",
                    "address":data_dict.get('Postiosoite','').replace("%","%%").replace("\n", "").replace("\t", "")
                },
                {
                    "type": "general_address",
                    "address":data_dict.get('Käyntiosoite','').replace("%","%%").replace("\n", "").replace("\t", "")
                }
            ],
            "contacts_detail":[
                {
                    "type":"phone_number",
                    "value":data_dict.get('Puhelin','').split(",")[0].strip()
                },
                {
                    "type":"phone_number_2",
                    "value":data_dict.get('Puhelin','').split(",")[1].strip() if len(data_dict.get('Puhelin','').split(",")) > 1 else ""
                },
                {
                    "type":"phone_number_3",
                    "value":data_dict.get('Puhelin','').split(",")[2].strip() if len(data_dict.get('Puhelin','').split(",")) > 2 else ""
                },
                {
                    "type":"email",
                    "value":data_dict.get('Sähköposti','').split(",")[0] 
                },
                {
                    "type":"email_2",
                    "value":data_dict.get('Sähköposti','').split(",")[1] if len(data_dict.get('Sähköposti','').split(",")) > 1 else ""
                },
                {
                    "type":"website_link",
                    "value":data_dict.get("Www",'').split(",")[0]
                },
                {
                    "type":"website_link",
                    "value":data_dict.get("Www",'').split(",")[0]if len(data_dict.get("Www",'').split(",")) > 1 else ""
                }
            ],
            "additional_detail": [
                {
                    "type": "action_names_detail",
                    "data": all_aux_name_data
                },
                {
                    "type": "discontinued_names",
                    "data": all_discontinued_names
                },
                {
                    "type": "historical_industy_info",
                    "data": all_previous_industry_details
                }
            ],
            "dissolution_date":format_date(data_dict['Lakkaamisajankohta'].replace(".","-")),
            "trade_register_number":format_date(data_dict['Kaupparekisterinumero']),
            "previous_names_detail": all_previous_names
        }

        OBJ =  finland_crawler.prepare_data_object(OBJ)
        ENTITY_ID = finland_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = ""
        ROW = finland_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        finland_crawler.insert_record(ROW)

try:
    crawl()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    finland_crawler.db_log(log_data)
    finland_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    finland_crawler.db_log(log_data)
