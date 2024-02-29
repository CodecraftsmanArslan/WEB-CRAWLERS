from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os


driver = webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
driver.get("https://members.alabar.org/member_portal/member-search")
wait = WebDriverWait(driver, 10)  # Wait for up to 10 seconds


for i in range(1, 84):
    # Click on the search field

    time.sleep(2)
    button = driver.find_element(By.XPATH, "//li[@class='search-field']")
    button.click()

    time.sleep(2)
    select_element = driver.find_element(By.XPATH, f"//li[@class='active-result'][{i}]")
    select_element.click()

    time.sleep(2)
    # Click on the submit button
    submit_element = driver.find_element(By.XPATH, "//input[@class=' TextButton']")
    submit_element.click()


    page_number = 0
    file_exists = os.path.exists("filtered.csv")
    names_set = set()  # Initialize an empty set to store unique names
    
    try:
        while True:
            # Wait for the table to be present
            data = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table[@class='rgMasterTable CaptionTextInvisible']")))
            outer_html = data.get_attribute("outerHTML")

            time.sleep(2)
            # Create BeautifulSoup object from the outer HTML content
            soup = BeautifulSoup(outer_html, "html.parser")
            rows = soup.find_all('div', class_='col-md-4 col-sm-6')
            filtered_text = []
            for row in rows:
                person_info = {}  # Create a new dictionary for each person
                for text in row.stripped_strings:
                    title = row.find('h3').text
                    person_info['name'] = title

                    email = row.find('a', href=lambda href: href and 'mailto:' in href)
                    if email:
                        person_info['email'] = email.text
                    else:
                        person_info['email'] = None

                    following_text = row.find('h3').find_next_sibling(text=True).strip()
                    person_info['status'] = following_text
                    if "Date " in text:
                        person_info['date'] = text.replace("Date Admitted:","")

                    if "(" in text:
                        person_info['phone'] = '+' + text.replace('(', '').replace(')', '')

                name = person_info.get('name')
                if name not in names_set:
                    filtered_text.append(person_info)
                    names_set.add(name)

            df = pd.DataFrame(filtered_text)
            print(df)

            if not file_exists:  # Check if file exists before writing the header
                df.to_csv("filtered.csv", index=False, mode='a', header=True)
                file_exists = True  # Set flag to indicate that the file exists
            else:
                df.to_csv("filtered.csv", index=False, mode='a', header=False)  # Append data without header

            print("------------------------------------")

            time.sleep(2)
            next_page = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@class="rgPageNext"]')))
            next_page.click()
            page_number += 1

            if page_number == 4:
                break

        time.sleep(2)
        search_close = driver.find_element(By.XPATH, '//a[@class="search-choice-close"]')
        search_close.click()

    except:
        time.sleep(2)
        search_close = driver.find_element(By.XPATH, '//a[@class="search-choice-close"]')
        search_close.click()









































































