# Crawler: United Arab Emirates

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Ministry of Economy - National Economic Register](https://ner.economy.ae/Search_By_BN.aspx).The script utilizes Selenium to extract data from web pages indexed between a to z and 0 to 9, as part of the search process, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports"

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "AL NAKKAS TRADING ESTABLISHMENT - BRANCH",
  "type": "Companie Branches",
  "status": "Active",
  "industries": "Importing,Retail sale of Fresh Fruits and Vegetables,",
  "meta_detail": {
    "alias": "مؤسسة النكاس للتجارة - فرع",
    "is_branch": "No",
    "expiry_date": "03-04-2026",
    "license_number": "CN-1065923",
    "registration_branch": "Abu Dhabi Department for Economic Development",
    "industries_in_arabic": "استيراد,بيع الفواكه والخضروات الطازجة - بالتجزئة,",
    "emirate_of_registration": "Abu Dhabi Department of Economic Development"
  },
  "country_name": "United Arab Emirates",
  "crawler_name": "custom_crawlers.kyb.united_arab_emirates.united_arab_emirates_py.py",
  "contacts_detail": [
    {
      "type": "mobile_number",
      "value": "00971554671980"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "أبو ظبي - شارع  الميناء -  بناية دائرة بلدية ابوظبي,    أبو ظبي - شارع  الميناء -  بناية دائرة بلدية ابوظبي أبوظبي"
    }
  ],
  "registration_date": "21-12-2004",
  "registration_number": "11085461"
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
5. Run the script: `python3 custom_crawlers/kyb/united_arab_emirates/united_arab_emirates_py.py`