# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
# import time,requests
# import pandas as pd
# import os,sys
# from selenium.common.exceptions import TimeoutException
# from captcha import TwoCaptcha

# driver=webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
# driver.get("https://www.lawsociety.bc.ca/lsbc/apps/lkup/mbr-search.cfm?txt_search_type=2&txt_last_nm=aa&txt_given_nm=&txt_city=&member_search=Search&is_submitted=1&results_no=50#results")
# time.sleep(2)

# driver.get("https://www.lawsociety.bc.ca/lsbc/apps/lkup/mbr-details.cfm?encrypted=%2C%27%2A%3F%5B%22%20A%2C%24%5C%3D%3EG%3F%5D%5D%0A")

# link_submit= WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='aalink']")))
# link_submit.click()
# time.sleep(5)


# iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//iframe[@class='panel panel-default']")))
# driver.switch_to.frame(iframe)

# capture_img = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='container']//form//img")))
# capture_img.screenshot('captcha/captcha.png')


# api_key = os.getenv('APIKEY_2CAPTCHA', '6dec9c6113e2dc5c11baaf85452aa0b8')
# solver = TwoCaptcha(api_key)

# try:
#     # Solve CAPTCHA
#     result = solver.normal('captcha/captcha.png')

# # except Exception as e:
# except Exception as e:
#     print("2Captcha API is not working:", e)
# else:
#     print(result)

# driver.switch_to.default_content()







# from bs4 import BeautifulSoup

# with open("data.html","r")as f:
#     outer_html=f.read()

# soup=BeautifulSoup(outer_html,"html.parser")
# table = soup.find_all('div', class_='course-box-content')
# for rows in table:
#     tr = rows.find_all('tr')
#     for trs in tr:
#         tds = trs.find_all('td')
#         if len(tds) == 2:
#             key = tds[0].text.strip()
#             value = tds[1].text.strip()
#             print(f"{key}: {value}")











# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd




# driver=webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
# driver.get("https://portal.oa.pt/advogados/pesquisa-de-advogados/")

# element_click=driver.find_element(By.XPATH,"//span[@id='select2-conselho-regional-select-container']")
# element_click.click()

# time.sleep(5)
# drop_down=driver.find_element(By.XPATH,"//span[@class='select2-results']//li[1]")
# drop_down.click()


# search_button=driver.find_element(By.XPATH,"//span[text()='Pesquisar']")
# search_button.click()





# cur.execute("""
#     CREATE TABLE IF NOT EXISTS person_data (
#         id SERIAL PRIMARY KEY,
#         name TEXT,
#         conselho_regional TEXT,
#         cedula TEXT,
#         localidade TEXT,
#         data_de_inscricao TEXT,
#         morada TEXT,
#         codigo_postal TEXT,
#         telefone TEXT,
#         fax TEXT
#     )
# """)

# soup = BeautifulSoup(driver.page_source, "html.parser")
# person_info=soup.find_all('div',class_='search-results__article-wrapper full-width')
# for person_data in person_info:
#     name = person_data.select_one(".search-results__article-person-title").text
    
#     # Define the extract_data function outside the loop
#     def extract_data(soup):
#         data = soup.find_all('div', class_='search-results__article-person-col')
#         trs = []
#         for info in data:
#             tds = info.find_all('ul')
#             table_info = {}
#             for td in tds:
#                 lis = td.find_all('li')
#                 for d_span in lis:
#                     spans = d_span.find_all('span')
#                     if len(spans) == 2:
#                         key = spans[0].text
#                         value = spans[1].text
#                         table_info[key] = value
#             trs.append(table_info)
#         return trs

#     element_info = extract_data(person_data)
#     for info in element_info:
#         conselho_regional_value = info.get('Conselho Regional', '')
#         cedula_value = info.get('Cédula', '')
#         localidade_value = info.get('Localidade', '')
#         data_de_inscricao_value = info.get('Data de Inscrição', '')
#         morada_value = info.get('Morada', '')
#         codigo_postal_value = info.get('Código Postal', '')
#         telefone_value = info.get('Telefone', '')
#         fax_value = info.get('Fax', '')

#         sql = """INSERT INTO person_data (name, conselho_regional, cedula, localidade, 
#         data_de_inscricao, morada, codigo_postal, telefone, fax)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

#         data = (name, conselho_regional_value, cedula_value, localidade_value, 
#                 data_de_inscricao_value, morada_value, codigo_postal_value, 
#                 telefone_value, fax_value)

#         # Execute the SQL query
#         cur.execute(sql, data)

#         print("Name:", name)
#         print("Conselho Regional:", conselho_regional_value)
#         print("Cédula:", cedula_value)
#         print("Localidade:", localidade_value)
#         print("Data de Inscrição:", data_de_inscricao_value)
#         print("Morada:", morada_value)
#         print("Código Postal:", codigo_postal_value)
#         print("Telefone:", telefone_value)
#         print("Fax:", fax_value)




# import pandas as pd

# # Read the Excel file
# df = pd.read_excel('portugal.xlsx', engine='openpyxl')

# # Convert 'telephone' column to strings and perform the replacement and concatenation
# df['telephone'] =  "+351" + df['telephone'].str.replace('+', '')
# df['fax'] =  "+351" + df['fax'].str.replace('+', '')


