import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time,os
from bs4 import BeautifulSoup
import pandas as pd



def handle(driver, url):
    driver.get(url)

def extract_data(driver):
    for i in range(ord('q'), ord('z') + 1):
        time.sleep(2)
        letter = chr(i)
        print(f"letter data getting {letter}")
        click_on_button = driver.find_element(By.XPATH, "//div[@class='PanelFieldValue']//input[1]")
        click_on_button.send_keys(letter)

        # Wait for the form to be submitted
        wait = WebDriverWait(driver, 10)  # Wait for a maximum of 10 seconds
        submit = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Search' or @value='Find']")))
        submit.click()        
        
        try:
            last_page=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "thead .AddPaddingLeft")))
            last_page.click()
        except:
            pass


        time.sleep(6)
        info_element=driver.find_element(By.XPATH,"//table[@class='rgMasterTable CaptionTextInvisible']")
        outer_html = info_element.get_attribute("outerHTML")
        time.sleep(2)
        url = "https://hsba.org"
        soup = BeautifulSoup(outer_html, "html.parser")
        data_info=soup.find_all('tr',role='row')
        element_info=[]
        for element in data_info[1:]:
            href_value = element.find('a', href=lambda href: href and '/HSBA/Directory/Directory_results.aspx?' in href)['href']
            full_url = f"{url}{href_value}"
            driver.get(full_url)
            soup2=BeautifulSoup(driver.page_source,"html.parser")
            info=soup2.find_all('div',class_='ReadOnly PanelField Left')
            info_value=dict()
            for data in info:
                trs = data.find_all('div')  
                if len(trs) == 2:
                    key = trs[0].text.strip()
                    value= trs[1].text.strip()

                    info_value[key]=value

            element_info.append(info_value)

        back_to_search=wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='ButtonItem']")))
        back_to_search.click()

        save_data(element_info)


def save_data(element_info):
    file_path="hawaii.xlsx"
    if not os.path.exists(file_path):
        df=pd.DataFrame(element_info)
        df.to_excel(file_path,index=False)
        print("New data append in file")
    else:
        exsist_data=pd.read_excel(file_path,engine='openpyxl')
        new_data=pd.DataFrame(element_info)
        combined_data=exsist_data.append(new_data,ignore_index=True)
        combined_data.to_excel(file_path,index=False)
        print("Data appended to existing Excel file.")


def main():
    url = "https://hsba.org/HSBA_2020/For_the_Public/Find_a_Lawyer/HSBA_2020/Public/Find_a_Lawyer.aspx?hkey=5850e9dd-227b-4556-8ec8-cf8878106f77"
    driver = webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
    handle(driver, url)
    person_info = extract_data(driver)
    save_data(person_info)
    driver.quit()

if __name__ == "__main__":
    main()




