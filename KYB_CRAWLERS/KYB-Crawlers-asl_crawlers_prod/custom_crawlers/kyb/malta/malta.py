"""Import required library"""
import sys, traceback,time,requests
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE' :'Malta Business Registry (MBR)',
    'COUNTRY' : 'Malta',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://registry.mbr.mt/ROC/index.jsp#companySearch.do?action=companyDetails", 
                        "Source Description": "The Malta Business Registry (MBR),  is responsible for the registration of new commercial partnerships and legal entities, the registration of documents related to commercial partnership, the issuing of certified documentation including certificates of good-standing amongst others, the reservation of company names, the collection of registration and other fees, the publication of notices and the imposition and collection of penalties."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://registry.mbr.mt/ROC/index.jsp#companySearch.do?action=companyDetails'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Malta Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

malta_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  malta_crawler.get_requests_helper()
s = malta_crawler.get_requests_session()
arguments = sys.argv
alphabet = str(arguments[1])
start_number = int(arguments[2])
end_number = int(arguments[3])

def extract_data(table):
    data = []
    rows = table.find_all('tr')[1:] 
    current_entry = None

    for row in rows:
        columns = row.find_all(['td', 'th'])
        if len(columns) == 3:
            if current_entry:
                data.append(current_entry)
            input_string = columns[0].get_text(separator=' ', strip=True).replace("\r\n\t\t\t\t\t\t\t\t\t\t\t\t"," ")
            name_parts = input_string.split('Registration No:')
            name = name_parts[0].strip()
            if len(name_parts) > 1:
                registration_no =  name_parts[1].strip()
            else:
                registration_no=""

            address = columns[1].get_text(separator=' ', strip=True)
            current_entry = {'name': name, 'address': address, }

        elif len(columns) == 5 and current_entry:
            share_data = {
                'type': columns[0].get_text(separator=' ', strip=True),
                'class': columns[1].get_text(separator=' ', strip=True),
                'issued_shares': columns[2].get_text(separator=' ', strip=True),
                'paid_up': columns[3].get_text(separator=' ', strip=True),
                'nominal_value_per_share_in_eur': columns[4].get_text(separator=' ', strip=True),
                "registration_no":registration_no
            }
            current_entry['meta_detail'] = share_data

    if current_entry:
        data.append(current_entry)
    return data

