# Crawler: Delaware

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Delaware Secretary of State, Division of Corporations](https://data.delaware.gov/Licenses-and-Certifications/Delaware-Business-Licenses/5zy2-grhr). There are two sources exist in this country. In source one the script fetches data from the specified API endpoint, and source two use selenium for captcha solving processes the retrieved HTML content, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"Source one"
"data":{
  "name": "DYNAMIC DOCK & DOOR LLC",
  "industries": "GENERAL SERVICES",
  "meta_detail": {
    "trade_name": "DYNAMIC DOCK & DOOR LLC",
    "license_valid_to": "2023-12-31T00:00:00.000",
    "license_valid_from": "2023-01-01 00:00:00"
  },
  "country_name": "Delaware",
  "crawler_name": "crawlers.custom_crawlers.kyb.delaware.delaware_kyb",
  "addresses_detail": [
    {
      "type": "postal_address",
      "address": "64 LOWELL ST  UNITED STATES WEST SPRINGFIELD MA 010893507",
      "meta_detail": {
        "latitude": "42.095959998",
        "longitude": "-72.616629979"
      }
    }
  ],
  "registration_number": "2022713331"
}
"Source two"
"data":{
  "name": "21 MANAGEMENT COMPANY OF DELAWARE, INC.",
  "type": "Corporation",
  "meta_detail": {
    "category": "General",
    "domicile": "Domestic",
    "incorporatio_date": "1-8-1981"
  },
  "country_name": "Delaware",
  "crawler_name": "custom_crawlers.kyb.delaware.delaware_source2.py",
  "jurisdiction": "DELAWARE",
  "people_detail": [
    {
      "name": "THE PRENTICE-HALL CORPORATION SYSTEM, INC.",
      "address": "251 LITTLE FALLS DRIVE New Castle WILMINGTON DE",
      "designation": "registered_agent",
      "phone_number": "302-636-5400"
    }
  ],
  "registration_number": "905990"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request`,`Selenium` and`Pandas`  libraries for scraping.

## Additional Dependencies
- `Request`
- `pandas` 
- `selenium` 
- `webdriver_manager`


## Estimated Processing Time
The processing time for the source one is estimated 50 minniutes and source two is estimated 3 days.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the scrip for source 1: `python3 custom_crawlers/kyb/delaware/delaware_kyb.py`
6. Run the script for source 2: `python3 custom_crawlers/kyb/delaware/delaware_source2.py`
