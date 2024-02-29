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







from bs4 import BeautifulSoup

with open("data.html","r")as f:
    outer_html=f.read()

soup=BeautifulSoup(outer_html,"html.parser")
table = soup.find_all('div', class_='course-box-content')
for rows in table:
    tr = rows.find_all('tr')
    for trs in tr:
        tds = trs.find_all('td')
        if len(tds) == 2:
            key = tds[0].text.strip()
            value = tds[1].text.strip()
            print(f"{key}: {value}")


