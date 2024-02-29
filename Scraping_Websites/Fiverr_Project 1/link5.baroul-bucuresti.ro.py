import scrapy
from scrapy.http import Request
from bs4 import BeautifulSoup
import pandas as pd


class GeneralSpider(scrapy.Spider):
    name = 'general'
    start_urls = ['https://www.baroul-cluj.ro/tabloul-avocatilor/avocati-definitivi/']
    page_number = 1
   
    
    def parse(self, response):
       
        for tt in response.xpath("//table[@class='table table-striped']"):
            for t in response.xpath("//tbody//tr"):
                ta=t.xpath(".//td[1]//text()").get()
                try:
                    k=t.xpath(".//td[2]//text()[1]").get()
                except:
                    pass  
                try:
                    l=t.xpath(".//td[2]//text()[2]").get()
                    l = "+" + l[5:]
                except:
                    pass
                
                try:
                    m=t.xpath(".//td[2]//text()[3]").get()
                except:
                    pass 
                 
                
                    
                tc=t.xpath(".//td[3]//text()").get()
                td=t.xpath(".//td[4]//text()").get()
                te=t.xpath(".//td[5]//text()").get()
                te=te.strip()
                tf=t.xpath(".//td[6]//text()").get()
                tf=tf.strip()
                
                
                yield{
                    'avocat':ta,
                    'address':k,
                    'telephone':l,
                    'email':m,
                    'Punct de lucru':tc,
                    'Data primirii în profesie':td,
                    'Instanțe la care poate pune concluzii':te,
                    'Limbi străine':tf
                    }
                
                
                next_page = 'https://www.baroul-cluj.ro/tabloul-avocatilor/avocati-definitivi/?wpv_view_count=9662&wpv_post_search=&wpv_paged=' + str(GeneralSpider.page_number) 
                
                if GeneralSpider.page_number<=26:
                    GeneralSpider.page_number += 1
                    yield response.follow(next_page, callback = self.parse)
            
                
                

            
         
            
            
      
            
 