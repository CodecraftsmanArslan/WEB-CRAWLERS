# import scrapy
# from scrapy import FormRequest
# from scrapy.crawler import CrawlerProcess
# from scrapy.http import Request


# class TestSpider(scrapy.Spider):
#     name = 'test'
#     url = 'https://www.benrishi-navi.com/english/english1_2.php'
#     cookies = {
#     'CAKEPHP': 'u6u40lefkqnm45j49a5i0h6bs3',
#     '__utma': '42336182.871903078.1657200864.1657200864.1657200864.1',
#     '__utmz': '42336182.1657200864.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
#     }

#     headers = {
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,pt;q=0.7',
#         'Cache-Control': 'max-age=0',
#         'Connection': 'keep-alive',
#         # Requests sorts cookies= alphabetically
#         # 'Cookie': 'CAKEPHP=u6u40lefkqnm45j49a5i0h6bs3; __utma=42336182.871903078.1657200864.1657200864.1657200864.1; __utmz=42336182.1657200864.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
#         'Origin': 'https://www.benrishi-navi.com',
#         'Referer': 'https://www.benrishi-navi.com/english/english1_2.php',
#         'Sec-Fetch-Dest': 'document',
#         'Sec-Fetch-Mode': 'navigate',
#         'Sec-Fetch-Site': 'same-origin',
#         'Sec-Fetch-User': '?1',
#         'Upgrade-Insecure-Requests': '1',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
#         'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
#         'sec-ch-ua-mobile': '?0',
#         'sec-ch-ua-platform': '"Windows"',
#     }

#     formdata = [
#         ('tuusan_year', ''),
#         ('tuusan_month', ''),
#         ('tuusan_chk', ''),
#         ('methodAndOr1', ''),
#         ('methodAndOr2', ''),
#         ('methodAndOr3', ''),
#         ('text_sen', ''),
#         ('text_skill', ''),
#         ('text_business', ''),
#         ('tokkyo_data', ''),
#         ('fuki_day_chk', ''),
#         ('shuju', ''),
#         ('kensyuu_bunya', ''),
#         ('text_kensyuu', ''),
#         ('methodAndOr_kensyuu', ''),
#         ('keitai_kikan', ''),
#         ('keitai_hisu', ''),
#         ('display_flag', '1'),
#         ('search', '2'),
#         ('text', ''),
#         ('method', ''),
#         ('methodAndOr', ''),
#         ('area', ''),
#         ('pref', ''),
#         ('name', ''),
#         ('kana', ''),
#         ('id', ''),
#         ('year', ''),
#         ('month', ''),
#         ('day', ''),
#         ('day_chk', ''),
#         ('exp01', ''),
#         ('exp02', ''),
#         ('exp03', ''),
#         ('trip', ''),
#         ('venture_support', ''),
#         ('venture_flag', ''),
#         ('university_support', ''),
#         ('university_flag', ''),
#         ('university1', ''),
#         ('university2', ''),
#         ('university', ''),
#         ('college', ''),
#         ('high_pref', ''),
#         ('junior_pref', ''),
#         ('elementary_pref', ''),
#         ('tyosaku', ''),
#         ('hp', ''),
#         ('jukoureki', ''),
#         ('experience1', ''),
#         ('experience2', ''),
#         ('experience3', ''),
#         ('experience4', ''),
#         ('sort', ''),
#         ('fuki_year', ''),
#         ('fuki_month', ''),
#         ('fuki_day', ''),
#         ('fuki_day_chk', ''),
#         ('id_chk', ''),
#         ('shugyou', ''),
#         ('fuki', ''),
#         ('address1', ''),
#         ('address2', ''),
#         ('trip_pref', ''),
#         ('expref', ''),
#         ('office', ''),
#         ('max_count', '1438'),
#         ('search_count', '1438'),
#         ('start_count', '1'),
#         ('search_default', '1438'),
#     ]
   
    
#     def start_requests(self):
#         yield scrapy.FormRequest(
#             url=self.url,
#             method='POST',
#             formdata=self.formdata,
#             cookies=self.cookies,
#             headers=self.headers,
#             callback=self.parse_item,
#             )
        
        
#     def parse_item(self, response):
#         base_url="https://www.benrishi-navi.com/english/"
#         links =response.xpath("//table[4]//tr")
#         for link in links[1:]:
#             t=link.xpath("//form//@action").get()
#             u=link.xpath(".//input[@name='serial']//@value").get()
#             product=base_url+t+"?serial="+u+"&office_serial=&submit2=Details"
#             yield Request(product,callback=self.parse_book)
                    
#     def parse_book(self,response):
#         name=response.xpath("normalize-space(//td[text()[contains(.,'Name')]]/following-sibling::td//text())").get()
                
