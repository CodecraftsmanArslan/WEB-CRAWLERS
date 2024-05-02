"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import string
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

meta_data = {
    'SOURCE' :'Solomon Islands Business Registry',
    'COUNTRY' : 'Solomon Islands',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.solomonbusinessregistry.gov.sb/", 
                        "Source Description": "The Solomon Islands Business Registry (SIBR) is the official government agency responsible for the registration and administration of businesses and companies in the Solomon Islands. It serves as the central repository of information on registered entities and ensures compliance with relevant laws and regulations."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.solomonbusinessregistry.gov.sb/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Solomon Islands Business Registry Crawler",
}

_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  _crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True,Nopecha=False)


"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv

people_list = list()

def change_date_format(date_string):

    if date_string:
        try:
            date = datetime.strptime(date_string, "%m/%d/%Y")
            new_date_string = date.strftime("%m-%d-%Y")
            return new_date_string
        except:
            pass
    else:
        return date_string

def get_owners_data(director_cards):
    global people_list

    if len(director_cards) > 0:

        for director in director_cards:
            director_dict = dict()
            if len(director.find_elements(By.CLASS_NAME, "individualName")) > 0:
                name_main_element = director.find_element(By.CLASS_NAME, "individualName")
                name_element = name_main_element.find_element(By.CLASS_NAME, "appAttrValue") if name_main_element else ""
                director_dict['name'] = name_element.text.replace("'", "''") if name_element else ""
            if len(director.find_elements(By.CLASS_NAME, "RoleCountryCode")) > 0:
                nationality_main_element = director.find_element(By.CLASS_NAME, "RoleCountryCode")
                nationality_element = nationality_main_element.find_element(By.CLASS_NAME, "appAttrValue") if nationality_main_element else ""
                director_dict['nationality'] = nationality_element.text.strip().replace("'", "''") if nationality_element else ""

            try:
                consent_main_element = director.find_element(By.CLASS_NAME, "postalAddressRoot")
                consent_element = consent_main_element.find_element(By.CLASS_NAME, "appAttrValue") if consent_main_element else ""
                director_dict['postal_address'] = consent_element.text.replace("'", "''") if consent_element else ""

            except NoSuchElementException as e:
                pass

            if len(director.find_elements(By.CLASS_NAME, "AppointedDate")) > 0:
                appointed_date_main_element = director.find_element(By.CLASS_NAME, "AppointedDate")
                appointed_date_element = appointed_date_main_element.find_element(By.CLASS_NAME, "appAttrValue") if appointed_date_main_element else ""
                director_dict['appointment_date'] = appointed_date_element.text.replace("'", "''") if appointed_date_element else ""

            try:
                ceased_date_main_element = director.find_element(By.CLASS_NAME, "EntityRolePhysicalAddresses")
                ceased_date_element = ceased_date_main_element.find_element(By.CLASS_NAME, "appAttrValue") if ceased_date_main_element else ""
                director_dict['address'] = ceased_date_element.text.replace("'", "''") if ceased_date_element else ""
            except NoSuchElementException as e:
                director_dict['address'] = ""

            director_dict['designation'] = "authorized_person"

            people_list.append(director_dict) if "name" in director_dict and director_dict['name'] else ''

