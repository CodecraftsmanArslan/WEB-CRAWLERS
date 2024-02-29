import scrapy
from scrapy.http import Request
from scrapy.crawler import CrawlerProcess

class TestSpider(scrapy.Spider):
    name = 'test'
    page_number = 1
    start_urls = ['https://rejestradwokatow.pl/adwokat/list/strona/1/sta/2,3,9']
    custom_settings = {
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 1,
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }


    def parse(self, response):
        books = response.xpath("//td[@class='icon_link']//a//@href").extract()
        for book in books:
            url = response.urljoin(book)
            yield Request(url, callback=self.parse_book)

    def parse_book(self, response):
        # it may need default value when item doesn't exist on page 
        wev = {
            'title':'',
            'Email:': '',
            'Status:': '',
            'Fax:': '',
            'Data wpisu w aktualnej izbie na listę adwokatów:': '',
            'Stary nr wpisu:': '',
            'Adres do korespondencji:': '',
            
        }
        
        title=response.css("section h2::text").get()
        wev['title']=title

        tic = response.xpath("//div[@class='line_list_K']//div//span//text()").getall()
        det = response.xpath("//div[@class='line_list_K']//div//div//text()").getall()


        all_rows = response.xpath("//div[@class='line_list_K']/div")

        for row in all_rows:
            name  = row.xpath(".//span/text()").get()
            value = row.xpath(".//div/text()").get()
            if name and value:
                wev[name.strip()] = value.strip()
            elif name and name.strip() == 'Email:':
                # <div class="address_e" data-ea="adwokat.adach" data-eb="gmail.com"></div>
                div = row.xpath('./div')
                email_a = div.attrib['data-ea']
                email_b = div.attrib['data-eb']
                wev[name.strip()] = f'{email_a}@{email_b}'

        print(wev)

        yield wev
        
        
        next_page = 'https://rejestradwokatow.pl/adwokat/list/strona/' + str(TestSpider.page_number) + '/sta/2,3,9' 
        if TestSpider.page_number<=288:
            TestSpider.page_number += 1
            yield response.follow(next_page, callback = self.parse)