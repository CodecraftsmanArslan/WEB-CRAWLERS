from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import psycopg2




driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
driver.get("https://marketplace.tensordock.com/deploy")

time.sleep(2)
element_click=driver.find_elements(By.CSS_SELECTOR,".gpu-select")
for element in element_click:
    element.click()

    conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="modeltown123",
            host="localhost",
            port="5432"
        )

    cur = conn.cursor()
    create_table_command = """
    CREATE TABLE IF NOT EXISTS server_info (
        id SERIAL PRIMARY KEY,
        location TEXT,
        price TEXT,
        number TEXT,
        type TEXT,
        processor TEXT,
        ram TEXT,
        ssd TEXT,
        uptime TEXT
    );
    """

    cur.execute(create_table_command)
    print("Table is Created")

    time.sleep(7)
    soup=BeautifulSoup(driver.page_source,'html.parser')
    data=soup.find_all('div',class_='row px-4')

    time.sleep(5)
    for row in data:
        infos = row.find_all('div', class_='row')
        for info in infos:
            server_info={}
            body = info.find_all('div', class_='card-body')
            for body_data in body:
                location=body_data.find('h5').text.split(' -')[0]
                price=body_data.find('h5').text.split('-')[1]
                number=body_data.find('p').text.split(',')[0].split('x')[1]
                type=body_data.find('p').text.split(',')[0].split('x')[0]
                processor=body_data.find('p').text.split(',')[1]
                ram=body_data.find('p').text.split(',')[2]
                ssd=body_data.find('p').text.split(',')[3]
                uptime=body_data.find('p').text.split(',')[4]


                server_info['location'] = location
                server_info['price'] = price
                server_info['number'] = number
                server_info['type'] = type
                server_info['processor'] = processor
                server_info['ram'] = ram
                server_info['ssd'] = ssd
                server_info['uptime'] = uptime

                cur.execute(
                    "INSERT INTO server_info (location, price, number, type, processor, ram, ssd, uptime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (server_info['location'], server_info['price'], server_info['number'], server_info['type'], server_info['processor'], server_info['ram'], server_info['ssd'], server_info['uptime'])
                    )
                conn.commit()
                print("DATA INSERTED SUCCESSFULLY")

























