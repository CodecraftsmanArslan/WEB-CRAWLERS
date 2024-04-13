from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://docs.vast.ai/google-colab")

# Get the page source and create a BeautifulSoup object
soup = BeautifulSoup(driver.page_source, "html.parser")

# Extract visible text using get_text() method
all_text = soup.get_text(separator='\n', strip=True)

# Write the text to a file
with open("google_colab.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