def scrape_data():
    for i in range(start_number, end_number+1):
        print("\nCompanyID Number", i)
        
        url = f'https://registry.mbr.mt/ROC/companyDetails.do?companyId={alphabet}+{i}'
        
        response = request_helper.make_request(url)
        try:
            content_string = response.content.decode('utf-8')
        except UnicodeDecodeError:
            content_string = response.content.decode('utf-8', errors='ignore')
            
        if 'The following errors / warnings have been given:' in content_string:
            print("\nNo data available")
            continue

        cookies = response.cookies.get_dict()
        # JSESSIONID = cookies['JSESSIONID']
        
        headers = {
                   "Cookie": f'_ga=GA1.2.1805318058.1693230949; _gid=GA1.2.345070483.1703659622; JSESSIONID=D9103660B43D7BF3B71EF7F32D96952E; _ga_72FBX85Z9S=GS1.2.1703679544.60.0.1703679544.0.0.0',
                   'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
                }
        
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        soup = BeautifulSoup(response.content, 'html.parser')
        detail_tables = soup.select("td.labelLeft")
        
        data_dict={}
        for detail_table in detail_tables:
            head=detail_table.text.strip()
            title = detail_table.find_next("td").text.replace("//", "")
            data_dict[head] = title

        try:
            additional_detail = []
            url1= f"https://registry.mbr.mt/ROC/companyDetailsRO.do?action=authorisedCapital&companyId={alphabet}%20{i}"
            response1 = request_helper.make_request(url1)
            soup2 = BeautifulSoup(response1.text, 'lxml')
            table = soup2.find('table', class_="form-table list-table alternate-rows")
            rows = table.find_all('tr')
            data = []
            for row in rows[1:]:
                cells = row.find_all("td")
                data.append({
                            "authorized_share":cells[0].text.strip(),
                            "share_type":cells[1].text.strip(),
                            "nominal_value_per_share_in_eur":cells[2].text.strip(),
                            "issued_share":cells[3].text.strip()
                        })
            ad_dict = {
                    "type": "share_information",
                    "data":data
            }
            additional_detail.append(ad_dict)

        except Exception as e:
            additional_detail = []

        url2=f"https://registry.mbr.mt/ROC/companyDetailsRO.do?action=involvementList&companyId={alphabet}%20{i}"
        response2 = request_helper.make_request(url2 ,headers = headers)
        soup3 = BeautifulSoup(response2.content, 'html.parser')
        people_detail=[]
        try: 
            # get Directors
            table = soup3.find_all("table", class_="form-table alternate-rows list-table")[0]
            designation = soup3.select('div.heading ')
            direct = designation[0].text.split('s(')[0].strip().lower()
            direct1= designation[1].text.split('s(')[0].strip().lower()
            direct2 = designation[2].text.split('s(')[0].strip().lower()
            direct3 = designation[3].text.split('s(')[0].strip().lower()
            direct4 = designation[4].text.split('s(')[0].strip().lower()
            direct5 = designation[5].text.split('s(')[0].strip().lower()
            for tab in table.find_all("tr"):
                data_elements = tab.find_all("td", class_="bodyLight1")
                if len(data_elements) >= 2:
                    name = data_elements[0].get_text(separator = ' ', strip=True).split("ID")[0]
                    id_part=data_elements[0].text.strip()
                    part_id =  ''
                    if "ID" in id_part:
                        part_id = id_part.split("ID Card:")[1].strip()
                    address = data_elements[1].text.strip()
                    nation=data_elements[2].text.strip()
                    dict1={
                        "designation":direct,
                        "name":name.strip().split("Registration No: ")[0],
                        "nationality":nation,
                        "address":address.replace("\r\n\t\t\t\t\t\t\t\t\t\t\t"," ").replace("\r\n\t\t\t\t\t\t\t\t\t\t"," ").replace('\t','').strip(),
                        "meta_detail":{
                        "id_number":part_id,
                        }
                    }
                    print(dict1)
                    input()
                    people_detail.append(dict1)
                
        except Exception as e:
            dict1={}
            people_detail.append(dict1)
        
        # get Shareholders
        try:
            data = []
            table1 = soup3.find_all("table", class_="form-table alternate-rows list-table")[1]
            
            rows = table1.find_all('tr')[1:] 
            current_entry = None
            for row in rows:
                columns = row.find_all(['td', 'th'])
                if len(columns) == 3:
                    if current_entry:
                        people_detail.append(current_entry)
                    input_string = columns[0].get_text(separator=' ', strip=True).replace("\r\n\t\t\t\t\t\t\t\t\t\t\t\t"," ")
                    name_parts = input_string.split('Registration No:')
                    name = name_parts[0].strip()
                    if len(name_parts) > 1:
                        registration_no =  name_parts[1].strip()
                    else:
                        registration_no=""
                    
                    name_parts_ = input_string.split('ID Card:')
                    if len(name_parts_) > 1:
                        part_id1 =  name_parts_[1].strip()
                    else:
                        part_id1=""

                    address = columns[1].get_text(separator=' ', strip=True)
                    current_entry = {'name': name, 'address': address, "designation":direct1}

                elif len(columns) == 5 and current_entry:
                    share_data = {
                        'type': columns[0].get_text(separator=' ', strip=True),
                        'class': columns[1].get_text(separator=' ', strip=True),
                        'issued_shares': columns[2].get_text(separator=' ', strip=True),
                        'paid_up': columns[3].get_text(separator=' ', strip=True),
                        'nominal_value_per_share_in_eur': columns[4].get_text(separator=' ', strip=True),
                        "registration_no":registration_no,
                        "id_number":part_id1
                    }
                    current_entry['meta_detail'] = share_data
            
            if current_entry:
                people_detail.append(current_entry)
  
        except Exception as e:
            dict2={}
            people_detail.append(dict2)

        try:
            # get Legal Representatives
            table2 = soup3.find_all("table", class_="form-table alternate-rows list-table")[2]
            for tab_2 in table2.find_all("tr"):
                data_elements_2 = tab_2.find_all("td", class_="bodyLight1")
                if len(data_elements_2) >= 2:
                    name2 = data_elements_2[0].get_text(separator = ' ',strip = True).split("ID")[0]
                    
                    id_part2=data_elements_2[0].text.strip()
                    if "ID" in id_part2:
                        part_id2 = id_part2.split("ID Card:")[1].strip()
                    
                    address2 = data_elements_2[1].text.strip()
                    nation2=data_elements_2[2].get_text(separator = ' ',strip = True)
                    dict3={
                        "designation":direct2,
                        "name":name2.strip().split("Registration No: ")[0],
                        "nationality":nation2,
                        "address":address2.replace("\r\n\t\t\t\t\t\t\t\t\t\t\t"," "),
                        "meta_detail":{
                        "id_number":part_id2,
                        }
                    }
                    people_detail.append(dict3)
        except:
            dict3={}
            people_detail.append(dict3)

        try:
            # get  Judicial Representatives
            table3 = soup3.find_all("table", class_="form-table alternate-rows list-table")[3]
            for tab_3 in table3.find_all("tr"):
                data_elements_3 = tab_3.find_all("td", class_="bodyLight1")
                if len(data_elements_3) >= 2:
                    name3 = data_elements_3[0].get_text(separator = ' ',strip = True).split("ID")[0]
                    
                    id_part3=data_elements_3[0].text.strip()
                    if "ID" in id_part3:
                        part_id3 = id_part3.split("ID Card:")[1].strip()
                    address3 = data_elements_3[1].get_text(separator = ' ',strip = True)
                    nation3=data_elements_3[2].get_text(separator = ' ',strip = True)
                    dict4={
                    "designation":direct3,
                        "name":name3.strip().split("Registration No: ")[0],
                        "nationality":nation3,
                        "address":address3.replace("\r\n\t\t\t\t\t\t\t\t\t\t\t"," "),
                        "meta_detail":{
                        "id_number":part_id3,
                        }
                    }
                    people_detail.append(dict4)
        except:
            dict4={}
            people_detail.append(dict4)

        try:
            # get Secretaries
            table4 = soup3.find_all("table", class_="form-table alternate-rows list-table")[4]
            for tab_4 in table4.find_all("tr"):
                data_elements_4 = tab_4.find_all("td", class_="bodyLight1")
                if len(data_elements_4) >= 2:
                    name4 = data_elements_4[0].get_text(separator = ' ',strip = True).split("ID")[0]
                    id_part4=data_elements_4[0].text.strip()
                    part_id4 = ''
                    Registration_no = ''
                    if "ID" in id_part4:
                        part_id4 = id_part4.split("ID Card:")[1].strip()
                    elif "Registration" in id_part4:
                        Registration_no = id_part4.split("Registration No:")[1].strip()

                    address4 = data_elements_4[1].get_text(separator = ' ',strip = True)
                    nation4=data_elements_4[2].get_text(separator = ' ',strip = True)
                    dict5={
                        "designation":direct4,
                        "name":name4.strip().split("Registration No: ")[0],
                        "nationality":nation4,
                        "address":address4.replace("\r\n\t\t\t\t\t\t\t\t\t\t\t"," "),
                        "meta_detail":{
                        "id_number":part_id4,
                        "registration_no":Registration_no
                        }
                    }
                    people_detail.append(dict5)
        except Exception as e:
            dict5={}
            people_detail.append(dict5)

        try:
            # get Auditors
            table5 = soup3.find_all("table", class_="form-table alternate-rows list-table")[5]
            for tab_5 in table5.find_all("tr"):
                data_elements_5 = tab_5.find_all("td", class_="bodyLight1")
                part_id5 = ""
                if len(data_elements_5) >= 2:
                    name5 = data_elements_5[0].get_text(separator = ' ',strip = True).split("ID")[0]
                    name5 = data_elements_5[0].get_text(separator = ' ',strip = True).split("Warrant")[0]
                    try:
                        id_part5=data_elements_5[0].text.strip()
                        if "ID" in id_part5:
                            part_id5 = id_part5.split("ID Card:")[1].strip()
                    except:
                        part_id5 = ""
                    if "Registration" in id_part5:
                        Registration = id_part5.split("Registration No:")[1].strip()
                    address5 = data_elements_5[1].get_text(separator = ' ',strip = True)
                    nation5=data_elements_5[2].get_text(separator = ' ',strip = True)
                    dict6={
                        "designation":direct5,
                        "name":name5.strip().split("Registration No: ")[0],
                        "nationality":nation5,
                        "address":address5.replace("\r\n\t\t\t\t\t\t\t\t\t\t\t"," "),
                        "meta_detail":{
                        "id_number":part_id5,
                        "registration_no":Registration
                        }
                    }
                    people_detail.append(dict6)
        except:
            dict6={}
            people_detail.append(dict6)
        try:
            fillings_detail = []
            if 'Documents' in soup.find(id = 'dropdownMenu1').get_text(separator=' ', strip=True): 
                for page_num in range(0, 880, 10):
                    if page_num%20==0:
                        documentsReport = f"https://registry.mbr.mt/ROC/documentsReport.jsp?action=companyDetails&companyId={alphabet}%20{i}&pager.offset={page_num}"
                        response_url = requests.get(documentsReport, headers=headers)
                        soup_ = BeautifulSoup(response_url.content, 'html.parser')
                        table_ = soup_.find("table", class_="alternate-rows")
                        base_url = 'https://registry.mbr.mt'
                        for row_ in table_.find_all("tr")[1:-1]:
                            tds_ = row_.find_all('td')
                            try:
                                date = tds_[1].text.strip()
                                file_url = base_url + tds_[0].find('a').get('href')
                                title = tds_[2].text.strip()
                                doument_in_file = tds_[3].text.strip().replace('NA', '')
                                document_year = tds_[4].text.strip().replace('NA', '')
                            except:
                                date,file_url, title, document_year, doument_in_file = "", "", "","", ""
                            
                            comp_detail = {
                                "date": date,
                                "title": title,
                                "file_url": file_url,
                                "meta_detail": {
                                    "document_year": document_year,
                                    "doument_in_file":doument_in_file
                                }
                            }
                            
                            fillings_detail.append(comp_detail)
        
        except:
            comp_detail={}
            fillings_detail.append(comp_detail)
        
        OBJ = {
                "registration_number":data_dict.get('Company Registration Number',data_dict.get('Registration Number','')),
                "name":data_dict.get('Company Name',data_dict.get('Name','')),
                "registration_date":data_dict.get('Registration Date',''),
                "addresses_detail":[
                    {
                    "type": "office_address",
                    "address":data_dict.get('Registered Office','')+' '+data_dict.get('City/Locality','').replace("\r\n\t\t\t\t\t\t\t\t\t\t\t"," ").strip()
                    }
                ],
                "jurisdiction":data_dict.get('Country',""),
                "status":data_dict.get('Status',""),
                "effective_date":data_dict.get('Effective Date','').replace('/','-').strip(),
                "additional_detail":additional_detail,
                "people_detail":people_detail,
                "fillings_detail":fillings_detail
            }
        # Filter out dictionaries with 'name': 'Involved Party'
        filtered_data = [entry for entry in OBJ['people_detail'] if entry.get('name') != 'Involved Party']
        # Update the original data with the filtered list
        OBJ['people_detail'] = filtered_data

        OBJ =  malta_crawler.prepare_data_object(OBJ)
        ENTITY_ID = malta_crawler.generate_entity_id(reg_number=OBJ['registration_number'],company_name=OBJ['name'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = ""
        ROW = malta_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        malta_crawler.insert_record(ROW)

    return STATUS_CODE, DATA_SIZE, CONTENT_TYPE

try:
    STATUS_CODE, DATA_SIZE, CONTENT_TYPE = scrape_data()
    malta_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    malta_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    malta_crawler.db_log(log_data)