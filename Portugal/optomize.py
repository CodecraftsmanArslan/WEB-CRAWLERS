from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://portal.oa.pt/advogados/pesquisa-de-advogados/")


element_click = driver.find_element(By.XPATH, "//span[@id='select2-conselho-regional-select-container']")
element_click.click()

time.sleep(5)

drop_down = driver.find_element(By.XPATH, "//span[@class='select2-results']")
options = drop_down.find_elements(By.TAG_NAME, "li")


element_click = True

for index, option in enumerate(options, start=0):
    time.sleep(2)
    if not element_click:  # Check if element_click is False
        element = driver.find_element(By.XPATH, "//span[@id='select2-conselho-regional-select-container']")
        element.click()
        drop_down = driver.find_element(By.XPATH, "//span[@class='select2-results']")
        options = drop_down.find_elements(By.TAG_NAME, "li")
    
    time.sleep(2)
    if index < len(options):
        options[index].click()
        
        element_click = False
        for _ in range(50):
            search_button = driver.find_element(By.XPATH, "//span[text()='Pesquisar']")
            search_button.click()
            while True:
                conn = psycopg2.connect(
                            dbname="postgres",
                            user="postgres",
                            password="airflow",
                            host="localhost",
                            port="5432"
                        )
                cur = conn.cursor()


                cur.execute("""
                    CREATE TABLE IF NOT EXISTS person_data (
                        name TEXT,
                        conselho_regional TEXT,
                        cedula TEXT,
                        localidade TEXT,
                        data_de_inscricao TEXT,
                        status TEXT,
                        email TEXT,
                        telephone TEXT,
                        fax TEXT,
                        morada TEXT,
                        codigo_postal TEXT
                    )
                """)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                person_info=soup.find_all('div',class_='search-results__article-wrapper full-width')
                for person_data in person_info:
                    name = person_data.select_one(".search-results__article-person-title").text
                    status=person_data.select_one(".search-results__article-person-status").text.strip()
                    email = ''  # Initialize email variable before try block
                    href = person_data.find('a')
                    if href is not None:
                        link = href.get('href', '')
                        r1=requests.get(link)
                        soup1=BeautifulSoup(r1.content,"html.parser")
                        email=soup1.select_one('.text-break')
                        if email:
                            email=email.text
                        else:
                            email=''
                   

                    
                    # Define the extract_data function outside the loop
                    def extract_data(soup):
                        data = soup.find_all('div', class_='search-results__article-person-col')
                        trs = []
                        for info in data:
                            tds = info.find_all('ul')
                            table_info = {}
                            for td in tds:
                                lis = td.find_all('li')
                                for d_span in lis:
                                    spans = d_span.find_all('span')
                                    if len(spans) == 2:
                                        key = spans[0].text
                                        value = spans[1].text
                                        table_info[key] = value
                            trs.append(table_info)
                        return trs

                    element_info = extract_data(person_data)
                    for info in element_info:
                        conselho_regional_value = info.get('Conselho Regional', '')
                        cedula_value = info.get('Cédula', '')
                        localidade_value = info.get('Localidade', '')
                        data_de_inscricao_value = info.get('Data de Inscrição', '')
                        morada_value = info.get('Morada', '')
                        codigo_postal_value = info.get('Código Postal', '')
                        telefone_value =info.get('Telefone', '')
                        if telefone_value:
                            telefone_value="+" + telefone_value

                        fax_value =info.get('Fax', '')
                        if fax_value:
                            fax_value="+" + fax_value
                        


                        cur.execute("SELECT name FROM person_data WHERE name = %s", (name,))
                        existing_data = cur.fetchone()
                        if existing_data:
                            print("DATA ALREADY EXISTS")

                        else:
                            sql = """INSERT INTO person_data (name,status, conselho_regional, cedula, localidade, 
                            data_de_inscricao, morada, codigo_postal, telephone, fax,email)
                            VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""

                            data = (name,status ,conselho_regional_value, cedula_value, localidade_value, 
                                    data_de_inscricao_value, morada_value, codigo_postal_value,
                                    telefone_value, fax_value,email)
                            print("DATA INSERTED SUCCESSFULLY")

                            cur.execute(sql, data)
                            conn.commit()
                    
                try:    
                    next_page=driver.find_element(By.CSS_SELECTOR,".icon-chevron-right")
                    next_page.click()
                except:
                    print("No page exsist")
                    break

