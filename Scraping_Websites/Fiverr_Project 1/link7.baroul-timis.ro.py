import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

url = "https://baroul-timis.ro/get-av-data?param=toti-avocatii"
base_url= 'https://baroul-timis.ro'

headers ={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}

test = []

def process(link):
    wev={}
    r =requests.get(link,headers=headers)
    soup=BeautifulSoup(r.content, 'lxml')
    prod=soup.find_all('div',class_='user-info text-left mb-50')
    for pip in prod:
        title=pip.find('h4').text
        wev['title']=title
        try:
            phone=pip.select('span',class_='font-weight-bolder')[2].text
            
        except:
            pass
        wev['phone']=phone.strip()
        wev['phone']=phone[5:]
     
        try:
            email=pip.select('span',class_='font-weight-bolder')[3].text.split()[-1]
        except:
            pass
        wev['email']=email
        test.append(wev)
        
        
        table=soup.find_all('table',class_='table')
    
        for t in table:
            for head in t.find_all('tr'):
                dd=head.select('td')[0].text  
                dt=head.select('td')[1].text.strip()
                wev[dd]=dt
                
            data.append(wev)

productlink=[]
data = requests.get(url).json()
for d in data["data"]:
    link = BeautifulSoup(d["actions"], "lxml").a["href"]
    productlink.append(base_url+link)

with ThreadPoolExecutor() as executor:
    executor.map(process, productlink)

df = pd.DataFrame(test)
df.to_csv("sample.xlsx")






























        
        
        
        
        
        
        
        
        
        
        

        
            

                

      
        
        
        
        

        
    
        
        




