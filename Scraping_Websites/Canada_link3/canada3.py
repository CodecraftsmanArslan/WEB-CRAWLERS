# import requests
# from selenium import webdriver
# from bs4 import BeautifulSoup
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time,re

# driver=webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
# for i in range(ord('a'), ord('z')+1):
#     letter = chr(i)
#     url = f"https://www.lawsociety.bc.ca/lsbc/apps/lkup/mbr-search.cfm?txt_search_type=2&txt_last_nm=a{letter}&txt_given_nm=&txt_city=&member_search=Search&is_submitted=1&results_no=50"
#     driver.get(url)
#     wait = WebDriverWait(driver, 10)

#     while True:
#         soup1=BeautifulSoup(driver.page_source,"html.parser")
#         links=soup1.find_all('td',class_='sorting_1')

#         payload = {}
#         headers = {
#         'Referer': 'https://www.lawsociety.bc.ca/lsbc/apps/lkup/mbr-search.cfm',
#         'Upgrade-Insecure-Requests': '1',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
#         'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
#         'sec-ch-ua-mobile': '?0',
#         'sec-ch-ua-platform': '"Windows"',
#         'Cookie': 'CFID=3675360; CFTOKEN=50282456; JSESSIONID=AC4F9438C4C280E3230DEC67326BC8E4.LawSociety'
#         }

#         for link in links:
#             url=f"https://www.lawsociety.bc.ca/lsbc/apps/lkup/{link.find('a')['href']}"
#             response2 = requests.request("GET", url, headers=headers, data=payload)            
#             soup=BeautifulSoup(response2.content,"html.parser")
#             name=soup.find('h3').text
#             print(name)

#             call_date_div = soup.find('div', string='Current status')
#             if call_date_div is not None:
#                 status = call_date_div.find_next('div').text.strip()
#                 print(status)

#             location_div = soup.find('div', string='Call date')
#             if location_div is not None:
#                 location = location_div.find_next('div').text.strip()
#                 print(location)


#             primary_div = soup.find('div', string='Primary location')
#             if primary_div is not None:
#                     primary = primary_div.find_next('div').text.strip()
#                     print(primary)

#             phone_div = soup.find('div', string='Phone number')
#             if phone_div:
#                 phone_text = phone_div.find_next('div').text.strip()
#                 phone = phone_text.split('[Firm]')[0].strip()
#                 print(phone)

#             fax_div = soup.find('div', string='Fax number')
#             if fax_div:
#                 fax_text = fax_div.find_next('div').text.strip()
#                 fax = fax_text.split('[Firm]')[0].strip()
#                 print(fax)

#             address_div = soup.find('div', string='Contact address')
#             if address_div:
#                 address_text = address_div.find_next_sibling('div').get_text(strip=True, separator='\n')    
#                 unwanted_phrases_pattern = r"\s*\[\s*(?:Show Map|Add to Outlook Contacts|Show QRCode)\s*\]\s*"
#                 address_text = re.sub(unwanted_phrases_pattern, "", address_text).strip()
#                 address_text = re.sub(r'\s+', ' ', address_text)
#                 print(address_text)  # Print processed address text


#         try:
#             next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//li[@class="paginate_button next"]//a')))
#             next_button.click()
#             print("Go to Next Page")
#         except:
#             print("No page exists")
#             break












import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time,re,os,sys
import pandas as pd


# arguments = sys.argv
# start_page = arguments[2] if len(arguments) > 1 else 1



def setup_driver():
    driver = webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
    return driver


def pagination(driver,start_page):
    wait = WebDriverWait(driver, 10)
    for i in range(int(start_page) - 1):  # Convert start_page to integer
        pagination_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//li[@class="paginate_button next"]//a')))
        if i > 0:
            pagination_button.click()
        else:
            print("Pagination not Exist")
            break


