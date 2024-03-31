from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd




driver=webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
driver.get("https://portal.oa.pt/advogados/pesquisa-de-advogados/")

element_click=driver.find_element(By.XPATH,"//span[@id='select2-conselho-regional-select-container']")
element_click.click()

time.sleep(5)
drop_down=driver.find_element(By.XPATH,"//span[@class='select2-results']//li[1]")
drop_down.click()


search_button=driver.find_element(By.XPATH,"//span[text()='Pesquisar']")
search_button.click()





cur.execute("""
    CREATE TABLE IF NOT EXISTS person_data (
        id SERIAL PRIMARY KEY,
        name TEXT,
        conselho_regional TEXT,
        cedula TEXT,
        localidade TEXT,
        data_de_inscricao TEXT,
        morada TEXT,
        codigo_postal TEXT,
        telefone TEXT,
        fax TEXT
    )
""")

soup = BeautifulSoup(driver.page_source, "html.parser")
person_info=soup.find_all('div',class_='search-results__article-wrapper full-width')
for person_data in person_info:
    name = person_data.select_one(".search-results__article-person-title").text
    
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
        telefone_value = info.get('Telefone', '')
        fax_value = info.get('Fax', '')

        sql = """INSERT INTO person_data (name, conselho_regional, cedula, localidade, 
        data_de_inscricao, morada, codigo_postal, telefone, fax)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        data = (name, conselho_regional_value, cedula_value, localidade_value, 
                data_de_inscricao_value, morada_value, codigo_postal_value, 
                telefone_value, fax_value)

        # Execute the SQL query
        cur.execute(sql, data)

        print("Name:", name)
        print("Conselho Regional:", conselho_regional_value)
        print("Cédula:", cedula_value)
        print("Localidade:", localidade_value)
        print("Data de Inscrição:", data_de_inscricao_value)
        print("Morada:", morada_value)
        print("Código Postal:", codigo_postal_value)
        print("Telefone:", telefone_value)
        print("Fax:", fax_value)