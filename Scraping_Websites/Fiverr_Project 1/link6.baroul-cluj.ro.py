import scrapy
from scrapy.http import Request
from bs4 import BeautifulSoup


class TestSpider(scrapy.Spider):
    name = 'test'
    start_urls = ['https://www.baroul-bucuresti.ro/tablou-definitivi']
    page_number = 1
    
    def parse(self, response):
        base_url='https://www.baroul-bucuresti.ro'
        soup=BeautifulSoup(response.text, 'html.parser')
        tra = soup.find_all('div',class_='panel-title')
        productlinks=[]
        for links in tra:
            for link in links.find_all('a',href=True)[1:]:
                comp=base_url+link['href']
                yield Request(comp, callback=self.parse_book)
     
    
    def parse_book(self, response):
           
        header=response.xpath("//div[@class='av_bot_left left']")
        for k in header:
            title=k.xpath("//h1//text()").get()
            title=title.strip()
            dec=k.xpath("//p[@class='ral_r f16']//text()").get()
            dec=dec.strip()
                
        d1=''
        d2=''
        d3=''
        d4=''
        d5=''
        
        detail=response.xpath("//div[@class='av_bot_left left']//p")
        for i in range(len(detail)):
           
              if 'Decizia de intrare:' in detail[i].get():
                d1=detail[i].xpath('.//text()').getall()
                d1 = [i.strip() for i in d1 if i.strip()][-1]
           
                
                
              elif 'Telefon:' in detail[i].get():
                d2=detail[i].xpath('.//text()').getall()
                d2 = [i.strip().replace(".", " ") for i in d2 if i.strip()][-1]
                d2 = "+" + d2[1:]
             
                
                  
              elif 'Expertiză' in detail[i].get():
                d3=detail[i].xpath('.//text()').getall()
                
                d3 = [i.strip() for i in d3 if i.strip()][-1]
                
                  
              elif 'Concluzii instanţe' in detail[i].get():
                d4=detail[i].xpath('.//text()').getall()
               
                d4 = [i.strip() for i in d4 if i.strip()][-1]
                
                
        mail=response.xpath("//div[@class='av_bot_left left']//a")       
        for j in range(len(mail)):
            if '@' in mail[j].get():
                d5=mail[j].xpath('.//text()').getall()
             
                d5 = [j.strip() for j in d5 if j.strip()][-1]
                
                
        yield{
            'Name':title,
            'Telefon':d2,
            'Adresă email':d5,
            'Data intrarii in baroul bucuresti':dec,
            'Expertiză':d3,
            'Decizia de intrare':d1,
            'Concluzii instanţe':d4,
            

        }
        
        
        next_page = 'https://www.baroul-bucuresti.ro/index.php?urlpag=tablou-definitivi&p=' + str(TestSpider.page_number) 

        if TestSpider.page_number<=624:
            TestSpider.page_number += 1
            yield response.follow(next_page, callback = self.parse)
            
            
            
            

                
                
        










  