def extract_data_from_page(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = soup.find_all('td', class_='sorting_1')
    payload = {}
    headers = {
        'Referer': 'https://www.lawsociety.bc.ca/lsbc/apps/lkup/mbr-search.cfm',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': 'CMSPreferredCulture=en-CA; _ga=GA1.1.937667338.1706388277; nmstat=fcf67239-91e6-20db-7420-8a33c737248f; _cc_id=5b62d9ea3718898ad6935e7485c61283; CFID=3707900; CFTOKEN=73185389; JSESSIONID=AEC417DF857BF502E34C5EB2F67146D5.LawSociety; panoramaId_expiry=1709050175450; panoramaId=a4e7b799825ea8b8abd47a3db19b185ca02c9df2adf5a443ecdd0bcdd23081af; panoramaIdType=panoDevice; CMSCsrfCookie=xCyiQlreEP4X6vr70lvqVqHe0jBpf9ECETZnLTmE; ASP.NET_SessionId=1t451d5akvwcn4kbgulkflvb; _ga_2R6QVEV3E3=GS1.1.1708445374.19.0.1708445391.0.0.0'
    }

    extracted_data = []


    for link in links:
        url = f"https://www.lawsociety.bc.ca/lsbc/apps/lkup/{link.find('a')['href']}"
        response = requests.request("GET", url, headers=headers, data=payload)
        soup = BeautifulSoup(response.content, "html.parser")
        data = {}

        data['name'] = soup.find('h3').get_text(strip=True)

        status = soup.find('div', string='Current status')
        if status:
            data['status'] = status.find_next('div').get_text(strip=True)

        location = soup.find('div', string='Call date')
        if location:
            data['call_date'] = location.find_next('div').get_text(strip=True)

        primary = soup.find('div', string='Primary location')
        if primary:
            data['primary_location'] = primary.find_next('div').get_text(strip=True)

        phone_tag = soup.find('div', string='Phone number')
        if phone_tag:
            phone = phone_tag.find_next('div').get_text(strip=True).split('[Firm]')[0].strip().replace('-', '')
            data['phone_number'] = "+" + phone


        fax = soup.find('div', string='Fax number')
        if fax:
            data['fax_number'] = fax.find_next('div').get_text(strip=True).split('[Firm]')[0].strip()

        address = soup.find('div', string='Contact address')
        if address:
            address_text = address.find_next_sibling('div').get_text(strip=True, separator=' ')
            unwanted_phrases_pattern = r"\s*\[\s*(?:Show Map|Add to Outlook Contacts|Show QRCode)\s*\]\s*"
            address_text = re.sub(unwanted_phrases_pattern, "", address_text).strip()
            data['contact_address'] = re.sub(r'\s+', ' ', address_text)

            print("Extracted data")

        extracted_data.append(data)

    return extracted_data


def save_data(extracted_data):
    file_path = 'canada3.xlsx'
    if not os.path.exists(file_path):
        df = pd.DataFrame(extracted_data)
        df.to_excel(file_path, index=False)
        print("New Excel file created and data appended.")

    else:
        existing_data = pd.read_excel(file_path, engine='openpyxl')
        new_data = pd.DataFrame(extracted_data)
        combined_data = existing_data.append(new_data, ignore_index=True)
        combined_data.to_excel(file_path, index=False)
        print("Data appended to existing Excel file.")


def handle_pagination(driver):
    wait = WebDriverWait(driver, 10)
    while True:
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//li[@class="paginate_button next"]//a')))
            next_button.click()
            print("Go to Next Page")
            extracted_data = extract_data_from_page(driver)  # Capture the returned data
            save_data(extracted_data)

        except:
            print("No page exists")
            break


arguments = sys.argv
start_letter = arguments[1].lower() if len(arguments) > 1 else 'a'
start_num = ord(start_letter)

def main():
    driver = setup_driver()
    for i in range(start_num, ord('z') + 1):
        letter = chr(i)
        url = f"https://www.lawsociety.bc.ca/lsbc/apps/lkup/mbr-search.cfm?txt_search_type=2&txt_last_nm=a{letter}&txt_given_nm=&txt_city=&member_search=Search&is_submitted=1&results_no=50"
        driver.get(url)
        arguments = sys.argv
        start_page = arguments[2] if len(arguments) > 2 else '1' 
        pagination(driver, start_page)
        extracted_data = extract_data_from_page(driver)  # Capture the returned data
        save_data(extracted_data)
        handle_pagination(driver)


# Call the main function
if __name__ == "__main__":
    main()


        

# start from ar page 10

        



        






        # call_date_div = element.find('div', string='Current status')
        # if call_date_div is not None:
        #     status = call_date_div.find_next('div').text.strip()
        #     print(status)
        # location_div = element.find('div', string='Call date')
        # if location_div is not None:
        #     location = location_div.find_next('div').text.strip()
        #     print(location)

















# cookies = {
#     'CMSPreferredCulture': 'en-CA',
#     '_ga': 'GA1.1.937667338.1706388277',
#     'nmstat': 'fcf67239-91e6-20db-7420-8a33c737248f',
#     '_cc_id': '5b62d9ea3718898ad6935e7485c61283',
#     'CFID': '3665628',
#     'CFTOKEN': '64852813',
#     'panoramaId_expiry': '1708285959086',
#     'panoramaId': '181a108f8770e70dc17c8673c0bf185ca02cbc3fc6967e2955f9eadd40cc393b',
#     'panoramaIdType': 'panoDevice',
#     'JSESSIONID': '1D10606ACC88EAE2E7B6FF1EF9A00BBC.LawSociety',
#     'CMSCsrfCookie': 'SaQfQS8l+o7EXaiXRSw4Xl2GBzDPCWIlh49ZcKiY',
#     'ASP.NET_SessionId': '0yjfexahv5aaxcwdwjqgyf1q',
#     '_ga_2R6QVEV3E3': 'GS1.1.1707762289.6.1.1707762708.0.0.0',
# }

# headers = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Cache-Control': 'max-age=0',
#     'Connection': 'keep-alive',
#     # 'Cookie': 'CMSPreferredCulture=en-CA; _ga=GA1.1.937667338.1706388277; nmstat=fcf67239-91e6-20db-7420-8a33c737248f; _cc_id=5b62d9ea3718898ad6935e7485c61283; CFID=3665628; CFTOKEN=64852813; panoramaId_expiry=1708285959086; panoramaId=181a108f8770e70dc17c8673c0bf185ca02cbc3fc6967e2955f9eadd40cc393b; panoramaIdType=panoDevice; JSESSIONID=1D10606ACC88EAE2E7B6FF1EF9A00BBC.LawSociety; CMSCsrfCookie=SaQfQS8l+o7EXaiXRSw4Xl2GBzDPCWIlh49ZcKiY; ASP.NET_SessionId=0yjfexahv5aaxcwdwjqgyf1q; _ga_2R6QVEV3E3=GS1.1.1707762289.6.1.1707762708.0.0.0',
#     'Referer': 'https://www.lawsociety.bc.ca/lsbc/apps/lkup/mbr-search.cfm?txt_search_type=2&txt_last_nm=aa&txt_given_nm=&txt_city=&member_search=Search&is_submitted=1&results_no=50',
#     'Sec-Fetch-Dest': 'document',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-Site': 'same-origin',
#     'Sec-Fetch-User': '?1',
#     'Upgrade-Insecure-Requests': '1',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
#     'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
# }


# params = {
#     'encrypted': ',&*?]#@M,$\\=>G?]]\n',
# }

# response = requests.get(
#     'https://www.lawsociety.bc.ca/lsbc/apps/lkup/mbr-details.cfm',
#     params=params,
#     cookies=cookies,
#     headers=headers,
# )
# print(response.text)