# import pandas as pd

# df = pd.read_excel("portugal3.xlsx",engine='openpyxl')

# def remove_spaces(phone_number):
#     return phone_number.replace(" ", "")

# df['telephone']  = df['telephone'].apply(lambda x: remove_spaces(x) if isinstance(x, str) else x)
# df['fax']=df['fax'].apply(lambda x: remove_spaces(x) if isinstance(x, str) else x)

# df.to_excel('portugal4.xlsx')



# import pandas as pd

# # Read the Excel file
# df = pd.read_csv("server_info.csv")
# # df[['number', 'type']] = df['type'].str.split(n=1, expand=True)
# df.to_excel("tensordock.xlsx", index=False)









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
driver.get("https://www.linkedin.com/home")
time.sleep(2)

login=driver.find_element(By.XPATH,'//input[@id="session_key"]')
login.send_keys('farirs50@gmail.com')
password=driver.find_element(By.XPATH,'//input[@id="session_password"]')
password.send_keys('wgiryrat1')
submit=driver.find_element(By.XPATH,'//button[@type="submit"]')
submit.click()
time.sleep(1)
print("opend website")
job_click=driver.find_element(By.XPATH,'//span[@title="Jobs"]')
job_click.click()
time.sleep(2)
print('Click on job Button')
search_element=driver.find_element(By.XPATH,'//input[@class="jobs-search-box__text-input jobs-search-box__keyboard-text-input"]')
search_element.send_keys('web scraping')
search_element.send_keys(Keys.RETURN)  # Pressing Enter key
time.sleep(5)
print("Job is Search")