# # Save the modified DataFrame to a new Excel file
# df.to_excel('portugal1.xlsx')  # Set index=False to exclude the index column





import pandas as pd

# Read the Excel file
df = pd.read_excel('portugal2.xlsx', engine='openpyxl')

# Function to process phone numbers
def process_phone_number(phone):
    if isinstance(phone, float) and pd.isnull(phone):  # Check if the value is NaN
        return phone
    # Convert to string to handle float values
    phone = str(phone)
    # Remove brackets and hash
    phone = phone.replace('(', '').replace(')', '').replace('-', '').replace('#', '')
    # Check if the phone number contains a semicolon
    if ";" in phone:
        # Split the phone number by semicolon and remove any whitespace
        parts = [part.strip() for part in phone.split(";")]
        # If there are two parts after splitting, concatenate "+351" with both parts and return as multiline string
        if len(parts) == 2:
            part1 = parts[0].replace('+', '')  # Remove existing '+' sign
            part2 = parts[1].replace('+', '')  # Remove existing '+' sign
            return "+351" + part1 + ";" + "+351" + part2
    # If "+351" is not already present, add it to the beginning of the phone number
    elif "+351" not in phone:
        phone = "+351" + phone
    # Replace any existing '+' sign
    return phone.replace('+', '')


df['telephone'] = df['telephone'].apply(process_phone_number)
df['fax'] = df['fax'].apply(process_phone_number)

# Add '+' prefix to phone numbers if '+' is not already present
df['telephone'] = df['telephone'].apply(lambda x: "+" + x if isinstance(x, str) and "+" not in x else x)
df['fax'] = df['fax'].apply(lambda x: "+" + x if isinstance(x, str) and "+" not in x else x)


# Save the modified DataFrame to a new Excel file
df.to_excel('portugal3.xlsx', index=False)  # Set index=False to exclude the index column






















# import requests
# from bs4 import BeautifulSoup
# import pandas as pd


# with open("data.html",'r',encoding='utf-8')as f:
#     outer_html=f.read()


# soup = BeautifulSoup(outer_html, "html.parser")
# person_info=soup.find_all('article',class_='search-results__article-person inactive')
# person_info = soup.find_all('article', class_='search-results__article-person inactive')
# for person_data in person_info:
#     name = person_data.select_one(".search-results__article-person-title").text
    
#     # Define the extract_data function outside the loop
#     def extract_data(soup):
#         data = soup.find_all('div', class_='search-results__article-person-col')
#         trs = []
#         for info in data:
#             tds = info.find_all('ul')
#             table_info = {}
#             for td in tds:
#                 lis = td.find_all('li')
#                 for d_span in lis:
#                     spans = d_span.find_all('span')
#                     if len(spans) == 2:
#                         key = spans[0].text
#                         value = spans[1].text
#                         table_info[key] = value
#             trs.append(table_info)
#         return trs

#     element_info = extract_data(person_data)
#     for info in element_info:
#         conselho_regional_value = info.get('Conselho Regional', '')
#         cedula_value = info.get('Cédula', '')
#         localidade_value = info.get('Localidade', '')
#         data_de_inscricao_value = info.get('Data de Inscrição', '')
#         morada_value = info.get('Morada', '')
#         codigo_postal_value = info.get('Código Postal', '')
#         telefone_value = info.get('Telefone', '')
#         fax_value = info.get('Fax', '')

#         print("Name:", name)
#         print("Conselho Regional:", conselho_regional_value)
#         print("Cédula:", cedula_value)
#         print("Localidade:", localidade_value)
#         print("Data de Inscrição:", data_de_inscricao_value)
#         print("Morada:", morada_value)
#         print("Código Postal:", codigo_postal_value)
#         print("Telefone:", telefone_value)
#         print("Fax:", fax_value)



# for person_data in person_info:
#     name=person_data.select_one(".search-results__article-person-title").text
#     def extract_data(soup):
#         data = soup.find_all('div', class_='search-results__article-person-col')
#         trs=[]
#         for info in data:
#             tds = info.find_all('ul')
#             table_info={}
#             for td in tds:
#                 lis = td.find_all('li')
#                 for d_span in lis:
#                     spans = d_span.find_all('span')
#                     if len(spans) == 2:
#                         key = spans[0].text
#                         value=spans[1].text
#                         table_info[key]=value

#             trs.append(table_info)
#         return trs

#     element_info=extract_data(soup)
#     for info in element_info:
#         conselho_regional_value = info.get('Conselho Regional','')
#         Cédula_value=info.get('Cédula','')
#         localidade_value=info.get('Localidade','')
#         data_de_inscricao_value=info.get('Data de Inscrição','')
#         morada_value=info.get('Morada','')
#         codigo_postal_value=info.get('Código Postal','')
#         telefone_value=info.get('Telefone','')
#         fax_value=info.get('Fax','')

#         print('name',name)
#         print("Conselho Regional:", conselho_regional_value)
#         print("Cédula:", Cédula_value)
#         print("Localidade:", localidade_value)
#         print("Data de Inscrição:", data_de_inscricao_value)
#         print("Morada:", morada_value)
#         print("Código Postal:", codigo_postal_value)
#         print("Telefone:", telefone_value)
#         print("fax:", fax_value)






















