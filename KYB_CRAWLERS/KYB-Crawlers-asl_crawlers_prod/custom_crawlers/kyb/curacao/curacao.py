"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


meta_data = {
    'SOURCE' :'Curaçao Commercial Register',
    'COUNTRY' : 'Curaçao',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www2.curacao-chamber.com/", 
                        "Source Description": "The Curaçao Commercial Register, also known as the Handelsregister van Curaçao, is a government-run registry that keeps records of businesses and entities operating in Curaçao. It is responsible for maintaining and updating information on commercial activities and entities registered in Curaçao."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www2.curacao-chamber.com/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Curaçao Official Registry"
}
"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

curaçao_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = curaçao_crawler.get_selenium_helper()
s =  curaçao_crawler.get_requests_session()

driver = selenium_helper.create_driver(headless=True, Nopecha=True)

API_URL = 'https://www2.curacao-chamber.com/companyselect.asp'
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}
arguments = sys.argv
start_number = int(arguments[1]) if len(arguments)>1 else 1
end_number  = 165107
# search_numbers = [73816,4607,49516, 7090, 112376 ,62138, 109007,53367, 165107]
def wait_for_captcha_to_be_solved(browser):
        try:
            while True:
                iframe_element = browser.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                browser.switch_to.frame(iframe_element)
                wait = WebDriverWait(browser, 10000)
                print('trying to resolve captcha')
                if 'Error: Invalid API parameter(s). Try reloading the page.' in browser.page_source:
                    browser.refresh()
                    time.sleep(3)
                    continue
                checkbox = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"recaptcha-checkbox-checked")))
                print("Captcha has been Solved")
                # Switch back to the default content
                browser.switch_to.default_content()
                return browser
        except:
            print('captcha solution timeout error, retrying...')