#         telephone=response.xpath("normalize-space(//td[text()[contains(.,'TEL')]]/following-sibling::td//text())").get()
        
#         fax=response.xpath("normalize-space(//td[text()[contains(.,'FAX')]]/following-sibling::td//text())").get()
        
#         email=response.xpath("normalize-space(//td[text()[contains(.,'Email')]]/following-sibling::td//text())").get()
        
#         website=response.xpath("//td[text()[contains(.,'Website')]]/following-sibling::td//a[starts-with(@href, 'http')]/@href").get()
        
        
#         registration_date=response.xpath("normalize-space(//td[text()[contains(.,'Registration date')]]/following-sibling::td//text())").get()
        
        
#         firm=response.xpath("normalize-space(//td[text()[contains(.,'Firm Name')]]/following-sibling::td//text())").get()
        
        
#         address=response.xpath("normalize-space(//td[text()[contains(.,'Address (Prefecture)')]]/following-sibling::td//text())").get()
        
        
        
#         spec=response.xpath("normalize-space(//td[text()[contains(.,'Specialization')]]/following-sibling::td//text())").get().replace(" ï½œ","|")
        
        
#         tech=response.xpath("normalize-space(//td[text()[contains(.,'Technical field')]]/following-sibling::td//text())").get().replace(" ï½œ","|")
        
        
#         yield{
#         "name":name,
#         "Telephone":telephone,
#         "Fax":fax,
#         "Email":email,
#         "website":website,
#         "Registration_date":registration_date,
#         "Firm_name":firm,
#         "Address":address,
#         "Specialization":spec,
#         "Technical_field":tech
#         }










import requests

cookies = {
    'CAKEPHP': 'f70i12bbp1mudao307fdnbks51',
    'ab.storage.deviceId.a9882122-ac6c-486a-bc3b-fab39ef624c5': '%7B%22g%22%3A%22c02a7b90-cf4b-74db-363c-587208117fe2%22%2C%22c%22%3A1679332482063%2C%22l%22%3A1679332482063%7D',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,pt;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    # 'Cookie': 'CAKEPHP=f70i12bbp1mudao307fdnbks51; ab.storage.deviceId.a9882122-ac6c-486a-bc3b-fab39ef624c5=%7B%22g%22%3A%22c02a7b90-cf4b-74db-363c-587208117fe2%22%2C%22c%22%3A1679332482063%2C%22l%22%3A1679332482063%7D',
    'Origin': 'https://www.benrishi-navi.com',
    'Referer': 'https://www.benrishi-navi.com/english/english1_2.php',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

data = [
    ('tuusan_year', ''),
    ('tuusan_month', ''),
    ('tuusan_chk', ''),
    ('methodAndOr1', ''),
    ('methodAndOr2', ''),
    ('methodAndOr3', ''),
    ('text_sen', ''),
    ('text_skill', ''),
    ('text_business', ''),
    ('tokkyo_data', ''),
    ('fuki_day_chk', ''),
    ('shuju', ''),
    ('kensyuu_bunya', ''),
    ('text_kensyuu', ''),
    ('methodAndOr_kensyuu', ''),
    ('keitai_kikan', ''),
    ('keitai_hisu', ''),
    ('display_flag', '1'),
    ('search', '2'),
    ('text', ''),
    ('method', ''),
    ('methodAndOr', ''),
    ('area', ''),
    ('pref', ''),
    ('name', ''),
    ('kana', ''),
    ('id', ''),
    ('year', ''),
    ('month', ''),
    ('day', ''),
    ('day_chk', ''),
    ('exp01', ''),
    ('exp02', ''),
    ('exp03', ''),
    ('trip', ''),
    ('venture_support', ''),
    ('venture_flag', ''),
    ('university_support', ''),
    ('university_flag', ''),
    ('university1', ''),
    ('university2', ''),
    ('university', ''),
    ('college', ''),
    ('high_pref', ''),
    ('junior_pref', ''),
    ('elementary_pref', ''),
    ('tyosaku', ''),
    ('hp', ''),
    ('jukoureki', ''),
    ('experience1', ''),
    ('experience2', ''),
    ('experience3', ''),
    ('experience4', ''),
    ('sort', ''),
    ('fuki_year', ''),
    ('fuki_month', ''),
    ('fuki_day', ''),
    ('fuki_day_chk', ''),
    ('id_chk', ''),
    ('shugyou', ''),
    ('fuki', ''),
    ('address1', ''),
    ('address2', ''),
    ('trip_pref', ''),
    ('expref', ''),
    ('office', ''),
    ('max_count', '1433'),
    ('search_count', '10'),
    ('start_count', '1'),
    ('search_default', '10'),
]

response = requests.post('https://www.benrishi-navi.com/english/english1_2.php', cookies=cookies, headers=headers, data=data)
print(response.text)
