import time
from playwright.sync_api import sync_playwright
import pandas as pd

with sync_playwright() as p:
    browser = p.webkit.launch(headless=False)
    baseurl = "https://www.ifep.ro/Justice/Lawyers/LawyersPanel.aspx?CompanyId=1115&CurrentPanel=Definitivi&HideHeader=1&HideFooter=1&HideFilters=1"
    page = browser.new_page()
    page.goto(baseurl)
    productlinks = []
    
    # page.locator("text=Tabloul avocaţilor stagiari").click()
    for k in range(1,47):
        links = page.query_selector_all("//div[@class='list-group']//a")
        for link in links:
            link_href = link.get_attribute("href")
            if link_href.startswith("LawyerFile.aspx"):
                productlinks.append("https://www.ifep.ro/justice/lawyers/" + link_href)
        
        time.sleep(8)
        # page.select_option('select#MainContent_ddlRecords', '30')
        page.wait_for_selector("#MainContent_PagerTop_NavNext").click()
        time.sleep(4)  # wait for load the page
    data=[]    
    for product in productlinks:
        wev={}
        page.goto(product)
        title = page.wait_for_selector('#HeadingContent_lblTitle').text_content()
        wev['title']=title
        
        try:
            d6=page.wait_for_selector("//span[@class='text-nowrap']//a").text_content()
           
        except:
            pass
        wev['Email']=d6
        try:
            d5 = page.wait_for_selector("//span[@class='padding-right-md text-primary']").text_content()
            d5=d5.replace(".", "")
        except:
            pass
        wev['phone']=d5
        d1 = page.wait_for_selector("//div[@class='col-md-10']//p[1]").text_content()
        wev['Avocaţilor']=d1.strip()
        d2 = page.wait_for_selector("//div[@class='col-md-10']//p[2]").text_content()
        d2 = d2.strip().split()[-1]
        wev['Dată înscriere']=d2
        d3 = page.wait_for_selector("//div[@class='col-md-10']//p[3]//span").text_content()
        d3 = d3.strip().split()[-1]
        wev['Situaţie curentă în tablou']=d3
        d4 = page.wait_for_selector("//div[@class='col-md-10']//p[4]").text_content()
        d4 = d4.strip().split()[-1]
        wev['Instanţe cu drept de concluzii']=d4
        data.append(wev) 
        time.sleep(5)
    df=pd.DataFrame(data)
    df.to_csv("data.csv")
    browser.close()
    
   