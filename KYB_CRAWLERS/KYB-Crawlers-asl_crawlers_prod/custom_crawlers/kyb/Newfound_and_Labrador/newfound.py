import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE' :'Government website for the province of Newfoundland and Labrador in Canada',
    'COUNTRY' : 'Newfoundland and Labrador',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://cado.eservices.gov.nl.ca/CADOInternet/Company/CompanyNameNumberSearch.aspx", 
                        "Source Description": "The Government website for the province of Newfoundland and Labrador in Canada is the official digital presence of the provincial government. It serves as a comprehensive and authoritative source of information, services, and resources for residents, businesses, and visitors within the province. This website provides valuable insights into the government's policies, programs, and initiatives, covering various sectors, including healthcare, education, transportation, natural resources, and more."},
    'URL' : 'https://cado.eservices.gov.nl.ca/CADOInternet/Company/CompanyNameNumberSearch.aspx',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Newfoundland and Labrador Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'


Newfoundland_and_Labrador = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = Newfoundland_and_Labrador.get_selenium_helper()
driver = selenium_helper.create_driver(headless=True)



arguments = sys.argv
start_num = int(arguments[1]) if len(arguments) > 1 else 0


       

driver.get("https://cado.eservices.gov.nl.ca/CadoInternet/Main.aspx")
time.sleep(5)
registry_select=driver.find_element(By.CSS_SELECTOR,".row li:nth-child(5) a")
registry_select.click()

