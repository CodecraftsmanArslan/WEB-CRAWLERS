from selenium import webdriver
import psycopg2
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time,sys
import requests,re
import json
from bs4 import BeautifulSoup



driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


driver.get('https://members.ctbar.org/searchserver/people2.aspx?id=C5CEEC4B-7451-4A0F-8C2D-73B127BF275E&cdbid=&canconnect=0&canmessage=0&map=True&clientId=71977&view=tile&sort=NameAsc&map_displayed=True&sd=OUlmYz3F6OCBxSq3%2B9RVhcEoC3E36HPfnB0gGvk1eZmMN8z21etI4D35IEbS88gA&cv=KCpeycZoFKeyrxKExwD%2FRw%3D%3D&callback=SaveSearchResultsPrefs&hhSearchTerms=')
time.sleep(5)
soup1=BeautifulSoup(driver.page_source,"html.parser")
links=soup1.find_all('p',class_='name')
base_url='https://members.ctbar.org'
for link in links:
    url=f"{base_url}{link.find('a')['href']}"
    driver.get(url)
    time.sleep(2)
    soup=BeautifulSoup(driver.page_source,"html.parser")
    name=soup.select_one("b.big").text
    try:
        status = soup.select_one("b.big").find_next_sibling("br").find_next_sibling(string=True).strip()
    except AttributeError:
        status = None

    # Extract email
    b_tag = soup.find('b', class_='big')
    mail = b_tag.find_next_sibling('a')['href'].replace('mailto:', '') if b_tag and b_tag.find_next_sibling('a') else None

    # Extract phone

    phone_text = soup.select_one("td#tdWorkPhone").get_text(strip=True)
    primary_phone = re.match(r'(\d{3} \d{3}-\d{4})', phone_text)
    primary_phone = primary_phone.group(1) if primary_phone else None


    # Extract address
    address = soup.find('td', id='tdEmployerName')
    address_text = re.sub(r'\s+', ' ', address.text.strip()).replace(' [ Map ]', '') if address else None

    # Handle fax and website
    try:
        fax = soup.select_one("td#tdWorkPhone span:contains('(Phone)')").find_next_sibling(string=True).strip()
    except AttributeError:
        fax = None

    try:
        website = soup.select_one("td#tdWorkPhone a")['href']
    except (AttributeError, TypeError):
        website = None

    # Output the extracted data
    print("Name:",name)
    print("Status:", status)
    print("Email:", mail)
    print("Phone:", primary_phone)
    print("Address:", address_text)
    print("Fax:", fax)
    print("Website:", website)
