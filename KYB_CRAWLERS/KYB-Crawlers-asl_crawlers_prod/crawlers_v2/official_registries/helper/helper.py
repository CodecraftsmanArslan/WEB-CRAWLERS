"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import time , httpx , asyncio
from dateutil import parser
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from helpers.crawlers_helper_func import CrawlersFunctions

crawlers_functions = CrawlersFunctions()

#Description
# The `skip_pages` function is designed to facilitate web automation by allowing the program to skip a specified number of pages on a website. It takes a Selenium WebDriver (`browser`) as an argument and looks for a "next" button on the web page. If a start number is provided as a command-line argument, the function clicks the "next" button the specified number of times, pausing for 10 seconds between each click. This function is useful for navigating through multiple pages of a website and is part of a web scraping or automation script.

def skip_pages(browser):
    start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if start_number != 0:
        for i in range(start_number):
            try:
                time.sleep(10)
                print("Skipping page number: ", i+1)
                next_button = browser.find_element(
                    By.XPATH, '/html/body/app/div[2]/div[2]/div/div/div/div[4]/div[1]/nav[1]/ul/li[4]/a')
                next_button.click()
            except WebDriverException:
                print("WebDriverException occurred while skipping page")
    return start_number



def timestamp_to_str(timestamp):
    try:
        datetime_obj = parser.parse(timestamp)
        return datetime_obj.strftime("%m-%d-%Y")
    except Exception as e:
        return ""
    
async def make_request(url, method="GET" , headers={} ,payload=None, timeout=10, retry_interval=60):
    async with httpx.AsyncClient() as client:
        while True:
            try:
                if(method == 'POST'):
                    response = await client.request(method ,url, json=payload, headers=headers, timeout=timeout)
                    print(response.status_code, 'status_code_post')
                else:
                    response = await client.request(method , url , headers=headers, timeout=timeout)
                    print(response.status_code, 'status_code_get')
                if response or response.status_code == 200 or response.status_code == 500:
                    return response
            except Exception as e:
                print(f"Error while making a request: {e}. Retrying in {retry_interval} seconds")
                await asyncio.sleep(retry_interval)

async def make_request_with_retry(url, method , headers={} , payload=None):
    while True:
        response = await make_request(url, method, headers ,payload)
        if response :
            return response