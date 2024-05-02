from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv

url = "https://idx.co.id/id/perusahaan-tercatat/profil-perusahaan-tercatat/"
driver = webdriver.Chrome()
driver.get(url)

time.sleep(10)
# Find elements using the provided XPath
elements = driver.find_elements(By.XPATH, '//*[@id="vgt-table"]/tbody/tr/td[2]/span/a')

# Initialize a list to store href values
href_values = []

# Iterate through the found elements and get the href attribute
for element in elements:
    href = element.get_attribute("href")
    if href:
        href_values.append(href)

# Close the web driver
driver.quit()

# Iterate through the found elements and get the href attribute
# Save the href values to a CSV file
csv_file = 'input/company_urls.csv'
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Href Values"])  # Write header row
    for href in href_values:
        writer.writerow([href])

print(f"Href values saved to {csv_file}")