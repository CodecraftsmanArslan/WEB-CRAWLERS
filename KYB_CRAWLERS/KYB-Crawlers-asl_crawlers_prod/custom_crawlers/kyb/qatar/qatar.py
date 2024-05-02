"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup

meta_data = {
    'SOURCE': 'Ministry of Commerce and Industry - Qatar Chamber',
    'COUNTRY': 'Qatar',
    'CATEGORY': 'Official Chamber',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://qatarcid.com/",
                      "Source Description": "Established in 1963 by virtue of the Law No (4), Qatar Chamber of Commerce & Industry (QCCI) is one of the oldest chambers in the GCC countries. Its main role  is to organise business interests and represent the Qatari private sector locally and globally as well as support the country’s economic actors and productivity."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://qatarcid.com/'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Qatar Official Chamber"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
ARGUMENTS = sys.argv
LAST_PAGE = 3010
API_URL = "https://qatarcid.com/wp-content/plugins/pointfindercoreelements/includes/pfajaxhandler.php"

start_page = int(ARGUMENTS[1]) if len(ARGUMENTS) > 1 else 1
qatar_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = qatar_crawler.get_requests_helper()

headers = {
  'authority': 'qatarcid.com',
  'path': '/wp-content/plugins/pointfindercoreelements/includes/pfajaxhandler.php',
  'Accept-Encoding': 'gzip, deflate, br',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Origin': 'https://qatarcid.com',
  'Referer': 'https://qatarcid.com/?jobskeyword=&field_company=&field_listingtype=&geolocation=&pointfinder_google_search_coord=&pointfinder_google_search_coord_unit=Mile&pointfinder_radius_search=&ne=&ne2=&sw=&sw2=&CR_NO=&QCCI_MEM_NO=&s=&serialized=1&action=pfs',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest'
}

def get_security_key():
    security_response = request_helper.make_request("https://qatarcid.com/?jobskeyword=&field_company=&field_listingtype=&geolocation=&pointfinder_google_search_coord=&pointfinder_google_search_coord_unit=Mile&pointfinder_radius_search=&ne=&ne2=&sw=&sw2=&CR_NO=&QCCI_MEM_NO=&s=&serialized=1&action=pfs")
    security_data = security_response.text
    soup = BeautifulSoup(security_data, "html.parser")
    script_tag = soup.find('script', id='theme-scriptspf-js-extra')
    script_content = script_tag.contents[0]
    start_index = script_content.find('"pfget_listitems":"') + len('"pfget_listitems":"')
    end_index = script_content.find('"', start_index)
    value = script_content[start_index:end_index]

    return value

def crawl():
    for i in range(start_page, 3011):

        payload = f"action=pfget_listitems&act=search&dt%5Bjobskeyword%5D=&dt%5Bfield_company%5D=&dt%5Bfield_listingtype%5D=&dt%5Bgeolocation%5D=&dt%5Bpointfinder_google_search_coord%5D=&dt%5Bpointfinder_google_search_coord_unit%5D=Mile&dt%5Bpointfinder_radius_search%5D=&dt%5Bne%5D=&dt%5Bne2%5D=&dt%5Bsw%5D=&dt%5Bsw2%5D=&dt%5BCR_NO%5D=&dt%5BQCCI_MEM_NO%5D=&dt%5Bs%5D=&dt%5Bserialized%5D=1&dt%5Baction%5D=pfs&dtx%5B0%5D%5Bname%5D=post_tags&dtx%5B0%5D%5Bvalue%5D=&dtx%5B1%5D%5Bname%5D=pointfinderltypes&dtx%5B1%5D%5Bvalue%5D=&dtx%5B2%5D%5Bname%5D=pointfinderlocations&dtx%5B2%5D%5Bvalue%5D=&dtx%5B3%5D%5Bname%5D=pointfinderconditions&dtx%5B3%5D%5Bvalue%5D=&dtx%5B4%5D%5Bname%5D=pointfinderitypes&dtx%5B4%5D%5Bvalue%5D=&dtx%5B5%5D%5Bname%5D=pointfinderfeatures&dtx%5B5%5D%5Bvalue%5D=&ne=&sw=&ne2=&sw2=&cl=&grid=&pfg_orderby=&pfg_order=&pfg_number=&pfcontainerdiv=.pfsearchresults&pfcontainershow=.pfsearchgridview&page={i}&from=halfmap&security={get_security_key()}&pflat=undefined&pflng=undefined&ohours="

        while True:
            all_company_response = request_helper.make_request(method="POST", url=API_URL, headers=headers, data=payload)
            if not all_company_response:
                print("No data response. Retrying...")
                time.sleep(10)
                continue
            if all_company_response.status_code == 200:
                companies_data = all_company_response.text
                print(f"Scraping Page No: {i}")
                break
            else:
                print(f"Error: {all_company_response.status_code}")
                time.sleep(10)

        soup = BeautifulSoup(companies_data, "html.parser")

        main_list = soup.find("ul", class_="pfitemlists-content-elements pf2col")
        all_list_items = main_list.find_all("li")
        for item in all_list_items:
            item_div = item.find("div", class_="pflist-item-inner")
            if item_div:
                company_link = item_div.find("a").get("href")
                company_response = request_helper.make_request(method="GET", url=company_link)
                company_data = company_response.text

                soup = BeautifulSoup(company_data, "html.parser")

                def find_data(the_string):
                    result = soup.find("span", string=the_string)
                    result = result.find_next_sibling().text.strip() if result else ""
                    return result

                opening_hours_details = []
                contacts_detail = []
                people_detail = []

                company_name = soup.find("h1", {"itemprop": "name"}).text if soup.find("h1", {"itemprop": "name"}) else ""
                listing_type = find_data("Listing Type : ")
                jurisdiction = find_data("Location : ")
                qcci_number = find_data("QCCI Membership Number : ")
                cr_no = find_data("CR Number : ")
                company_type = find_data("Company Type : ")
                address_line_1 = find_data("Address : ")
                p_o_box_number = find_data("PO Box : ")
                complete_address = address_line_1 + ", " + p_o_box_number
                phone_number = find_data("Phone : ")
                fax_number = find_data("Fax : ")
                if phone_number == "0":
                    phone_number = ""
                email = find_data("Email : ")
                website = find_data("Website : ")
                contact_person_phone = find_data("Contact Person Mobile : ")
                contact_person_name = find_data("Contact Person : ")
                if contact_person_name or contact_person_phone:
                    contact_person_dict = {
                            "designation": "authorized_representative",
                            "name": contact_person_name,
                            "phone_number": contact_person_phone
                        }
                    people_detail.append(contact_person_dict)

                owner_name = find_data("Owner Name : ")
                if owner_name:
                    owner_name_dict = {
                            "designation": "owner",
                            "name": owner_name
                        }
                    people_detail.append(owner_name_dict)
                address_location = soup.find("h1", {"itemprop": "name"}).find_next_sibling().text.strip()

                phone_dict = {
                    "type": "phone_number",
                    "value": phone_number
                }
                contacts_detail.append(phone_dict)
                fax_dict = {
                    "type": "fax_number",
                    "value": fax_number
                }
                contacts_detail.append(fax_dict)
                email_dict = {
                    "type": "email",
                    "value": email
                }
                contacts_detail.append(email_dict)
                website_dict = {
                    "type": "website",
                    "value": website
                }
                contacts_detail.append(website_dict)

                #Card Details
                social_div = soup.find("div", class_="pf-itempage-sidebarinfo-social")
                if social_div:
                    all_links = social_div.find_all("a")
                    for link in all_links:
                        the_link = link.get("href")
                        if "facebook" in the_link:
                            facebook_link = the_link
                            facebook_dict = {
                                "type": "facebook",
                                "value": facebook_link
                            }
                            contacts_detail.append(facebook_dict)
                        elif "twitter" in the_link:
                            twitter_link = the_link
                            twitter_dict = {
                                "type": "twitter",
                                "value": twitter_link
                            }
                            contacts_detail.append(twitter_dict)
                        elif "linkedin" in the_link:
                            linkedin_link = the_link
                            linkedin_dict = {
                                "type": "linkedin",
                                "value": linkedin_link
                            }
                            contacts_detail.append(linkedin_dict)

                opening_hours_list = soup.find("div", class_="pf-itempage-ohours").find("ul").find_all("li") if soup.find("div", class_="pf-itempage-ohours") else ""
                if opening_hours_list:
                    for opening_row in opening_hours_list:
                        opening_data = opening_row.find_all("span")
                        opening_day = opening_data[0].text.strip()
                        opening_hours = opening_data[1].text.strip()
                        opening_hours_dict = {
                            "day": opening_day,
                            "working_hours": opening_hours
                        }
                        opening_hours_details.append(opening_hours_dict)
                
                description = soup.find("div", {"itemprop":"description"}).text.replace("\n", "").replace("…", "").replace("..", ".")

                OBJ = {
                    "name": company_name,
                    "registration_number": cr_no,
                    "industries": listing_type,
                    "addresses_detail": [
                        {
                            "type": "general_address",
                            "address": complete_address,
                            "meta_detail": {
                                "location": address_location
                            }
                        }
                    ],
                    "contacts_detail": contacts_detail,
                    "people_detail": people_detail,
                    "additional_detail": [
                        {
                            "type": "opening_hours",
                            "data": opening_hours_details
                        }
                    ],
                    "company_description": description,
                    "type": company_type,
                    "qcci_number": qcci_number,
                    "jurisdiction": jurisdiction
                }

                OBJ = qatar_crawler.prepare_data_object(OBJ)
                ENTITY_ID = qatar_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
                NAME = OBJ['name'].replace("%","%%")
                BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
                ROW = qatar_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
                qatar_crawler.insert_record(ROW)

try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    qatar_crawler.db_log(log_data)
    qatar_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    qatar_crawler.db_log(log_data)

           

