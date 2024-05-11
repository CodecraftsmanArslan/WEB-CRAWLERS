from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import psycopg2
import time

# Initialize WebDriver

def connection_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="airflow",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    return cur,conn

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    

def  extract_data(driver,cur,conn):
    while True:
        time.sleep(2)
        scroll_to_bottom(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        people_info = soup.find_all('div', class_='card border-primary')
        for info in people_info:
            name = info.find('h5', class_='card-header').text.strip()
            # Extracting the address
            address_lines = info.find_all('p', class_='card-text')[1].find_all('br')
            address = [line.next_sibling.strip() for line in address_lines]
            delimiter = ""
            list_as_string = delimiter.join(address)        
            # Extracting the phone number
            phone_number = info.find('p', text=lambda text: text and '-' in text)
            p_elements_with_dash = "+" + phone_number.text.strip().replace('-','') if phone_number else None
            # Extracting the email address
            email_links = info.find('a', href=lambda href: href and 'mailto:' in href)['href'].replace('mailto:', '')

            cur.execute("INSERT INTO data (name, address, phone_number, email) VALUES (%s, %s, %s, %s)",
                                (name, list_as_string, p_elements_with_dash, email_links))
            conn.commit()
            print("Data inserted successfully")

        try:
            time.sleep(2)
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Next']")))
            next_button.click()
            print('Next Page')
        except:
            print("No Page exsist")
            break

def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get("https://mx.arkbar.com/Attorneys/Arkansas-Find-A-Lawyer")
    time.sleep(2)
    scroll_to_bottom(driver)
    time.sleep(2)
    search_button = driver.find_element(By.XPATH, "//input[@value='Search']")
    search_button.click()
    cur,con=connection_database()
    extract_data(driver,cur,con)


if __name__ == "__main__":
    main()

            