def get_director_data(director_cards):
    global people_list

    if len(director_cards) > 0:

        for director in director_cards:
            director_dict = dict()
            if len(director.find_elements(By.CLASS_NAME, "individualName")) == 0:
                continue
            name_main_element = director.find_element(By.CLASS_NAME, "individualName")
            name_element = name_main_element.find_element(By.CLASS_NAME, "appAttrValue") if name_main_element else ""
            director_dict['name'] = name_element.text.replace("'", "''") if name_element else ""

            nationality_main_element = director.find_element(By.CLASS_NAME, "RoleCountryCode")
            nationality_element = nationality_main_element.find_element(By.CLASS_NAME, "appAttrValue") if nationality_main_element else ""
            director_dict['nationality'] = nationality_element.text.strip().replace("'", "''") if nationality_element else ""

            try:
                consent_main_element = director.find_element(By.CLASS_NAME, "ConsentReceivedYn")
                consent_element = consent_main_element.find_element(By.CLASS_NAME, "appAttrValue") if consent_main_element else ""
                consent = consent_element.text.replace("'", "''") if consent_element else ""

            except NoSuchElementException as e:
                consent = ''

        
            appointed_date_main_element = director.find_element(By.CLASS_NAME, "AppointedDate")
            appointed_date_element = appointed_date_main_element.find_element(By.CLASS_NAME, "appAttrValue") if appointed_date_main_element else ""
            director_dict['appointment_date'] = appointed_date_element.text.replace("'", "''") if appointed_date_element else ""

            
            director_dict['meta_detail'] = {
                "consent": consent,
            } if consent else {}

            try:
                ceased_date_main_element = director.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-directorsTab-categorizerBox-directorRepeater-director-dirBox-ceasedDateStandardDelegateBox-ceasedDateBox-CeasedDate")
                ceased_date_element = ceased_date_main_element.find_element(By.CLASS_NAME, "appAttrValue") if ceased_date_main_element else ""
                director_dict['termination_date'] = ceased_date_element.text.replace("'", "''") if ceased_date_element else ""
            except NoSuchElementException as e:
                director_dict['termination_date'] = ""

            director_dict['designation'] = "director"

            people_list.append(director_dict) if director_dict['name'] else ''


