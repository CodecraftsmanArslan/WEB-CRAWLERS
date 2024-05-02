"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

"""Global Variables"""

meta_data = {
    'SOURCE' :'Ministry of Commerce, Industry, and Labour',
    'COUNTRY' : 'Samoa',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.businessregistries.gov.ws/", 
                        "Source Description": "The Ministry of Commerce, Industry, and Labour (MCIL) in Samoa is a government ministry responsible for the regulation, promotion, and development of commerce, industry, and labor-related matters in Samoa. It is tasked with creating a favorable business environment, supporting economic growth, and ensuring fair labor practices within the country."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.businessregistries.gov.ws/'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Samoa official registry"
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
ARGUMENT = sys.argv

start_page = int(ARGUMENT[1]) if len(ARGUMENT) > 1 else 1

samoa_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = samoa_crawler.get_selenium_helper()

driver = selenium_helper.create_driver(headless=True, Nopecha=False)
action = ActionChains(driver=driver)

def skip_pages():
    for _ in range(start_page - 1):
        next_button = driver.find_element(By.XPATH, '//div[@class="appNext appNextEnabled"]/a')
        action.move_to_element(next_button).click().perform()
        time.sleep(20)


driver.get("https://www.businessregistries.gov.ws/")
time.sleep(5)

def crawl():
    online_service_button = driver.find_element(By.XPATH, '//div[@id = "the_menu_triggers"]/a[@aria-controls="appMainNavigation"]')
    online_service_button.click()
    time.sleep(2)
    companies_button  = driver.find_element(By.XPATH, '//div[@id="appMainNavigation"]//span[text() = "Companies"]')
    companies_button.click()
    time.sleep(2)
    companies_search_button = driver.find_element(By.XPATH, '//div[@id="appMainNavigation"]//span[text() = "Company Search"]')
    companies_search_button.click()
    time.sleep(2)
    search_field = driver.find_element(By.ID, 'QueryString')
    search_field.send_keys("L")
    time.sleep(1)
    appSearchButton=  driver.find_element(By.XPATH, '//span[@class = "appReceiveFocus"][text() = "Search"]')
    appSearchButton.click()
    time.sleep(5)
    page_size = driver.find_element(By.XPATH, '//label[text()="Page size"]/following-sibling::select')
    page_size.click()
    select_option = driver.find_element(By.XPATH, '//option[@value="4"]')
    select_option.click()
    time.sleep(20)
    if start_page > 1:
        skip_pages()
    get_data()

def get_data():
    for i in range(start_page, 12):
        page_number = i
        print(f"Scraping Page No: {page_number}")
        view_details = driver.find_elements(By.CLASS_NAME, 'registerItemSearch-results-page-line-ItemBox-resultLeft-viewMenu')
        scripts = [view_detail.get_attribute('onclick') for view_detail in view_details]
        for script in scripts:
            catCallback = script.split('(')[2]
            aw = script.split('(')[3]
            aw2 = aw.split("==")[0]
            complete_script = catCallback+"("+aw2.replace(", me","")
            time.sleep(2)
            driver.execute_script(complete_script)
            time.sleep(5)
            company_string= driver.find_element(By.XPATH,'/html/body/div/div[1]/div[7]/div/div/div[1]/div/form/div/div/div[1]/div/div/div[1]/div[2]').text.replace("(SAMOA)", "")
            split_string = company_string.split('(')
            NAME = split_string[0].strip()  # Get the company name
            print(f"Scraping data of: {NAME}")
            registration_number = split_string[1].split(')')[0].strip()
            try:
                company_type = driver.find_element(By.CLASS_NAME,'appRestrictedValue-Private').text
                company_type= company_type.split('\n')[-1]
            except NoSuchElementException:
                try:
                    company_type = driver.find_element(By.CLASS_NAME,'appRestrictedValue-Overseas').text
                    company_type= company_type.split('\n')[-1]
                except:
                    company_type = ""

            if len(driver.find_elements(By.CLASS_NAME,'Attribute-Status'))==0:
                continue
            company_status = driver.find_element(By.CLASS_NAME,'Attribute-Status').text
            company_status= company_status.split('\n')[-1]

            incorp_date = driver.find_element(By.CLASS_NAME,'Attribute-RegistrationDate').text
            incorp_date= incorp_date.split('\n')[-1]
            try:
                re_registration_date = driver.find_element(By.CLASS_NAME, 'Attribute-ReregistrationDate').text
                re_registration_date = re_registration_date.split("\n")[-1]
            except NoSuchElementException:
                re_registration_date = ""

            try:
                aliases = driver.find_element(By.CLASS_NAME, 'Attribute-TradingAs').text
                aliases = aliases.split('\n')[-1]
            except NoSuchElementException:
                aliases = ""

            try:
                removal_date = driver.find_element(By.CLASS_NAME,'Attribute-DeregistrationDate').text
                removal_date= removal_date.split('\n')[-1]
            except:
                removal_date=""
                
            try:
                company_rule = driver.find_element(By.CLASS_NAME,'Attribute-CompanyRulesCode').text
                company_rule = company_rule.split('\n')[-1]
            except:
                company_rule = ""

            bus_activity = driver.find_element(By.CLASS_NAME,'Attribute-BusinessSectorCode').text
            bus_activity= bus_activity.split('\n')[-1]
            filing_month = driver.find_element(By.CLASS_NAME,'Attribute-AnnualFilingMonth').text
            filing_month= filing_month.split('\n')[-1]

            try:
                last_filed_date = driver.find_element(By.CLASS_NAME,'Attribute-LatestAnnualFiling').text
                last_filed_date= last_filed_date.split('\n')[-1]
            except:
                last_filed_date=""

            contact_details = driver.find_elements(By.CLASS_NAME,"appChildCount4")   
            for contact_detail in contact_details:
                try:
                    tele_no = contact_detail.find_element(By.CLASS_NAME,'EntityRolePhoneAddresses').text
                    tele_no = tele_no.split('\n')[-1]
                except:
                    tele_no=""
                try:
                    fax_no = contact_detail.find_element(By.CLASS_NAME,'EntityRoleFaxAddresses').text
                    fax_no = fax_no.split('\n')[-1]
                except:
                    fax_no=""
                try:
                    email = contact_detail.find_element(By.CLASS_NAME,'EntityRoleEmailAddresses').text
                    email = email.split('\n')[-1]
                except:
                    email=""
                try:
                    pre_name = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[7]/div/div/div[1]/div/form/div/div/div[1]/div/div/div[5]/div/div/div/div/div[1]/div/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div[2]').text      
                except:
                    pre_name = ''
                try:
                    start_date_ = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[7]/div/div/div[1]/div/form/div/div/div[1]/div/div/div[5]/div/div/div/div/div[1]/div/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div[2]').text
                except:
                    start_date_ = ''
                try:
                    end_date = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[7]/div/div/div[1]/div/form/div/div/div[1]/div/div/div[5]/div/div/div/div/div[1]/div/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div[2]').text
                except:
                    end_date = ''
                
            #Addresses Tab
            if len(driver.find_elements(By.XPATH, '//span[text()="Addresses"]')) > 0:
                addresses_button = driver.find_element(By.XPATH, '//span[text()="Addresses"]')
                action.move_to_element(addresses_button).click().perform()
                time.sleep(5)

                try:
                    office_address = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[7]/div/div/div[1]/div/form/div/div/div[1]/div/div/div[5]/div/div/div/div/div[1]/div/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div[2]')
                    office_address = office_address.text
                except:
                    office_address = ''
                try:
                    office_start_date = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[7]/div/div/div[1]/div/form/div/div/div[1]/div/div/div[5]/div/div/div/div/div[1]/div/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[1]/div/div/div[2]')
                    office_start_date =  office_start_date.text
                except:
                    office_start_date = ''

                try:
                    postal_start_date = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[7]/div/div/div[1]/div/form/div/div/div[1]/div/div/div[5]/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[1]/div/div/div[2]')
                    postal_start_date = postal_start_date.text
                except:
                    postal_start_date = ''
                try:
                    postal_address = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[7]/div/div/div[1]/div/form/div/div/div[1]/div/div/div[5]/div/div/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div[2]')
                    postal_address = postal_address.text
                except:
                    postal_address = ''

                try:
                    service_start_date = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[7]/div/div/div[1]/div/form/div/div/div[1]/div/div/div[5]/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[1]/div/div/div[2]')
                    service_start_date = service_start_date.text
                except:
                    service_start_date = ''
                try:
                    service_address = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[7]/div/div/div[1]/div/form/div/div/div[1]/div/div/div[5]/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div[2]')
                    service_address = service_address.text
                except:
                    service_address = ''

            #Directors Tab
            people_detail = []
            if len(driver.find_elements(By.XPATH, '//span[text()="Directors"]')) > 0:
                director_button = driver.find_element(By.XPATH, '//span[text()="Directors"]')
                action.move_to_element(director_button).click().perform()
                time.sleep(5)
                directors_div = driver.find_element(By.CLASS_NAME,"appRepeaterContent")
                directors = directors_div.find_elements(By.CLASS_NAME, "appRepeaterRowContent")
                for director in directors:
                    try:
                        dir_name = director.find_element(By.CLASS_NAME,'individualName')
                        dir_name = dir_name.text.split('\n')[-1]
                    except:
                        dir_name = ""
                    try:
                        dir_res_address = director.find_element(By.CLASS_NAME,'EntityRolePhysicalAddresses')
                        dir_res_address = dir_res_address.text.split('\n')[-1]
                    except:
                        dir_res_address = ""
                    try:
                        dir_pos_address = director.find_element(By.CLASS_NAME,'EntityRolePostalAddresses')
                        dir_pos_address = dir_pos_address.text.split('\n')[-1]
                    except:
                        dir_pos_address = ""
                    try:
                        dir_consent= director.find_element(By.CLASS_NAME,'appResourceLink')
                        dir_consent = dir_consent.get_attribute('href')
                    except:
                        dir_consent = ""
                    try:
                        dir_appointment_date= director.find_element(By.CLASS_NAME,'Attribute-AppointedDate')
                        dir_appointment_date = dir_appointment_date.text.split('\n')[-1]
                    except:
                        dir_appointment_date = ""
                    if dir_name != "":
                        people_detail.append({
                                "designation":"director",
                                "name":dir_name,
                                "address":dir_res_address,
                                "postal_address":dir_pos_address,
                                "meta_detail":{
                                    "consent":dir_consent,
                                },
                                "appointment_date":dir_appointment_date
                            })
                        
                    if len(driver.find_elements(By.XPATH, '//span[text()="Show Former Directors"]')) > 0:
                        former_director_button = driver.find_element(By.XPATH, '//span[text()="Show Former Directors"]')
                        former_director_button.click()
                        time.sleep(1)
                        former_div = driver.find_element(By.XPATH, '//div[@class="appExpandoChildren"]//div[@class="appRepeaterContent"]')
                        former_directors = former_div.find_elements(By.CLASS_NAME, "appRepeaterRowContent")
                        for f_director in former_directors:
                            if len(f_director.find_elements(By.CLASS_NAME,'individualName'))==0:
                                continue
                            try:
                                f_dir_name = f_director.find_element(By.CLASS_NAME,'individualName')
                                f_dir_name = f_dir_name.text.split('\n')[-1].strip()
                            except NoSuchElementException:
                                f_dir_name = ""
                            try:
                                f_dir_res_address = f_director.find_element(By.CLASS_NAME,'EntityRolePhysicalAddresses').text
                                f_dir_res_address = f_dir_res_address.split('\n')[-1].strip()
                            except NoSuchElementException:
                                f_dir_res_address = ""
                            try:
                                f_dir_pos_address = f_director.find_element(By.CLASS_NAME,'EntityRolePostalAddresses').text
                                f_dir_pos_address = f_dir_pos_address.split('\n')[-1].strip()
                            except NoSuchElementException:
                                f_dir_pos_address = ""
                            try:
                                f_dir_consent= f_director.find_element(By.CLASS_NAME,'appResourceLink')
                                f_dir_consent = f_dir_consent.get_attribute('href')
                            except NoSuchElementException:
                                f_dir_consent = ""
                            try:
                                f_dir_appointment_date= f_director.find_element(By.CLASS_NAME,'Attribute-AppointedDate').text
                                f_dir_appointment_date = f_dir_appointment_date.split('\n')[-1].strip()
                            except NoSuchElementException:
                                f_dir_appointment_date = ""

                            if dir_name != "":
                                people_detail.append({
                                        "designation":"former_director",
                                        "name":f_dir_name,
                                        "address":f_dir_res_address,
                                        "postal_address":f_dir_pos_address,
                                        "meta_detail":{
                                            "consent":f_dir_consent,
                                        },
                                        "appointment_date":f_dir_appointment_date
                                    })
            
            #Shares Tab
            additional_detail = []
            if len(driver.find_elements(By.XPATH, '//span[text()="Shares & Shareholders"]')) > 0:
                shares_button = driver.find_element(By.XPATH, '//span[text()="Shares & Shareholders"]')
                action.move_to_element(shares_button).click().perform()
                time.sleep(5)

                try:
                    total_shares = driver.find_element(By.XPATH, '//span[text()="Total Shares"]/parent::span/parent::div/following-sibling::div')
                    total_shares = total_shares.text
                except:
                    total_shares = ''
                try:
                    extensive_shareholding = driver.find_element(By.XPATH, '//span[text()="Do you have extensive shareholding?"]/parent::span/parent::div/following-sibling::div')
                    extensive_shareholding =  extensive_shareholding.text
                except:
                    extensive_shareholding = ''
                try:
                    more_than_one_class = driver.find_element(By.XPATH, '//span[text()="More than one class of share"]/parent::span/parent::div/following-sibling::div')
                    more_than_one_class = more_than_one_class.text
                except:
                    more_than_one_class = ''

                additional_dict = {
                            "type": "share_information",
                            "data":
                            [
                                {
                                    "total_shares": total_shares,
                                    "extensive_shareholding": extensive_shareholding,
                                    "more_than_one_class": more_than_one_class,
                                }
                            ]
                        }
                if total_shares or extensive_shareholding or more_than_one_class:
                    additional_detail.append(additional_dict)
                
                shareholders = driver.find_elements(By.CLASS_NAME,"Direct")  
                for shareholder in shareholders:
                    try:
                        holder_also_a_director = shareholder.find_element(By.CLASS_NAME,'appRestrictedValue-Y').text
                        holder_also_a_director = holder_also_a_director.split('\n')[-1]
                    except NoSuchElementException:
                        holder_also_a_director=""
                    try:
                        share_numbers_main_element = shareholder.find_element(By.CLASS_NAME, "Attribute-EntityName")
                        share_numbers_element = share_numbers_main_element.find_element(By.CLASS_NAME, "appAttrValue") if share_numbers_main_element else ""
                        holder_name = share_numbers_element.text.replace("'", "''") if share_numbers_element else ""

                        holder_res_address = shareholder.find_element(By.CLASS_NAME,'appPhysicalAddress').text
                        holder_res_address = holder_res_address.split('\n')[-1]

                        holder_appointment_date= shareholder.find_element(By.CLASS_NAME,'Attribute-AppointedDate').text
                        holder_appointment_date = holder_appointment_date.split('\n')[-1]
                        if holder_name != "":
                            people_detail.append({
                                    "designation":"shareholder",
                                    "name":holder_name,
                                    "address":holder_res_address,
                                    "meta_detail":{
                                        "also_a_director":holder_also_a_director,
                                    },
                                    "appointment_date":holder_appointment_date
                                })
                    except NoSuchElementException as e:
                        pass
                        
                    try:
                        share_numbers_main_element = shareholder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderInd-details-shareholderName-individualName")
                        share_numbers_element = share_numbers_main_element.find_element(By.CLASS_NAME, "appAttrValue") if share_numbers_main_element else ""
                        holder_name = share_numbers_element.text.replace("'", "''") if share_numbers_element else ""
                    except NoSuchElementException as e:
                            holder_name = ""

                    holder_res_address = shareholder.find_element(By.CLASS_NAME,'appPhysicalAddress').text
                    holder_res_address = holder_res_address.split('\n')[-1]

                    holder_appointment_date= shareholder.find_element(By.CLASS_NAME,'Attribute-AppointedDate').text
                    holder_appointment_date = holder_appointment_date.split('\n')[-1]
                    if holder_name != "":
                        people_detail.append({
                                "designation":"shareholder",
                                "name":holder_name,
                                "address":holder_res_address,
                                "meta_detail":{
                                    "also_a_director":holder_also_a_director,
                                },
                                "appointment_date":holder_appointment_date
                            })
                        
                if len(driver.find_elements(By.XPATH, '//span[text()="Show Former Shareholders"]')):
                    former_shareholder_button = driver.find_element(By.XPATH, '//span[text()="Show Former Shareholders"]')
                    former_shareholder_button.click()
                    time.sleep(3)

                    former_shareholders_div = driver.find_element(By.XPATH, '//div[@class="appCategory Historic"]//div[@class="appRepeaterContent"]')
                    former_shareholders = former_shareholders_div.find_elements(By.CLASS_NAME, "appRepeaterRowContent")
                    for f_shareholder in former_shareholders:
                        try:
                            f_holder_also_a_director = f_shareholder.find_element(By.CLASS_NAME,'appRestrictedValue-Y').text
                            f_holder_also_a_director = f_holder_also_a_director.split('\n')[-1]
                        except Exception as e:
                            f_holder_also_a_director= ""
                        try:
                            f_share_numbers_main_element = f_shareholder.find_element(By.CLASS_NAME, "Attribute-EntityName")
                            f_share_numbers_element = f_share_numbers_main_element.find_element(By.CLASS_NAME, "appAttrValue") if f_share_numbers_main_element else ""
                            f_holder_name = f_share_numbers_element.text.replace("'", "''").strip() if f_share_numbers_element else ""
                        except Exception as e:
                            f_holder_name = ""

                        f_holder_res_address = f_shareholder.find_element(By.CLASS_NAME,'appPhysicalAddress').text
                        f_holder_res_address = f_holder_res_address.split('\n')[-1]

                        f_holder_appointment_date= f_shareholder.find_element(By.CLASS_NAME,'Attribute-AppointedDate').text
                        f_holder_appointment_date = f_holder_appointment_date.split('\n')[-1]

                        if f_holder_name != "":
                            people_detail.append({
                                    "designation":"former_shareholder",
                                    "name":f_holder_name,
                                    "address":f_holder_res_address,
                                    "meta_detail":{
                                        "also_a_director":f_holder_also_a_director,
                                    },
                                    "appointment_date":f_holder_appointment_date
                                })

                        try:
                            f_share_numbers_main_element = f_shareholder.find_element(By.CLASS_NAME, "brViewLocalCompany-tabsBox-shareholdingTab-shareholding-shareholdersBox-categorizerBox-shareholderRepeater-shareholderSelector-shareholderInd-details-shareholderName-individualName")
                            f_share_numbers_element = f_share_numbers_main_element.find_element(By.CLASS_NAME, "appAttrValue") if f_share_numbers_main_element else ""
                            f_holder_name = f_share_numbers_element.text.replace("'", "''") if f_share_numbers_element else ""
                        except Exception as e:
                            f_holder_name = ""

                        f_holder_res_address = f_shareholder.find_element(By.CLASS_NAME,'appPhysicalAddress').text
                        f_holder_res_address = f_holder_res_address.split('\n')[-1]

                        f_holder_appointment_date= f_shareholder.find_element(By.CLASS_NAME,'Attribute-AppointedDate').text
                        f_holder_appointment_date = f_holder_appointment_date.split('\n')[-1]

                        if f_holder_name != "":
                            people_detail.append({
                                    "designation":"former_shareholder",
                                    "name":f_holder_name,
                                    "address":f_holder_res_address,
                                    "meta_detail":{
                                        "also_a_director":f_holder_also_a_director,
                                    },
                                    "appointment_date":f_holder_appointment_date
                                })

            #Share Parcel Tab
            if len(driver.find_elements(By.XPATH, '//span[text()="Share Parcels"]')) > 0:
                shares_parcel_button = driver.find_element(By.XPATH, '//span[text()="Share Parcels"]')
                action.move_to_element(shares_parcel_button).click().perform()
                time.sleep(10)

                total_shareparcel_details = driver.find_elements(By.CLASS_NAME, 'appRecordOwnershipBundles')
                for total_shareparcel in total_shareparcel_details:
                    try:
                        number_of_shared= total_shareparcel.find_element(By.CLASS_NAME,'Attribute-NumberOfUnits').text
                        number_of_shared = number_of_shared.split('\n')[-1]
                    except:
                        number_of_shared = ""
                    try:
                        share_numbers_main_element = total_shareparcel.find_element(By.CLASS_NAME, "appIndividualname")
                        share_numbers_element = share_numbers_main_element.find_element(By.CLASS_NAME, "appAttrValue") if share_numbers_main_element else ""
                        name_ = share_numbers_element.text.replace("'", "''") if share_numbers_element else ""
                    except NoSuchElementException as e:
                        try:
                            share_numbers_main_element = total_shareparcel.find_element(By.CLASS_NAME, "Attribute-EntityName")
                            share_numbers_element = share_numbers_main_element.find_element(By.CLASS_NAME, "appAttrValue") if share_numbers_main_element else ""
                            name_ = share_numbers_element.text.replace("'", "''") if share_numbers_element else ""
                        except NoSuchElementException as e:
                            name_ = ""
                    if name_ != '':
                        people_detail.append({
                                        "designation":"shareholder",
                                        "meta_detail":{
                                            "number_of_share": number_of_shared,
                                        },
                                        "name":name_
                                    })   
                        
            #Filings Tab
            fillings_detail = []
            if len(driver.find_elements(By.XPATH, '//span[text()="Filings"]')) > 0:
                filing_button = driver.find_element(By.XPATH, '//span[text()="Filings"]')
                action.move_to_element(filing_button).click().perform()
                time.sleep(5)

                filing_elements = driver.find_elements(By.CLASS_NAME, 'appFiling')
                
                for filing_element in filing_elements[1:]:
                    if len(filing_element.find_elements(By.TAG_NAME, 'span')) == 0:
                        continue
                    try:
                        filing_name = filing_element.find_element(By.TAG_NAME, 'span').text
                    except:
                        filing_name = ""
                    try:
                        filing_submitted_date = filing_element.find_element(By.CLASS_NAME, 'appFilingSubmitted').text
                    except:
                        filing_submitted_date = ""
                    try:
                        filing_registered_date = filing_element.find_element(By.CLASS_NAME, 'appFilingEnd').text
                    except:
                        filing_registered_date = ""

                    # Append the details to the list
                    fillings_detail.append({
                        "title": filing_name,
                        "meta-detail": {
                            "submission_date": filing_submitted_date.split(" ")[0],
                        },
                        "date": filing_registered_date.split(" ")[0],
                    })

            OBJ = {
                    "name": NAME,
                    "type": company_type,
                    "status": company_status,
                    "registration_number": registration_number,
                    "incorporation_date": incorp_date,
                    "removal_date": removal_date,
                    "company_rule": company_rule,
                    "industries": bus_activity,
                    "filing_month": filing_month,
                    "last_filed_date": last_filed_date,
                    "re_registration_date": re_registration_date,
                    "aliases": aliases,
                    "previous_names_detail": [
                    {
                        "name": pre_name,
                        "update_date": end_date,
                        "meta_detail":
                        {
                            "start_date": start_date_
                        }
                    }
                ],
                    "additional_detail": additional_detail,
                    "addresses_detail":[
                        {
                            "type": "office_address",
                            "address": office_address,
                            "meta_detail": {
                                "start_date": office_start_date,
                            }  
                        },
                        {
                            "type": "postal_address",
                            "address": postal_address,
                            "meta_detail": {
                            "start_date": postal_start_date
                            }
                        },
                        {
                            "type": "service_address",
                            "address": service_address,
                            "meta_detail": {
                            "start_date": service_start_date
                            }    
                        }
                    ],
                    "contacts_detail":[
                        {
                            "type": "email",
                            "value": email.replace("[Not Provided]","")
                        },
                        {
                            "type": "phone_number",
                            "value": tele_no.replace("[Not Provided]","")
                        },
                        {
                            "type": "fax",
                            "value": fax_no.replace("[Not Provided]","")
                        }
                    ],
                    "people_detail": people_detail,
                    "fillings_detail": fillings_detail
                }
            
            OBJ =  samoa_crawler.prepare_data_object(OBJ)
            ENTITY_ID = samoa_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
            BIRTH_INCORPORATION_DATE = OBJ["incorporation_date"]
            ROW = samoa_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
            samoa_crawler.insert_record(ROW)

            driver.back()
            time.sleep(5)
            pass
    
        next_button = driver.find_element(By.XPATH, '//div[@class="appNext appNextEnabled"]/a')
        action.move_to_element(next_button).click().perform()
        time.sleep(20)

try:
    crawl()
    samoa_crawler.end_crawler()
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    samoa_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    samoa_crawler.db_log(log_data)