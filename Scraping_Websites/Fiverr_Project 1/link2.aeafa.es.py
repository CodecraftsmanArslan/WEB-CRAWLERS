import requests
import pandas as pd
from bs4 import BeautifulSoup
from unicodedata import normalize
import re

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 2000)
pd.set_option('display.max_colwidth', 200)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
}

page = 1
data1 = []
data2 = []

while True:
    print(f"Page {page}")
    r = requests.get(f"https://www.aeafa.es/asociados.php?provinput=&_pagi_pg={page}", headers=headers)
    page += 1
    
    soup = BeautifulSoup(r.content, "lxml")
    
    for pro in soup.find_all("div", class_="col-md-8 col-sm-8"):
        values = [re.sub(r'\s+', ' ', normalize('NFKD', p.get_text(strip=True))) for p in pro.find_all("p")]
        row = {'Sobre' : values[0][6:]}     # skip over the word Sobre
        
        for item in values[2:]:
            key, value = item.split(':', 1)
            row[key.strip()] = value.strip()
        
        row['Teléfono'] = row['Teléfono'].replace(".", "")
        data1.append(row)

    details = soup.find("table", class_="table").tbody
    
    for tr in details.find_all("tr"):
        data2.append([re.sub(r'\s+', ' ', normalize('NFKD', td.get_text(strip=True))) for td in tr.find_all("td")[:-1]])
        
    # Any more?
    ul = soup.find("ul", class_="pagination")
    last_li = ul.find_all("li")[-1]
    
    if last_li.text != "»":
        break

# Merge the name and surname from the second table
data = []

for d1, d2 in zip(data1, data2):
    data.append({'Nombre' : d2[0], 'Apellidos' : d2[1]} | d1)

df = pd.DataFrame(data)
df.to_csv('read.csv')
        