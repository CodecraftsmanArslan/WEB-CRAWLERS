# Crawler: Palestine

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Ministry of National Economy (وزارة الاقتصاد الوطني) - Companies Controller](http://www.mne.gov.ps:9095/ords/f?p=200:298). The script employs Selenium to retrieve data from web pages, encompassing those indexed from 'a' to 'z', 0 to 9, and Urdu characters, as part of the search process, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "translate_reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "شركة جلاسكو للتصدير المحدودة GLAXO EXPORT LIMITED",
  "type": "شركة",
  "status": "شركة مسجلة",
  "industries": "العمل في مجال التجارة العمل في مجال التجارة العمل في مجال الصناعة العمل في مجال الصناعة صنع المواد والمنتجات الكيميائية",
  "meta_detail": {
    "entity_name": "شركة جلاسكو للتصدير المحدودة GLAXO EXPORT LIMITED"
  },
  "country_name": "State of Palestine",
  "crawler_name": "custom_crawlers.kyb.palestine.palestine_kyb.py",
  "jurisdiction": "غزة",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "فلسطين غزة غزة"
    }
  ],
  "registration_date": "22-02-1995",
  "registration_number": "563600725"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Selenium` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Selenium`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler is expected to take more than a week to complete its processing.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/palestine/palestine_kyb.py`