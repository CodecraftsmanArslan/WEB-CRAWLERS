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
            url="https://zoekeenadvocaat.advocatenorde.nl/zoeken?q=&type=advocaten&limiet=10&sortering=afstand&filters%5Brechtsgebieden%5D=%5B%5D&filters%5Bspecialisatie%5D=0&filters%5Btoevoegingen%5D=0&locatie%5Badres%5D=Holland&locatie%5Bgeo%5D%5Blat%5D=52.132633&locatie%5Bgeo%5D%5Blng%5D=5.291266&locatie%5Bstraal%5D=56&locatie%5Bhash%5D=67eb2b8d0aab60ec69666532ff9527c9&weergave=lijst&pagina=1",
            wait_time=3,
            screenshot=True,
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        books = response.xpath(
            "//span[@class='h4 no-margin-bottom']//a//@href").extract()
        for book in books:
            url = response.urljoin(book)
            yield Request(url, callback=self.parse_book)

    def parse_book(self, response):
        title = response.css(".title h3::text").get()
        advocaten = response.css(".secondary::text").get()
        detail = response.xpath("//section[@class='lawyer-info']")
        for i in range(len(detail)):
            email = detail[i].xpath(
                "//a[starts-with(@href, 'mailto')]/@href").get()
            try:
                email = email[7:]
            except:
                pass
            phone = detail[i].xpath(
                "//a[starts-with(@href, 'tel:')]/@href").get()
            try:
                phone = "+" + phone[5:].replace("-", "")
            except:
                pass
            website = detail[i].xpath(
                "//a[starts-with(@href, 'http:')]/@href").get()
            address = detail[i].xpath(
                "//div[@class='column medium-6']//text()").getall()
            address = [j.strip() for j in address]
            location = detail[i].xpath(
                "//span[@class='icon-before inline']//span//text()").get()

            yield{
                'title': title,
                'email': email,
                'phone': phone,
                'website': website,
                'address': address,
                'location': location,
                'office': advocaten
            }

            next_page = 'https://zoekeenadvocaat.advocatenorde.nl/zoeken?q=&type=advocaten&limiet=10&sortering=afstand&filters%5Brechtsgebieden%5D=%5B%5D&filters%5Bspecialisatie%5D=0&filters%5Btoevoegingen%5D=0&locatie%5Badres%5D=Holland&locatie%5Bgeo%5D%5Blat%5D=52.132633&locatie%5Bgeo%5D%5Blng%5D=5.291266&locatie%5Bstraal%5D=56&locatie%5Bhash%5D=67eb2b8d0aab60ec69666532ff9527c9&weergave=lijst&pagina=' + \
                str(TestSpider.page_number)
            if TestSpider.page_number <= 1831:
                TestSpider.page_number += 1
                yield response.follow(next_page, callback=self.parse)
