from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time,sys,requests,json
import psycopg2
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
time.sleep(2)
driver.get("http://www.advokatnoeglen.dk/sog.aspx?s=1&t=0&c=")
driver.maximize_window()


popup=driver.find_element(By.XPATH,'//a[@id="CybotCookiebotDialogBodyLevelButtonAccept"]')
popup.click()

def click_button(driver):
    element_click = driver.find_element(By.XPATH, "//select[@id='Search_CourtSelect']")
    element_click.click()

# Assuming 'driver' is already initialized

select_element = driver.find_element(By.XPATH, "//select[@id='Search_CourtSelect']")
options = select_element.find_elements(By.TAG_NAME, "option")

# Loop through each option starting from the second one
for index, option in enumerate(options[14:], start=14):
    select_element = driver.find_element(By.XPATH, "//select[@id='Search_CourtSelect']")
    options = select_element.find_elements(By.TAG_NAME, "option")
    print("STARTING  GETTING DATA ")
    click_button(driver)
    if index < len(options):
        options[index].click()
        
        # Click the search button
        button = driver.find_element(By.XPATH, "//input[@id='searchButton']")
        button.click()


        time.sleep(2)
        base_url='http://www.advokatnoeglen.dk'


        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="airflow",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS ScrapedData (
                            person_name TEXT,
                            status TEXT,
                            appointment TEXT,
                            company_info jsonb
                        )''')

        # Your scraping logic
        while True:

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            trs = soup.find_all('tr', onclick=lambda value: value and 'location.href' in value)

            for tr in trs:
                onclick_values = tr.get('onclick').replace('location.href=', '').replace(",", "").replace("'", "")
                url = f"{base_url}{onclick_values}"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")
            
                person_name = soup.find('div', attrs={'style': 'border-top:1px solid #e7e7e7;border-bottom:1px solid #e7e7e7;padding-top:16px;padding-bottom:14px;margin-bottom:25px;margin-top:20px'}).find('h1').text
                status = soup.find('div', attrs={'style': 'border-top:1px solid #e7e7e7;border-bottom:1px solid #e7e7e7;padding-top:16px;padding-bottom:14px;margin-bottom:25px;margin-top:20px'}).find('h2').text
                appointment_tags = soup.find(lambda tag: tag.name == 'p' and 'Beskikkelsesår:' in tag.text).text.strip().replace('Beskikkelsesår:','').split('  ')[0]

                
                div_data = soup.find_all('div', attrs={'style': 'background: #f4f4f4; margin-top: 15px; width: 360px; padding: 11px 11px 0px 11px; position: relative'})
                company_info=[]
                for element_info in div_data:
                    company = element_info.find('h2').text.strip()
                    tel = element_info.find(lambda tag: tag.name == 'p' and 'Tlf.' in tag.text).text.strip().replace('Tlf.','').split('\n ')[0].replace('\r','')
                    telephone="+" + tel.replace(":",'')

                    font_tags = element_info.select('div[style="background: #f4f4f4; margin-top: 15px; width: 360px; padding: 11px 11px 0px 11px; position: relative"] p:nth-of-type(1) ')
                    address = [address.text.strip() for address in font_tags]
                    address = [line.replace(' ', '') for line in address]
                    address_line=''
                    full_address = address_line.join(address).replace('\n',' ').replace('\r',' ')
                    
                    person_data = {
                        'company': company,
                        'address': full_address,
                        'telephone': telephone,
                        }
                    company_info.append(person_data)
                    
                    person_data_json = json.dumps(company_info)
                    
                cursor.execute('''INSERT INTO ScrapedData (person_name,status,appointment,company_info)
                                    VALUES (%s, %s, %s,%s)''', (person_name, status,appointment_tags,person_data_json))
                
                conn.commit()



            try:
                next_page = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='next']")))
                if next_page:
                    next_page.click()
            except:
                print("No page avaliable")
                break

































