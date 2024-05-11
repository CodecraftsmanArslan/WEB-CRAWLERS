from selenium import webdriver
import psycopg2
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time,sys
import requests
import json
from bs4 import BeautifulSoup

arguments = sys.argv
start_num = int(arguments[1]) if len(arguments) > 1 else 0

def connect_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="modeltown123",
        host="localhost",
        port="5432"
    )
    return conn, conn.cursor()

    
def handle_data(driver):
    driver.get("https://www.gabar.org/membersearchresults.cfm?start=1&id=8E04FC88-9BB5-8AFB-CC3F1D4518410447")
    time.sleep(1)
    submit = driver.find_element(By.XPATH, "//input[@type='submit']").click()

def extract_data(driver, conn, cur):
    time.sleep(2)
    for i in range(start_num,70000):
        i=i*25
        url=f"https://www.gabar.org/membersearchresults.cfm?start={i}&id=63494E12-E7C4-004F-9DEB1011BFD2421C"
        driver.get(url)
        links = driver.find_elements(By.XPATH, "//div[@class='member-name']")
        base_url = 'https://www.gabar.org'
        for link in links:
            outer_html = link.get_attribute('outerHTML')
            soup = BeautifulSoup(outer_html, "html.parser")
            url = f"{base_url}{soup.find('a')['href']}"
            response = requests.get(url, verify=False)
            soup2 = BeautifulSoup(response.content, "html.parser")
            table = soup2.find_all('div', class_='course-box-content')

            combined_info = {}

            for rows in table:
                name = soup2.find('div', class_='course-id').find('h3').text
                address_tag = soup2.find('div', class_='course-box').find('p')
                address = address_tag.get_text(separator='\n', strip=True)
                tr = rows.find_all('tr')

                for trs in tr:
                    tds = trs.find_all('td')
                    if len(tds) == 2:
                        key = tds[0].text.strip()
                        value = tds[1].text.strip()
                        combined_info[key] = value  # Add key-value pair to combined_info dictionary

            combined_info_json = json.dumps(combined_info)
            cur.execute("INSERT INTO reports (name, address, person_info) VALUES (%s, %s, %s)", (name, address, combined_info_json))

        conn.commit()

def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    conn, cur = connect_database()
    handle_data(driver)
    extract_data(driver, conn, cur)

if __name__ == "__main__":
    main()