search_registry=driver.find_element(By.CSS_SELECTOR,"#trCompanySearch a")
search_registry.click()
try:
   
    for file_number in range(start_num,1000000):
        number_enter = driver.find_element(By.CSS_SELECTOR,"input[id='txtCompanyNumber']")
        number_enter.clear()
        number_enter.send_keys(file_number)
        print("number_enter",file_number)
        submit_button=driver.find_element(By.CSS_SELECTOR,"input[id='btnSearch']")
        submit_button.click()

        time.sleep(5)
        no_of_links=len(driver.find_elements(By.CSS_SELECTOR,"#tableSearchResults table table td:nth-child(1)"))
        if no_of_links:

            for i in range(no_of_links)[1:-1]:
                links = driver.find_elements(By.CSS_SELECTOR,"#tableSearchResults table table td:nth-child(1)")
                
                href = links[i].find_element(By.CSS_SELECTOR,"a")
                href.click()
                time.sleep(5)
                registration_date_value=''
                direction_value=''
                mailing_address=''
                st_data=''
                category_value=''
                address_status_value=''

                addresses_detail=[]
                additional_detail=[]
                people_detail=[]
                previous_names_detail=[]

                soup=BeautifulSoup(driver.page_source,"html.parser")
                company_name = soup.find('span', id='lblCompanyName').text
                company_number = soup.find('span', id='lblCompanyNumber').text


                disolve_date = soup.find('span', id='lblStatus')
                state_date = disolve_date.text  

                if re.search(r'\([^)]*\)', state_date):
                    disolve_value = re.search(r'\([^)]*\)', state_date).group(0)
                    disolve_value_cleaned = re.sub(r'[()]', '', disolve_value)
                else:
                    disolve_value_cleaned=''

                status = soup.find('span', id='lblStatus')
                if status is not None:
                    status_value = status.text
                    if "Dissolved" not in status_value:
                        st_data=status_value

                status_info=soup.find('span',id='GoodStandingUC_lblGoodStanding')
                if status_info is not None:
                    status_info_value=status_info.text
                else:
                    status_info_value=''


                category = soup.find('span', id='lblCategory')
                if category:
                    category_value=category.text
                else:
                    category = ""

                Business_type = soup.find('span', id='lblBusinessType').text
                incorporation_jurisdiction = soup.find('span',id='lblIncorporationJurisdiction').text
                filing_type = soup.find('span', id='lblFilingType').text
                registration_date = soup.find('span', id='lblRegistrationDate')
                if registration_date:
                    registration_date_value=registration_date.text
                else:
                    pass

                incorporation_date = soup.find('span', id='lblIncorporationDate').text


                additional_info = soup.find('span', id='lblAddInfo')
                if additional_info:
                    additional_info_value=additional_info.text

                last_annual_return = soup.find('span', id='lblLastAnnualReturn')
                if last_annual_return:
                    last_annual_return_value=last_annual_return.text
                else:
                    pass


                direction = soup.find('span', id='lblMinMaxDirectors')
                if direction:
                    direction_value=direction.text
                else:
                    pass


                mailing_address_element = soup.find('span', {'id': 'lblMailingAddress'})
                if mailing_address_element:
                    # Check the text within the current and previous sibling spans
                    if "Mailing Address:" in mailing_address_element.text or "Mailing Address:" in mailing_address_element.find_previous('span').text:
                        mailing_address = ''
                        for sibling in mailing_address_element.find_next_siblings('span'):
                            mailing_text = sibling.get_text(strip=True)
                            mailing_address += mailing_text 

                        if mailing_address.strip():  # Check if the mailing address is not empty
                            addresses_detail.append({
                                'type': 'mailing_address',
                                'address': mailing_address.strip() # Strip leading/trailing whitespace
                            })





                ro_in_nl = soup.find('span', {'id': 'RegisteredOffice'})
                if  "Registered Office in NL:" in ro_in_nl.text:
                        in_nl_name = ro_in_nl.find_next('span', {'id':'lblLawFirm'})
                        if "No address on file" not in ro_in_nl:
                            in_nl_address1 = ro_in_nl.find_next('span', {'id':'lblROAddress1'}).text
                            in_nl_address2 = ro_in_nl.find_next('span', {'id':'lblROAddress2'}).text
                            in_nl_city = ro_in_nl.find_next('span', {'id':'lblROCity'}).text
                            in_nl_province_state = ro_in_nl.find_next('span',{'id': 'lblROProvinceState'}).text
                            in_nl_country = ro_in_nl.find_next('span', {'id':'lblROCountry'}).text
                            in_nl_postal_zip_code = ro_in_nl.find_next('span',{'id': 'lblROPostalZipCode'}).text
                            addresses_detail.append({
                                'type': 'registered_address',
                                'address':f"{in_nl_address1} {in_nl_address2} {in_nl_city} {in_nl_province_state} {in_nl_country} {in_nl_postal_zip_code}"

                            })
                        if in_nl_name is not None and in_nl_name.text.strip():
                            people_detail.append({
                                'designation': 'registered_agent',
                                'name':in_nl_name.text,
                                'address':f"{in_nl_address1} {in_nl_address2} {in_nl_city} {in_nl_province_state} {in_nl_country} {in_nl_postal_zip_code}"
                            })



                ro_outside_nl = soup.find('span', {'id': 'lblMailingAddress'})
                if "Registered Office outside NL:" in ro_outside_nl.text:
                    outside_nl_contact = ro_outside_nl.find_next('span',{'id': 'lblMAContact'})
                    if "No address on file" not in ro_outside_nl :
                        outside_nl_address1_element = ro_outside_nl.find_next('span', {'id': 'lblMAAddress1'})
                        outside_nl_address2_element = ro_outside_nl.find_next('span', {'id': 'lblMAAddress2'})
                        outside_nl_city_element = ro_outside_nl.find_next('span', {'id': 'lblMACity'})
                        outside_nl_province_state_element = ro_outside_nl.find_next('span', {'id': 'lblMAProvinceState'})
                        outside_nl_country_element = ro_outside_nl.find_next('span', {'id': 'lblMACountry'})
                        outside_nl_postal_zip_code_element = ro_outside_nl.find_next('span', {'id': 'lblMAPostalZipCode'})
                        address_status = ro_outside_nl.find_next('span', {'id': 'lblMAActive'})

                        
                    if outside_nl_contact is not None and outside_nl_contact.text.strip():
                            people_detail.append({
                                'designation': 'registered_agent',
                                'name': outside_nl_contact.text,
                                'address': f"{outside_nl_address1_element.text} {outside_nl_address2_element.text} {outside_nl_city_element.text} {outside_nl_province_state_element.text} {outside_nl_country_element.text} {outside_nl_postal_zip_code_element.text}"
                            })

                    if outside_nl_address1_element:
                        outside_nl_address1 = outside_nl_address1_element.text
                    else:
                        outside_nl_address1 = ''

                    if outside_nl_address2_element:
                        outside_nl_address2 = outside_nl_address2_element.text
                    else:
                        outside_nl_address2 = ''

                    if outside_nl_city_element:
                        outside_nl_city = outside_nl_city_element.text
                    else:
                        outside_nl_city = ''

                    if outside_nl_province_state_element:
                        outside_nl_province_state = outside_nl_province_state_element.text
                    else:
                        outside_nl_province_state = ''

                    if outside_nl_country_element:
                        outside_nl_country = outside_nl_country_element.text
                    else:
                        outside_nl_country = ''

                    if outside_nl_postal_zip_code_element:
                        outside_nl_postal_zip_code = outside_nl_postal_zip_code_element.text
                    else:
                        outside_nl_postal_zip_code = ''

                    if address_status:
                        address_status_value = address_status.text

                    addresses_detail.append({
                        'type': 'outside_address',
                        'address': f"{outside_nl_address1} {outside_nl_address2} {outside_nl_city} {outside_nl_province_state} {outside_nl_country} {outside_nl_postal_zip_code}",
                        'meta_detail': {
                            'address_status': address_status_value
                        }
                    })



                historical_remarks_table = soup.find('table', id='tblHistoricalRemarks')
                if historical_remarks_table:
                    historical_remarks = []
                    rows = historical_remarks_table.find_all('tr')
                    description = ''

                    for row in rows:
                        cell = row.find('td')
                        if cell:
                            text = cell.get_text(strip=True)
                            if "Historical Remarks" not in text:
                                description += " " + text
                    additional_detail.append({
                        'type': 'historical_remarks',
                        'data':[
                            {
                                'description':description.strip(),

                            }
                        ]
                    })




                previuos_table = soup.find('table', {'id': 'tblPreviousCompanyNames'})
                if previuos_table:
                    rows = previuos_table.find_all('tr', {'class': ['row', 'rowalt']})
                    names = []
                    date_changed = []
                    for row in rows:
                        columns = row.find_all('td')
                        if len(columns) == 2:
                            name = columns[0].get_text(separator="\n").strip()
                            date = columns[1].find('span').text
                            names.append(name)
                            date_changed.append(date)
                    for i in range(len(names)):
                        formatted_name = re.sub(r'\s+', ' ', names[i]).strip()
                        previous_names_detail.append({
                            'name': formatted_name,
                            'meta_detail':{
                                'date_changed':date_changed[i],
                            }
                           

                        })

                am_tables = soup.find_all('table', {'id': 'tblAmalgamatedCompanies'})
                for am_table in am_tables:
                    for am_row in am_table.find_all('tr')[1:]:
                        if "From:" in am_row.text:
                            cells = am_row.find_all('td')
                            if len(cells) == 3:
                                am_name = cells[1].get_text(strip=True)
                                am_number = cells[2].get_text(strip=True)
                                additional_detail.append({
                                    'type': 'amalgamated_information',
                                    'data':[{
                                        'amalgamated_from': am_name,
                                        'amalgmation_id':am_number,
                                        }]
                                    })
                        if "Into:" in am_row.text:
                            cells = am_row.find_all('td')
                            if len(cells) == 3:
                                am_name = cells[1].get_text(strip=True)
                                am_number = cells[2].get_text(strip=True)
                                additional_detail.append({
                                    'type': 'amalgamated_information',
                                    'data':[{
                                        'amalgamated_into': am_name,
                                        'amalgmation_id':am_number,
                                        }]
                                    })



                director_table = soup.find('table', {'id': 'tblCurrentDirectors'})
                if director_table:
                    director_rows = director_table.find_all('tr', {'class':['row', 'rowalt']})

                    director_names = []
                    unique_names = set()  # To keep track of unique names

                    for director_row in director_rows[1:]:
                        director_columns = director_row.find_all('td', colspan="2")
                        for director_col in director_columns:
                            director_name = director_col.get_text(strip=True)
                            cleaned_name = director_name.strip()

                            if cleaned_name and cleaned_name.lower() not in unique_names:
                                people_detail.append({
                                    'designation': 'director',
                                    'name':cleaned_name.replace("\n\t\t\t\t\t\t\t\t\t\t", "").replace("\t","")
                                })
                                unique_names.add(cleaned_name.lower())




                OBJ={
                    "name":company_name,
                    "registration_number":company_number,
                    'status':st_data,
                    'dissolution_date':disolve_value_cleaned,
                    "registration_type":category_value,
                    'status_info':status_info_value,
                    "last_annual_return_filed":last_annual_return_value,
                    "business_type":Business_type,
                    "jurisdiction_code":incorporation_jurisdiction,
                    "filing_type":filing_type,
                    "min/max_directors":direction_value,
                    'additional_info':additional_info_value,
                    "incorporation_date":incorporation_date,
                    'registration_date':registration_date_value,
                    "addresses_detail":addresses_detail,
                    "additional_detail":additional_detail,
                    'people_detail':people_detail,
                    'previous_names_detail':previous_names_detail

                }
                OBJ =  Newfoundland_and_Labrador.prepare_data_object(OBJ)
                ENTITY_ID = Newfoundland_and_Labrador.generate_entity_id(company_name=OBJ['name'],reg_number=OBJ['registration_number'])
                NAME = OBJ['name'].replace("%","%%")
                BIRTH_INCORPORATION_DATE = ""
                ROW = Newfoundland_and_Labrador.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                Newfoundland_and_Labrador.insert_record(ROW)


                back_button = driver.find_element(By.ID, 'hylClose')
                back_button.click()
                time.sleep(2)


                number_enter = driver.find_element(By.CSS_SELECTOR,"input[id='txtCompanyNumber']")
                number_enter.clear()
                number_enter.send_keys(str(file_number))

                submit_button=driver.find_element(By.CSS_SELECTOR,"input[id='btnSearch']")
                submit_button.click()

        driver.back()


    Newfoundland_and_Labrador.end_crawler()
    log_data = {"status": "success",
                        "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                        "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    Newfoundland_and_Labrador.db_log(log_data)


except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    Newfoundland_and_Labrador.db_log(log_data)




