def crawl_company_data_by_tags(company_tags, driver):
    global people_list
    existing_record = list()
    with open('registration_number.txt', 'r') as file:
        for line in file:
            existing_record.append(str(line.strip()))

    for i, element in enumerate(company_tags):
        company_tags = driver.find_elements(By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu")
        company_tags[i].click()
        time.sleep(5)

        if len(driver.find_elements(By.CLASS_NAME, 'businessNameContextBox')) > 0:
            row_1 = driver.find_element(By.CLASS_NAME, 'businessNameContextBox').text
        else:
            row_1 = driver.find_element(By.CLASS_NAME, 'appEntityContextBox').text
        split_text = row_1.split("- Private Company")[0]
        split_text_2 = split_text.split("(")
        name = split_text_2[0]
        registration_number = split_text_2[1].replace(")", "").strip()

        if name == "":
            pattern = r'\((.*?)\)'
            matches = re.findall(pattern, row_1)
            registration_number = matches[len(matches) - 1] if len(matches) > 0 else ""
            name = row_1.replace(registration_number, "").replace("()", "").strip()
            
        if str(registration_number) not in existing_record:

            try:
                type_main_element = driver.find_element(By.CLASS_NAME,"brViewLocalCompany-tabsBox-detailsTab-details-entitySubTypeBox-EntitySubTypeCode")
                type_element = type_main_element.find_element(By.CLASS_NAME, "appAttrValue") if type_main_element else ""
                company_type = type_element.text.replace("'", "''") if type_element else ""
            except:
                company_type = ""

            if len(driver.find_elements(By.CLASS_NAME, "StartDate")) > 0:
                data_name_first_used_m_el = driver.find_element(By.CLASS_NAME, "StartDate")
                data_name_first_used_element = data_name_first_used_m_el.find_element(By.CLASS_NAME, "appAttrValue") if data_name_first_used_m_el else ""
                data_name_first_used = data_name_first_used_element.text.replace("'", "''") if data_name_first_used_element else ""
            else:
                data_name_first_used = ""
            status_main_el = driver.find_element(By.CLASS_NAME, "Status")
            status_el = status_main_el.find_element(By.CLASS_NAME, "appAttrValue") if status_main_el else ""
            status = status_el.text.replace("'", "''") if status_el else ""

            incorporation_date_main_el = driver.find_element(By.CLASS_NAME, "RegistrationDate")
            incorporation_date_el = incorporation_date_main_el.find_element(By.CLASS_NAME, "appAttrValue") if incorporation_date_main_el else ""
            incorporation_date = incorporation_date_el.text.replace("'", "''") if incorporation_date_el else ""
            try:
                have_own_rule_main_el = driver.find_element(By.CLASS_NAME, "CompanyRulesCode")
                have_own_rule_el = have_own_rule_main_el.find_element(By.CLASS_NAME, "appAttrValue") if have_own_rule_main_el else ""
                have_own_rule = have_own_rule_el.text.replace("'", "''") if have_own_rule_el else ""
            except:
                have_own_rule = ""

            if len(driver.find_elements(By.CLASS_NAME, "BusinessSectorCode")) > 0:
                industries_main_el = driver.find_element(By.CLASS_NAME, "BusinessSectorCode")
                industries_el = industries_main_el.find_element(By.CLASS_NAME, "appAttrValue") if industries_main_el else ""
                industries = industries_el.text.replace("'", "''") if industries_el else ""
            else:
                industries = ""
            if len(driver.find_elements(By.CLASS_NAME, "AnnualFilingMonth")) > 0:
                filing_month_main_el = driver.find_element(By.CLASS_NAME, "AnnualFilingMonth")
                filing_month_el = filing_month_main_el.find_element(By.CLASS_NAME, "appAttrValue") if filing_month_main_el else ""
                filing_month = filing_month_el.text.replace("'", "''") if filing_month_el else ""
            else:
                filing_month = ""

            try:
                last_filed_date_main_el = driver.find_element(By.CLASS_NAME, "LatestAnnualFiling")
                last_filed_date_el = last_filed_date_main_el.find_element(By.CLASS_NAME, "appAttrValue") if last_filed_date_main_el else ""
                last_filed_date = last_filed_date_el.text.replace("'", "''") if last_filed_date_el else ""
            except NoSuchElementException as e:
                last_filed_date = ""

            try:
                removal_reason_main_el = driver.find_element(By.CLASS_NAME, "RemovalReasonCode")
                removal_reason_el = removal_reason_main_el.find_element(By.CLASS_NAME, "appAttrValue") if removal_reason_main_el else ""
                removal_reason = removal_reason_el.text.replace("'", "''") if removal_reason_el else ""
            except NoSuchElementException as e:
                removal_reason = ""

            try:
                removal_date_main_el = driver.find_element(By.CLASS_NAME, "DeregistrationDate")
                removal_date_el = removal_date_main_el.find_element(By.CLASS_NAME, "appAttrValue") if removal_date_main_el else ""
                removal_date = removal_date_el.text.replace("'", "''") if removal_date_el else ""
            except NoSuchElementException as e:
                removal_date = ""

            try:
                re_registration_date_main_el = driver.find_element(By.CLASS_NAME, "ReregistrationDate")
                re_registration_date_el = re_registration_date_main_el.find_element(By.CLASS_NAME, "appAttrValue") if re_registration_date_main_el else ""
                re_registration_date = re_registration_date_el.text.replace("'", "''") if re_registration_date_el else ""
            except NoSuchElementException as e:
                re_registration_date = ""

            if len(driver.find_elements(By.CLASS_NAME, "individualName")) > 0:
                full_name_main_el = driver.find_element(By.CLASS_NAME, "individualName")
                full_name_el = full_name_main_el.find_element(By.CLASS_NAME, "appAttrValue") if full_name_main_el else ""
                full_name = full_name_el.text.replace("'", "''") if full_name_el else ""
            else: 
                full_name = ""

            if (len(driver.find_elements(By.CLASS_NAME, "EntityRolePhoneAddresses")) > 0):
                phone_main_el = driver.find_element(By.CLASS_NAME, "EntityRolePhoneAddresses")
                phone_el = phone_main_el.find_element(By.CLASS_NAME, "appAttrValue") if phone_main_el else ""
                phone = phone_el.text.replace("'", "''") if phone_el else ""

            if (len(driver.find_elements(By.CLASS_NAME, "EntityRoleEmailAddresses")) > 0):
                email_main_el = driver.find_element(By.CLASS_NAME, "EntityRoleEmailAddresses")
                email_el = email_main_el.find_element(By.CLASS_NAME, "appAttrValue") if email_main_el else ""
                email = email_el.text.replace("'", "''") if email_el else ""

            try:
                tabs_div = driver.find_element(By.CLASS_NAME, 'appTabs')
                ul_elements = tabs_div.find_elements(By.TAG_NAME, 'li')
                a_tag = ul_elements[1].find_element(By.TAG_NAME, 'a')
                to_be_executed = a_tag.get_attribute("onclick")
                to_be_executed = to_be_executed[to_be_executed.find('(catHtml'):to_be_executed.find('skip')+6].replace(', me','')
                driver.execute_script(to_be_executed)
            except:
                driver.execute_script(to_be_executed)
        
            time.sleep(10)

            if len(driver.find_elements(By.CLASS_NAME, "address")) > 0:
                office_address_main_el = driver.find_element(By.CLASS_NAME, "address")
                office_address_el = office_address_main_el.find_element(By.CLASS_NAME, "appAttrValue") if office_address_main_el else ""
                office_address = office_address_el.text.replace("'", "''") if office_address_el else ""
            else:
                office_address = ""
            
            if len(driver.find_elements(By.CLASS_NAME, "postal")) > 0:
                postal_address_main_el = driver.find_element(By.CLASS_NAME, "postal")
                postal_address_el = postal_address_main_el.find_element(By.CLASS_NAME, "appAttrValue") if postal_address_main_el else ""
                postal_address = postal_address_el.text.replace("'", "''") if postal_address_el else ""
            else:
                postal_address = ""
                
            try:
                company_record_address_main_el = driver.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-addressesTab-showInViewBox-locationOfCompanyRecordsPhysicalBox-locationOfCompanyRecordsPhysicalBox-withoutPostalIsPhysical-withoutEvidenceUpload-editAddress-categorizerBox-physicalAddresses-physicalAddress-address")
                company_record_address_el = company_record_address_main_el.find_element(By.CLASS_NAME, "appAttrValue") if company_record_address_main_el else ""
                company_record_address = company_record_address_el.text.replace("'", "''") if company_record_address_el else ""
            except NoSuchElementException as e:
                company_record_address = ""

            try:
                tabs_div = driver.find_element(By.CLASS_NAME, 'appTabs')
                ul_elements = tabs_div.find_elements(By.TAG_NAME, 'li')
                a_tag = ul_elements[2].find_element(By.TAG_NAME, 'a')
                span_tag = a_tag.find_element(By.TAG_NAME, 'span')
                third_span_tag_text = span_tag.text
                to_be_executed = a_tag.get_attribute("onclick")
                to_be_executed = to_be_executed[to_be_executed.find('(catHtml'):to_be_executed.find('skip')+6].replace(', me','')
                driver.execute_script(to_be_executed)
            except:
                driver.execute_script(to_be_executed)

            time.sleep(3)
            

            if third_span_tag_text == "Directors":
                director_cards = driver.find_elements(By.CLASS_NAME, "Direct")
                get_director_data(director_cards)

            if third_span_tag_text == "Owners":
                director_cards = driver.find_elements(By.CLASS_NAME, "Direct")
                get_owners_data(director_cards)

                        
            if third_span_tag_text == "Persons Authorised to Accept Service":
                authorized_people_cards = driver.find_elements(By.CLASS_NAME, "Direct")

                if len(authorized_people_cards) > 0:

                    for auth_person in authorized_people_cards:
                        auth_person_dict = dict()
                        name_main_element = auth_person.find_element(By.CLASS_NAME, "individualName")
                        name_element = name_main_element.find_element(By.CLASS_NAME, "appAttrValue") if name_main_element else ""
                        auth_person_dict['name'] = name_element.text.replace("'", "''") if name_element else ""
                        address_main_element = auth_person.find_element(By.CLASS_NAME, "EntityRolePhysicalAddresses")
                        address_element = address_main_element.find_element(By.CLASS_NAME, "appAttrValue") if address_main_element else ""
                        auth_person_dict['address'] = address_element.text.strip().replace("'", "''") if address_element else ""
                        postal_address_main_element = auth_person.find_element(By.CLASS_NAME, "EntityRolePostalAddresses")
                        postal_address_element = postal_address_main_element.find_element(By.CLASS_NAME, "appAttrValue") if postal_address_main_element else ""
                        auth_person_dict['postal_address'] = postal_address_element.text.strip().replace("'", "''") if postal_address_element else ""
                        
                        try:

                            phone_main_element = auth_person.find_element(By.CLASS_NAME, "brViewOverseasCompany-tabsBox-acceptSopTab-categorizerBox-acceptSopRepeater-acceptSopSelector-sopind-details-sopIndAdditionalAttributes-acceptSopPhoneBox-phoneAddress")
                            phone_element = phone_main_element.find_element(By.CLASS_NAME, "appAttrValue") if phone_main_element else ""
                            auth_person_dict['phone_number'] = phone_element.text.strip().replace("'", "''") if phone_element else ""
                        except:
                            auth_person_dict['phone_number'] = ""

                        appointed_date_main_element = auth_person.find_element(By.CLASS_NAME, "AppointedDate")
                        appointed_date_element = appointed_date_main_element.find_element(By.CLASS_NAME, "appAttrValue") if appointed_date_main_element else ""
                        auth_person_dict['appointment_date'] = appointed_date_element.text.replace("'", "''") if appointed_date_element else ""
                        auth_person_dict['designation'] = "authorized_person"
                        people_list.append(auth_person_dict) if auth_person_dict['name'] else ''

            try:
                tabs_div = driver.find_element(By.CLASS_NAME, 'appTabs')
                ul_elements = tabs_div.find_elements(By.TAG_NAME, 'li')
                a_tag = ul_elements[3].find_element(By.TAG_NAME, 'a')
                span_tag = a_tag.find_element(By.TAG_NAME, 'span')
                forth_span_tag_text = span_tag.text
                to_be_executed = a_tag.get_attribute("onclick")
                to_be_executed = to_be_executed[to_be_executed.find('(catHtml'):to_be_executed.find('skip')+6].replace(', me','')
                driver.execute_script(to_be_executed)
            except Exception as e:
                print("Exception message", e)
                driver.execute_script(to_be_executed)
        
            time.sleep(10)

            if forth_span_tag_text == "Shares & Shareholders":

                try:
                    total_shares_main_el = driver.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-totalNumShares-TotalShares")
                    total_shares_el = total_shares_main_el.find_element(By.CLASS_NAME, "appAttrValue") if total_shares_main_el else ""
                    total_shares = total_shares_el.text.replace("'", "''") if total_shares_el else ""
                except NoSuchElementException as e:
                    total_shares = ""

                sharesholders_cards = driver.find_elements(By.CLASS_NAME, "Direct")

                if len(sharesholders_cards) > 0:

                    for share_holder in sharesholders_cards:
                        share_holder_dict = dict()

                        try:
                            name_main_element = share_holder.find_element(By.CLASS_NAME, "individualName")
                            name_element = name_main_element.find_element(By.CLASS_NAME, "appAttrValue") if name_main_element else ""
                            share_holder_dict['name'] = name_element.text.replace("'", "''") if name_element else ""
                        except NoSuchElementException as e:
                            share_holder_dict['name'] = None
                            

                        if share_holder_dict['name'] == None:
                            try:
                                name_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderOther-shareholderName-EntityName")
                                name_element = name_main_element.find_element(By.CLASS_NAME, "appAttrValue") if name_main_element else ""
                                share_holder_dict['name'] = name_element.text.replace("'", "''") if name_element else ""
                            except NoSuchElementException as e:
                                share_holder_dict['name'] = None
                        
                        if share_holder_dict['name'] == None:
                            try:
                                name_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderEntity-directorNotEntityBox-entityLookup-EntityName")
                                name_element = name_main_element.find_element(By.CLASS_NAME, "appAttrValue") if name_main_element else ""
                                share_holder_dict['name'] = name_element.text.replace("'", "''") if name_element else ""
                            except NoSuchElementException as e:
                                share_holder_dict['name'] = None

                        try:
                            nationality_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderInd-details-ownerIndAdditionalAttributes-RoleCountryCode")
                            nationality_element = nationality_main_element.find_element(By.CLASS_NAME, "appAttrValue") if nationality_main_element else ""
                            share_holder_dict['nationality'] = nationality_element.text.strip().replace("'", "''") if nationality_element else ""

                        except NoSuchElementException as e:
                            share_holder_dict['nationality'] = ""
                        
                        try:
                            share_numbers_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderInd-details-noShareBundles-shareDetailsBox-ShareUnits")
                            share_numbers_element = share_numbers_main_element.find_element(By.CLASS_NAME, "appAttrValue") if share_numbers_main_element else ""
                            share_numbers = share_numbers_element.text.replace("'", "''") if share_numbers_element else ""
                        except NoSuchElementException as e:
                            try:
                                share_numbers_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderOther-noShareBundles-shareDetailsBox-ShareUnits")
                                share_numbers_element = share_numbers_main_element.find_element(By.CLASS_NAME, "appAttrValue") if share_numbers_main_element else ""
                                share_numbers = share_numbers_element.text.replace("'", "''") if share_numbers_element else ""
                            except NoSuchElementException as e:
                                try:
                                    share_numbers_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderEntity-noShareBundles-shareDetailsBox-ShareUnits")
                                    share_numbers_element = share_numbers_main_element.find_element(By.CLASS_NAME, "appAttrValue") if share_numbers_main_element else ""
                                    share_numbers = share_numbers_element.text.replace("'", "''") if share_numbers_element else ""
                                except NoSuchElementException as e:
                                    share_numbers = ""

                        try:
                            appointed_date_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderInd-AppointedDate")
                            appointed_date_element = appointed_date_main_element.find_element(By.CLASS_NAME, "appAttrValue") if appointed_date_main_element else ""
                            share_holder_dict['appointment_date'] = appointed_date_element.text.replace("'", "''") if appointed_date_element else ""
                        except NoSuchElementException as e:
                            try:
                                appointed_date_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderOther-AppointedDate")
                                appointed_date_element = appointed_date_main_element.find_element(By.CLASS_NAME, "appAttrValue") if appointed_date_main_element else ""
                                share_holder_dict['appointment_date'] = appointed_date_element.text.replace("'", "''") if appointed_date_element else ""
                            except NoSuchElementException as e:
                                appointed_date_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderEntity-AppointedDate")
                                appointed_date_element = appointed_date_main_element.find_element(By.CLASS_NAME, "appAttrValue") if appointed_date_main_element else ""
                                share_holder_dict['appointment_date'] = appointed_date_element.text.replace("'", "''") if appointed_date_element else ""
                        try:
                            foreign_investor_certificate_number_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderInd-details-ownerIndAdditionalAttributes-foreignInvestmentLookup-foreignInvestmentCertNumberLookupBox-ForeignInvestmentCertificateNum")
                            foreign_investor_certificate_number_element = foreign_investor_certificate_number_main_element.find_element(By.CLASS_NAME, "appAttrValue") if foreign_investor_certificate_number_main_element else ""
                            foreign_investor_certificate_number = foreign_investor_certificate_number_element.text.replace("'", "''") if foreign_investor_certificate_number_element else ""
                        except NoSuchElementException as e:
                            foreign_investor_certificate_number = ""

                        try:
                            also_a_director_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderInd-ExistingRoleYn")
                            also_a_director_element = also_a_director_main_element.find_element(By.CLASS_NAME, "appAttrValue") if also_a_director_main_element else ""
                            also_a_director = also_a_director_element.text.replace("'", "''") if also_a_director_element else ""
                        except NoSuchElementException as e:
                            also_a_director = ""

                        
                        share_holder_dict['meta_detail'] = {
                            "number_of_shares": share_numbers,
                            "also_a_director": also_a_director,
                            "foreign_investor_certificate_number": foreign_investor_certificate_number,
                        } if share_numbers or also_a_director or foreign_investor_certificate_number else {}

                        try:
                            ceased_date_main_element = share_holder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderInd-ceasedDateStandardDelegateBox-ceasedDateBox-CeasedDate")
                            ceased_date_element = ceased_date_main_element.find_element(By.CLASS_NAME, "appAttrValue") if ceased_date_main_element else ""
                            share_holder_dict['termination_date'] = ceased_date_element.text.replace("'", "''") if ceased_date_element else ""
                        except NoSuchElementException as e:
                            share_holder_dict['termination_date'] = ""

                        share_holder_dict['designation'] = "shareholder"

                        people_list.append(share_holder_dict) if share_holder_dict['name'] else ''
            else:
                total_shares = ""
            if forth_span_tag_text == "Directors":
                director_cards = driver.find_elements(By.CLASS_NAME, "Direct")
                get_director_data(director_cards)

            if full_name != "":
                contact_people = dict()
                contact_people['name'] = full_name
                contact_people['phone_number'] = phone
                contact_people['email'] = email
                contact_people['designation'] = "contact_person"
                people_list.append(contact_people) if contact_people['name'] else ''

            if forth_span_tag_text == "Filings":
                pass
            else:
                tabs_div = driver.find_element(By.CLASS_NAME, 'appTabs')
                ul_elements = tabs_div.find_elements(By.TAG_NAME, 'li')
                a_tag = ul_elements[4].find_element(By.TAG_NAME, 'a')
                to_be_executed = a_tag.get_attribute("onclick")
                to_be_executed = to_be_executed[to_be_executed.find('(catHtml'):to_be_executed.find('skip')+6].replace(', me','')
                driver.execute_script(to_be_executed)

            time.sleep(10)
            
            fillings_detail = list()

            filing_cards = driver.find_elements(By.CLASS_NAME, "appRepeaterRowContent")

            if len(filing_cards) > 0:
                for filing_card in filing_cards:
                    if len(filing_card.find_elements(By.CLASS_NAME, "appFilingOpen")) > 0:
                        file_obj = dict()
                        file_name_el = filing_card.find_element(By.CLASS_NAME, "appFilingOpen")
                        file_obj['title'] = file_name_el.find_element(By.TAG_NAME, "span").text.strip().replace("'", "''") if file_name_el else ''
                        submission_el = filing_card.find_element(By.CLASS_NAME, "appFilingSubmitted")
                        registered_date_el = filing_card.find_element(By.CLASS_NAME, "appFilingEnd")
                        file_obj['date'] = registered_date_el.text.strip().replace("'", "''") if registered_date_el else ''
                        file_obj['meta_detail'] ={
                            "submission_date" : submission_el.text.strip().replace("'", "''") if submission_el else ''
                        } if submission_el.text else {}
                        fillings_detail.append(file_obj) if file_obj['title'] else ''
            addresses_detail = []
            if office_address != "" and office_address is not None:
                addresses_detail.append({
                    "address":  office_address.replace("Unknown,", " ").replace("  ", " "),
                    "type": "office_address"
                })
            if postal_address != "" and postal_address is not None:
                addresses_detail.append({
                    "type": "postal_address",
                    "address": postal_address.replace("Unknown,", " ").replace("  ", " ")
                })
            if company_record_address != "":
                addresses_detail.append({
                    "type": "company_records_address",
                    "address": company_record_address
                })
            OBJ = {
                "name": name.strip().replace("'", "''").replace('%','%%'),
                "status": status,
                "registration_number": registration_number,
                "type": company_type,
                "data_name_first_used": data_name_first_used,
                "incorporation_date": incorporation_date,
                "have_own_rule": have_own_rule,
                "industries": industries,
                "filing_month": filing_month,
                "last_filed_date": last_filed_date,
                "removal_reason": removal_reason,
                "removal_date": removal_date,
                "re_registration_date": re_registration_date,
                "total_shares": total_shares,
                "addresses_detail": addresses_detail,
                "people_detail": people_list,
                "fillings_detail": fillings_detail
            }
            
            people_list = list()
            print(OBJ)
            OBJ = _crawler.prepare_data_object(OBJ)
            ENTITY_ID = _crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
            NAME = OBJ['name']
            BIRTH_INCORPORATION_DATE = OBJ['incorporation_date']
            ROW = _crawler.prepare_row_for_db(ENTITY_ID,NAME.replace('%','%%'),BIRTH_INCORPORATION_DATE,OBJ)
            _crawler.insert_record(ROW)

            with open('registration_number.txt', 'a') as file:
                file.write(str(registration_number) + '\n')
                existing_record.append(registration_number)

        driver.back()
        time.sleep(1)

def crawl():

    if len(sys.argv) > 1:
        start_letter = sys.argv[1].lower()
    else:
        start_letter = 'a'

    if start_letter < 'a' or start_letter > 'z':
        print("Invalid start letter. The letter should be from 'a' to 'z'.")
        return False
        
    else:
        alphabet = string.ascii_lowercase[string.ascii_lowercase.index(start_letter):]

    for letter in alphabet:
        print("letter:", letter)
        driver.get("https://www.solomonbusinessregistry.gov.sb/sb-master/relay.html?url=https%3A%2F%2Fwww.solomonbusinessregistry.gov.sb%2Fsb-master%2Fservice%2Fcreate.html%3FtargetAppCode%3Dsb-master%26targetRegisterAppCode%3Dsb-br-companies%26service%3DregisterItemSearch&target=sb-master")
        
        time.sleep(2)
        input_element = driver.find_element(By.ID,"QueryString")
        input_element.send_keys(letter)

        select_element = Select(driver.find_element(By.ID, 'SourceAppCode'))
        select_element.select_by_index(0)
        time.sleep(2)
        search_btn = driver.find_element(By.CLASS_NAME, "appSearchButton")
        search_btn.click()

        time.sleep(3)

        company_tags = driver.find_elements(By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu")

        if len(company_tags) > 0:
            crawl_company_data_by_tags(company_tags, driver)
        
        while True:
            try:
                next_btn = driver.find_element(By.CLASS_NAME, "appNextEnabled")
                next_btn.click()    
                time.sleep(10)
                company_tags = driver.find_elements(By.CLASS_NAME, "registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu")
                if len(company_tags) > 0:
                    crawl_company_data_by_tags(company_tags, driver)
            except NoSuchElementException as e:
                break

    file_paths = ["registration_number.txt"]
    for file_path in file_paths:
        with open(file_path, mode='w') as file:
            file.truncate()
    return SATAUS_CODE,DATA_SIZE, CONTENT_TYPE
   

try:
    SATAUS_CODE,DATA_SIZE, CONTENT_TYPE = crawl()
    _crawler.end_crawler()
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back":"",  "crawler":"HTML"}
    _crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    _crawler.db_log(log_data)
