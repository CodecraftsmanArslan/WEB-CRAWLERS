# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# from selenium import webdriver

# # requests.packages.urllib3.disable_warnings()

# driver = webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")

# driver.get("https://www.gabar.org/membersearchresults.cfm?start=1&id=8E04FC88-9BB5-8AFB-CC3F1D4518410447")
# print("open")



# import requests
# import ssl

# ssl._create_default_https_context = ssl._create_unverified_context


# cookies = {
#     '__utmz': '160797355.1706539435.1.1.utmccn=(direct)|utmcsr=(direct)|utmcmd=(none)',
#     '_ga': 'GA1.1.1571261420.1706539439',
#     'CFID': '225335057',
#     'CFTOKEN': '80131394',
#     '__utma': '160797355.1813025221.1706539435.1706564080.1706628830.6',
#     '__utmb': '160797355',
#     '__utmc': '160797355',
#     '_ga_5XTYQHNL13': 'GS1.1.1706628889.6.1.1706628969.44.0.0',
# }

# headers = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Cache-Control': 'max-age=0',
#     'Connection': 'keep-alive',
#     # 'Cookie': '__utmz=160797355.1706539435.1.1.utmccn=(direct)|utmcsr=(direct)|utmcmd=(none); _ga=GA1.1.1571261420.1706539439; CFID=225335057; CFTOKEN=80131394; __utma=160797355.1813025221.1706539435.1706564080.1706628830.6; __utmb=160797355; __utmc=160797355; _ga_5XTYQHNL13=GS1.1.1706628889.6.1.1706628969.44.0.0',
#     'If-Modified-Since': 'Tue, 30 Jan 2024 10:36:03 GMT',
#     'Referer': 'https://www.gabar.org/membersearchresults.cfm?start=26&id=8E01424A-FE62-532C-EBF5888DDF6A889E',
#     'Sec-Fetch-Dest': 'document',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-Site': 'same-origin',
#     'Sec-Fetch-User': '?1',
#     'Upgrade-Insecure-Requests': '1',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
#     'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
# }

# params = {
#     'start': '1',
#     'id': '8E04FC88-9BB5-8AFB-CC3F1D4518410447',
# }

# response = requests.get('https://www.gabar.org/membersearchresults.cfm', params=params, cookies=cookies, headers=headers)
# print(response)



# response = requests.get("https://www.gabar.org/membersearchresults.cfm?start=1&id=675A0ABA-E286-7F04-C20716A150F36935", verify=False)
# soup=BeautifulSoup(response.content,"html.parser")
# links=soup.find_all('div',class_="member-name")
# base_url="https://www.gabar.org/"

# for link in links:
#     url=f"{base_url}{link.find('a')['href']}"
#     response2=requests.get(url,verify=True)
#     soup2=BeautifulSoup(response2.content,"html.parser")
#     title=soup2.find('div',class_='course-id').text
#     address=soup2.find('div',class_="course-box").find("p").text

#     # //table data

#     tables = soup2.find_all('table')
#     data={}
#     all_info=[]
#     for table in tables:
#         trs = table.find_all('tr')  
#         for tr in trs:
#             tds = tr.find_all('td')
#             if len(tds) == 2:  
#                 key = tds[0].text.strip()
#                 value = tds[1].text.strip()
#                 data[key]=value

#     all_info.append(data)


#     # //dataframe
#     obj = {
#         'title': title,
#         'info': all_info,
#     }
#     print(obj)


            
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd

# def get_soup(url):
#     response = session.get(url, verify=False)
#     return BeautifulSoup(response.content, "html.parser")

# def extract_table_info(table):
#     data = {}
#     for row in table.find_all('tr'):
#         cells = row.find_all('td')
#         if len(cells) == 2:
#             key = cells[0].text.strip()
#             value = cells[1].text.strip()
#             data[key] = value
#     return data

# def extract_member_info(member_link):
#     save_data=[]
#     soup2 = get_soup(member_link)
#     title = soup2.find('div', class_='course-id').text.strip()
#     address = soup2.find('div', class_="course-box").find("p").text.strip()
#     tables = soup2.find_all('table')
#     all_info = [extract_table_info(table) for table in tables]
#     wev={'title': title, 'address': address}
#     for info in all_info:
#         wev.update(info)
#     return wev

# total=1
# for total in range(1,2):
#     session = requests.Session()
#     base_url = "https://www.gabar.org/"
#     search_url = f"{base_url}membersearchresults.cfm?start={total}"
#     total+=25
#     response = session.get(search_url, verify=False)
#     soup = BeautifulSoup(response.content, "html.parser")
#     member_links = [base_url + link.find('a')['href'] for link in soup.find_all('div', class_="member-name")]

#     data = []
#     for member_link in member_links:
#         data.append(extract_member_info(member_link))

#     df = pd.DataFrame(data)
#     df.to_excel("georgea.xlsx")








from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time,requests
from bs4 import BeautifulSoup

driver = webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
driver.get("https://www.gabar.org/membersearchresults.cfm?start=1&id=8E04FC88-9BB5-8AFB-CC3F1D4518410447")
time.sleep(1)
submit=driver.find_element(By.XPATH,"//input[@type='submit']").click()
links=driver.find_elements(By.XPATH,"//div[@class='member-name']")
base_url='https://www.gabar.org'
for link in links:
    outer_html=link.get_attribute('outerHTML')
    soup=BeautifulSoup(outer_html,"html.parser")
    url=f"{base_url}{soup.find('a')['href']}"
    response=requests.get(url,verify=False)
    soup2=BeautifulSoup(response.content,"html.parser")
    table = soup2.find_all('div', class_='course-box-content')
    for rows in table:
        tr = rows.find_all('tr')
        for trs in tr:
            tds = trs.find_all('td')
            if len(tds) == 2:
                key = tds[0].text.strip()
                value = tds[1].text.strip()
                print(f"{key}: {value}")








