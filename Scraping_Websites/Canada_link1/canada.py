from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl
import os,sys


def get_driver():
    driver = webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
    return driver 

def extract_data(driver, page):
    url = f'https://www.canadianlawlist.com/searchresult?searchtype=lawyers&province=nl&page={page}'
    print(f"DATA EXTRACTED - PAGE {page}")
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    company_data_list = []
    base_url = "https://www.canadianlawlist.com/"
    trs = soup.find_all('span', class_='searchresult_company_link')
    for tr in trs:
        company_data = {}
        link = f"{base_url}{tr.find('a')['href']}"
        driver.get(link)
        soup_company = BeautifulSoup(driver.page_source, "html.parser")
        try:
            company_data['company_name'] = soup_company.find('span', itemprop='name').text.strip()
        except AttributeError:
            company_data['company_name'] = ''
        
        try:
            address_elements = soup_company.find('div', itemprop='address').find_all('div')
            company_data['street_address'] = address_elements[0].text.strip()
            company_data['city'] = soup_company.find('span', itemprop='addressLocality').text.strip()
            company_data['region'] = soup_company.find('span', itemprop='addressRegion').text.strip()
            company_data['postal_code'] = soup_company.find('span', itemprop='postalCode').text.strip()
        except AttributeError:
            company_data['street_address'] = ''
            company_data['city'] = ''
            company_data['region'] = ''
            company_data['postal_code'] = ''
        
        try:
            phone = soup_company.find('span', itemprop='telephone').text.strip().replace("-", "")
            company_data['phone'] = f"+{phone}"
        except AttributeError:
            company_data['phone'] = ''
        
        try:
            fax = soup_company.find('span', itemprop='faxNumber').text.strip().replace("-", "")
            company_data['fax'] = f"+{fax}"
        except AttributeError:
            company_data['fax'] = ''
        
        try:
            email_span = soup_company.find('span', itemprop='email')
            company_data['email'] = email_span.text.strip() if email_span else ''
        except AttributeError:
            company_data['email'] = ''
        
        company_data_list.append(company_data)
    
    return company_data_list


def save_data(company_data_list):
    file_name = 'canada_all_data.xlsx'
    df = pd.DataFrame(company_data_list)
    try:
        with pd.ExcelWriter(file_name, mode='a', engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        print(f"Data saved to {file_name}")
    except FileNotFoundError:
        df.to_excel(file_name, index=False)
        print(f"Data saved to {file_name}")


arguments = sys.argv
start_num = int(arguments[1]) if len(arguments)>1 else 0

def main():
    driver = get_driver()
    all_data = []
    for i in range(start_num, 63):
        all_data += extract_data(driver, i)
        save_data(all_data)


if __name__ == "__main__":
    main()


