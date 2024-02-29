import scrapy
from scrapy.http import Request
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from scrapy_selenium import SeleniumRequest


class TestSpider(scrapy.Spider):
    name = 'test'
    page_number = 1

    def start_requests(self):
        yield SeleniumRequest(
            url="https://www.barreaulyon.com/annuaire/",
            wait_time=3,
            screenshot=True,
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        books = response.xpath(
            "//div[@class='entry-content']//a[starts-with(@href, 'https://www.barreaulyon')]/@href").extract()
        for book in books:
            url = response.urljoin(book)

            yield Request(url, callback=self.parse_book)

    def parse_book(self, response):
        title = response.css("h1::text").get()
        
        telephone = response.xpath(
            "//div[@class='entry-infos__item entry-infos__item--tel']//a[starts-with(@href, 'tel')]/@href").get()
        try:
            telephone=telephone[4:]
        except:
            pass
        
        try:
            Fax=response.xpath("//div[@class='entry-infos__item']//a//@href").get()
            Fax=Fax[4:]
        except:
            pass
         
        try:
            mail = response.xpath("//a[starts-with(@href, 'mailto')]/@href").get()
            mail=mail[7:]
        except:
            mail=''
            
      
    
        details = response.xpath("//div[@class='entry-content']")
        for detail in details:
            d1 = detail.xpath("//div[@class='entry-content__item'][1]//text()").getall()
            d1=[i.strip() for i in d1]
            
            
            d2 = detail.xpath("//div[@class='entry-content__item'][2]//text()").getall()
            
            d2=[k.strip() for k in d2]
            
            d3 = detail.xpath("//div[@class='entry-content__item'][3]//text()").getall()
            d3=[j.strip() for j in d3]
            
            d4 = detail.xpath("//div[@class='entry-content__item'][4]//text()").getall()
            d4=[e.strip() for e in d4]
            
            d5 = detail.xpath("//div[@class='entry-content__item'][5]//text()").getall()
            d5=[f.strip() for f in d5]
            
            d6 = detail.xpath("//div[@class='entry-content__item'][6]//text()").getall()
            d6=[g.strip() for g in d6]
            
            yield{
                "title": title,
                "tel": telephone,
                "Fax":Fax,
                "email": mail,
                "d1": d1,
                "d2": d2,
                "d3": d3,
                "d4": d4,
                "d5": d5,
                "d6": d6
                }
            
            next_page = 'https://www.barreaulyon.com/annuaire?paged=' + str(TestSpider.page_number)
            if TestSpider.page_number<=335:
                TestSpider.page_number += 1
                yield response.follow(next_page, callback = self.parse)