from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time,sys
import psycopg2
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException




def handle_page(driver):
    select_option=driver.find_element(By.XPATH,"//select[@id='city_id']")
    select_option.click()

def database_conn():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="airflow",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    return cur,conn

def extract_data(cur,conn,driver):
    element_option=driver.find_elements(By.XPATH,'//option')
    for option in element_option:
        options=option.find_element(By.XPATH,'//option')
        option.click()
        time.sleep(2)
        info=driver.find_element(By.XPATH,'//button[@id="btnFilter"]')
        info.click()
        while True:
            element_html=driver.find_element(By.XPATH,'//div[@class="table-responsive"]')
            outer_html=element_html.get_attribute('outerHTML')
            soup = BeautifulSoup(outer_html, "html.parser")
            data_rows = soup.select("#tblLawyer tbody tr")  # Select all rows in tbody

            # Find the index of the columns
            headers = [th.text.strip() for th in soup.select("#tblLawyer thead tr td")]
            indices = {header: index for index, header in enumerate(headers)}

            # Iterate through all data rows and print the values corresponding to each column
            for row in data_rows:
                reg_id = row.find_all('td')[indices['Reg. ID.']].text.strip()
                name = row.find_all('td')[indices['Name']].text.strip()
                office_address = row.find_all('td')[indices['Office Address']].text.strip()
                office_phone = row.find_all('td')[indices['Office Phone']].text.strip()
                mobile = row.find_all('td')[indices['Mobile']].text.strip()
                email = row.find_all('td')[indices['Email']].text.strip()
                website = row.find_all('td')[indices['Website']].text.strip()
                city = row.find_all('td')[indices['City']].text.strip()
                cur.execute("INSERT INTO translate (reg_id, name, office_address, office_phone, mobile, email, website, city) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (reg_id, name, office_address, office_phone, mobile, email, website, city))
                conn.commit()
                print("Data inserted successfully")


            time.sleep(5)
            button = soup.find('table', id='tblLawyer').find('tbody')
            # Check if a <td> element exists within the <tbody>
            if button.find('td'):
                element_button = button.find('td').text.strip()

                if 'No record Found' not in element_button:
                    # Apply WebDriverWait to find the Next button
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))
                    )
                    next_button.click()
                    print('Next Page')
                else:
                    print("NO page Exist")
                    break
            
            else:
                print("No <td> element found within the <tbody>")


   
def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://pakistanlawyer.com/findlawyer/")
    handle_page(driver)
    cur,conn=database_conn()
    extract_data(cur,conn,driver)


if __name__ == "__main__":
    main()






