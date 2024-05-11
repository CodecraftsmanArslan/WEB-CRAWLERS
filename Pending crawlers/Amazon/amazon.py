from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time,requests
import pandas as pd
import os,sys
from selenium.common.exceptions import TimeoutException


"""
Important Notice these website has image Captcha I solved it manually sometime image captcha show or some time they will not show
But we can solved it automatically using the Nopecha Service it is paid 
Give any Keyword to (setup_driver_and_search) function they will extract data
"""


def setup_driver_and_search(query):
    """
    Sets up the WebDriver and performs a search on Amazon.

    This function initializes the Chrome WebDriver, navigates to Amazon's homepage,
    enters the provided search query into the search bar, and submits the search.

    Parameters:
    - query (str): The search query to be entered into the search bar.

    Returns:
    - None
    """
    driver = webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
    driver.get("https://www.amazon.com/")
    time.sleep(2)
    search_item = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='twotabsearchtextbox']")))
    search_item.send_keys(query)

    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='nav-search-submit-button']")))
    submit_button.click()

    scrape_amazon_results(driver)


def scrape_amazon_results(driver):
    """
    Scrapes data from Amazon search results.

    This function iterates through each page of search results on Amazon,
    extracts relevant information such as title, brand, price, ASIN,
    and additional item information. It then stores the scraped data
    in a list of dictionaries and appends it to a DataFrame. Finally,
    it clicks on the "Next" button to navigate to the next page of results.

    Parameters:
    - driver: The WebDriver instance.

    Returns:
    - None
    """
    while True:
        time.sleep(5)
        elements = driver.find_elements(By.XPATH, "//div[@class='sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16']")
        element_info = []
        base_url = "https://www.amazon.com"
        
        # Iterate through elements to scrape data
        for element in elements:
            data_info = []
            try:
                title_element = element.find_element(By.CSS_SELECTOR, '.a-color-base.a-text-normal')
                title = title_element.text.strip()
            except:
                title = ""
            
            try:
                data_asin = element.get_attribute("data-asin")
            except:
                data_asin = ""
            
            try:
                price_element = element.find_element(By.XPATH, './/span[@class="a-price"]')
                dollar_amount = price_element.find_element(By.XPATH, './/span[@class="a-price-whole"]').text
                cents_element = price_element.find_element(By.XPATH, './/span[@class="a-price-fraction"]')
                cents = cents_element.text
                formatted_price = f"${dollar_amount}.{cents}"
            except:
                formatted_price = ""
            
            outer_html = element.get_attribute("outerHTML")
            soup = BeautifulSoup(outer_html, "html.parser")
            href = soup.find('a', class_='a-link-normal').get('href')
            link = f"{base_url}{href}"
            response2 = requests.get(link)
            soup2 = BeautifulSoup(response2.content, "html.parser")
            
            try:
                brand = soup2.find('a', id='bylineInfo').text.replace("Visit the", "")
            except:
                brand = ""
            
            try:
                item_info = soup2.find('div', {'id': 'feature-bullets'}).find_all('span', {'class': 'a-list-item'})
                for item in item_info:
                    data_info.append(item.text.strip())
            except:
                pass  # Handle exceptions gracefully, optionally log them
            
            # Store scraped data in a dictionary
            wev = {
                'title': title,
                'brand': brand,
                'price': formatted_price,
                'ASIN': data_asin,
                'item_info': data_info
            }
            print("DATA Extacted")
            element_info.append(wev)
        
        # Convert scraped data to DataFrame and save to CSV
        df = pd.DataFrame(element_info)
        df.to_csv('amazon.csv', mode='a', header=not os.path.exists('amazon.csv'), index=False)
        
        try:
            next_page = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")))
            next_page.click()
            print("Next page")

        except TimeoutException:
            print("No more pages")
            break


# Call the setup_driver_and_search function

"""
Give any keyword you want to extract data they will scrape it 
"""

setup_driver_and_search("Wireless Mechnical Keyboards.")








