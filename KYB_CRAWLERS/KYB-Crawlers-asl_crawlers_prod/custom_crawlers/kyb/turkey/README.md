# Crawler: Turkey

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Istanbul Chamber of Commerce (ICOC)](https://bilgibankasi.ito.org.tr/en/data-bank/company-details).The script utilizes Selenium to extract data from web pages within the index range of 1 to 999,999 as an integral part of the search process, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports"

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "MBA GİYİM SANAYİ VE DIŞ TİCARET LİMİTED ŞİRKETİ",
  "status": "Firmanın dosyasında ORTAKLARLA İLGİLİ TAKYİDAT bulunmaktadır.",
  "industries": "39-UNDERWEAR AND ACCESSORIES",
  "meta_detail": {
    "capital": "50.000,00 ₺",
    "tax_id_available": "Mevcut",
    "chamber_registration_number": "1326869",
    "main_contract_registry_date": "28-10-2021",
    "central_registration_system_number": "0613-1773-9860-0001"
  },
  "country_name": "Turkey",
  "crawler_name": "custom_crawlers.kyb.turkey.turkey_kyb.py",
  "people_detail": [
    {
      "name": "PINAR AYDİNÇ",
      "designation": "Director Solely"
    }
  ],
  "contacts_detail": [
    {
      "type": "phone_number",
      "value": "5323940343"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "AKŞEMSEDDİN MAH.AŞIK MAHSUNİ ŞERİF CAD.NO:44 İÇ KAPI NO:1 ESENYURT"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "code": "47.71.01",
          "description": "Retail trade of infant and children wearing apparels in specialized stores (including infant underwear apparels)"
        }
      ],
      "type": "nace_code"
    }
  ],
  "registration_date": "28-10-2021",
  "registration_number": "336531-5"
}


```


## Crawler Type
This is a web scraper crawler that uses the `Selenium` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Selenium`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be more than a week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/turkey/turkey_kyb.py`