try:
    for number in range(start_number, end_number):
        print("\nSearch Number =", number)
        payload = f'name=&companyid={number}&source=0&languageabbrev=ENG'

        response = s.post(API_URL,headers=HEADERS, data = payload)

        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        soup = BeautifulSoup(response.text,'html.parser')

        base_url = 'https://www2.curacao-chamber.com/'
        
        trade_name = soup.find('td', {'id': 'Companies_TradeName_data_cell'}).get_text(strip=True)
        trade_url = soup.find('td', {'id': 'Companies_TradeName_data_cell'}).find('a')['href']
        regstation_numer = soup.find('td', {'id': 'Companies_CompanyID_data_cell'}).get_text(strip=True)
        Establishment = soup.find('td', {'id': 'Companies_EstablishmentNr_data_cell'}).get_text(strip=True)
        aliases = soup.find('td', {'id': 'Companies_CompanyName_data_cell'}).get_text(strip=True)
        URL = base_url+trade_url

        driver.get(URL)
        time.sleep(5)
        wait_for_captcha_to_be_solved(driver)
        continue_button = driver.find_element(By.XPATH,'/html/body/form/input[3]')
        continue_button.click()
        time.sleep(2)
        
        if '<html><head></head><body></body></html>' in driver.page_source:
            print("\nNo Data Found Move To Next Number =", number)
            continue

        Soup = BeautifulSoup(driver.page_source,'html.parser')
        
        LegalFormID = Soup.find('td',{'id': 'LegalInfo_LegalFormID_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'LegalInfo_LegalFormID_data_cell'}) else ""
        statutory_seat = Soup.find('td',{'id': 'LegalInfo_StatutorySeat_data_cell'}).get_text(strip=True) if Soup.find('td',{'id': 'LegalInfo_StatutorySeat_data_cell'}) else ""
        Duration =  Soup.find('td',{'id': 'PartnerShipInfo_Duration_data_cell'}).get_text(strip=True) if Soup.find('td',{'id': 'PartnerShipInfo_Duration_data_cell'}) else ""
        DateEstablished = Soup.find('td',{'id': 'LegalInfo_DateEstablished_data_cell'}).get_text(strip=True) if Soup.find('td',{'id': 'LegalInfo_DateEstablished_data_cell'}) else ""
        DateIncorporated = Soup.find('td',{'id': 'LegalInfo_DateIncorporated_data_cell'}).get_text(strip=True) if Soup.find('td',{'id': 'LegalInfo_DateIncorporated_data_cell'}) else ""
        DateLastAmendment = Soup.find('td',{'id': 'LegalInfo_DateLastAmendment_data_cell'}).get_text(strip=True) if Soup.find('td',{'id': 'LegalInfo_DateLastAmendment_data_cell'}) else ""
        Address = Soup.find('td',{'id': 'Addresses_Street_data_cell'}).get_text(strip=True) if Soup.find('td',{'id': 'Addresses_Street_data_cell'}) else ""
        CountryID = Soup.find('td',{'id': 'Addresses_CountryID_data_cell'}).get_text(strip=True) if Soup.find('td',{'id': 'Addresses_CountryID_data_cell'}) else ""
        try:
            Mailing_address = Soup.find('td',{'id': '(same as above)_label_cell'}).get_text(strip=True)
        except:
            Mailing_address = Soup.find('td',{'id': 'Addresses_POBoxNr_data_cell'}).get_text(strip=True) if Soup.find('td',{'id': 'Addresses_POBoxNr_data_cell'}) else ''

        Industries = Soup.find('td',{'id': 'Activities_ActivityCategoryID_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'Activities_ActivityCategoryID_data_cell'}) else ""
        try:
            Dates = Soup.select('#status_cell > span')
            Inactive_Date = Dates[0].get_text(strip=True)
            Liquidation_Date = Dates[1].get_text(strip=True)
            date_pattern = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s\d{4}"
            matches1 = re.findall(date_pattern, Inactive_Date)
            matches2 = re.findall(date_pattern, Liquidation_Date)
            result1 = ", ".join(matches1)
            result2 = ", ".join(matches2)
        except:
            result1, result2 = "",""
        
        capital_data = Soup.find('td',{'id': 'FinancialDetails_nominalcapital_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'FinancialDetails_nominalcapital_data_cell'}) else ""
        AuthorizedCapital = Soup.find('td',{'id': 'FinancialInfo_AuthorizedCapital_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'FinancialInfo_AuthorizedCapital_data_cell'}) else ""
        IssuedCapital = Soup.find('td',{'id': 'FinancialInfo_IssuedCapital_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'FinancialInfo_IssuedCapital_data_cell'}) else ""
        PaidUpCapital = Soup.find('td',{'id': 'FinancialInfo_PaidUpCapital_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'FinancialInfo_PaidUpCapital_data_cell'}) else ""
        FiscalYear = Soup.find('td',{'id': 'FinancialInfo_DateStartFiscalYear_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'FinancialInfo_DateStartFiscalYear_data_cell'}) else ""
        DescriptionENG = Soup.find('td',{'id': 'BusinessObjects_DescriptionENG_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'BusinessObjects_DescriptionENG_data_cell'}) else ""
        ForeignAddresses = Soup.find('td',{'id': 'ForeignAddresses_Street_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'ForeignAddresses_Street_data_cell'}) else ""
        PostalCode = Soup.find('td',{'id': 'ForeignAddresses_PostalCode_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'ForeignAddresses_PostalCode_data_cell'}) else ""
        CityName = Soup.find('td',{'id': 'ForeignAddresses_CityName_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'ForeignAddresses_CityName_data_cell'}) else ""
        Foreign_CountryID = Soup.find('td',{'id': 'ForeignAddresses_CountryID_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'ForeignAddresses_CountryID_data_cell'}) else ""
        IsDifferentShares = Soup.find('td',{'id': 'FinancialInfo_IsDifferentShares_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'FinancialInfo_IsDifferentShares_data_cell'}) else ""
        EndFiscalYear = Soup.find('td',{'id': 'FinancialInfo_DateEndFiscalYear_data_cell'}).get_text(strip=True) if  Soup.find('td',{'id': 'FinancialInfo_DateEndFiscalYear_data_cell'}) else ""


        additional_detail = []
        if AuthorizedCapital != "":
            add_dict = {
                        "type":'capital_information',
                        "data":[
                            {
                                "nominal_capital":capital_data,
                                "authorized_capital":AuthorizedCapital,
                                "issued_capital":IssuedCapital,
                                "paid_up_capital":PaidUpCapital,
                            }
                        ]
                        }
            additional_detail.append(add_dict)
        try:
            table = Soup.find(id="Excerpt2")
            trs = table.find_all('tr')
            all_data = []
            partner_data = {}  
            for tr in trs[1:]:  
                tds = tr.find_all('td')
                if len(tds) >= 2:
                    key = tds[0].text.strip()
                    value = tds[1].text.strip()
                    partner_data[key] = value
                else:
                    if partner_data:
                        all_data.append(partner_data)
                        partner_data = {} 
            if partner_data:
                all_data.append(partner_data)
                
            people_details = []
            for item in all_data:
                data_dict = {
                    "designation": item.get('Function',''),
                    "name": item.get('Name',''),
                    "meta_detail":{
                        "date_of_birth": item.get('Date of birth',''),
                        "place_of_birth": item.get('Place of birth',''),
                        "country_of_birth": item.get('Country of birth',''),
                        'registration_number':item.get('Registration number official','')
                        
                    },
                    "nationality": item.get('Nationality','')
                }
                people_details.append(data_dict)
        except Exception as e:
            print("Exception in people_details", e)
            people_details  =[]
        
        OBJ = {
                "registration_number":regstation_numer,
                "name":trade_name,
                "registration_date":DateEstablished,
                'incorporation_date':DateIncorporated,
                'last_updated':DateLastAmendment,
                'inactive_date':result1,
                'liquidation_date':result2,
                "industries":Industries,
                'jurisdiction':CountryID,
                'aliases':aliases,
                'description':DescriptionENG,
                'shares':IsDifferentShares,
                'fiscal_year':FiscalYear,
                'end_fiscal_year':EndFiscalYear,
                'statutory_seat':statutory_seat,
                'duration':Duration,
                'type':LegalFormID,
                "addresses_detail":[
                    {
                    "type": "general_address",
                    "address":Address.replace('Unknown Address','').replace('Unknown','')+' '+CountryID
                    },
                    {
                    "type": "postal_address",
                    "address":Mailing_address+' '+CountryID
                    },
                    {
                    "type": "foreign_address",
                    "address":ForeignAddresses+' '+CityName+' '+Foreign_CountryID+' '+PostalCode
                    }
                ],
                "additional_detail":additional_detail,
                "people_detail":people_details
            }

        OBJ =  curaçao_crawler.prepare_data_object(OBJ)
        ENTITY_ID = curaçao_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = OBJ['incorporation_date']
        ROW = curaçao_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        curaçao_crawler.insert_record(ROW)

    curaçao_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    curaçao_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    curaçao_crawler.db_log(log_data) 