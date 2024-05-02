# Crawler: liechtenstein

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Handelsregister des Fürstentums](https://www.oera.li/cr-portal/suche/suche.xhtml). The script use selenium to crawl to data page, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "AARA Stiftung",
  "type": "Eingetragene Stiftung",
  "meta_detail": {
    "municipality": "Vaduz",
    "address_detail": [
      {
        "type": "general_address",
        "address": "c/o Continor Treuhand Anstalt Kirchstrasse 19490 Vaduz",
        "meta_detail": {
          "reference_number": "1"
        }
      }
    ],
    "Additional_data": [
      {
        "data": [
          {
            "reference_number": "1",
            "daily_register_date": "07-11-2022",
            "daily_register_number": "10679"
          },
          {
            "reference_number": "2",
            "daily_register_date": "29-03-2023",
            "daily_register_number": "6010"
          }
        ],
        "type": "daily_register_information"
      }
    ]
  },
  "country_name": "Liechtenstein",
  "crawler_name": "custom_crawlers.kyb.liechtenstein.liechtenstein.py",
  "registration_date": "29-03-2023",
  "registration_number": "FL-0002.695.410-8"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library crawl to data page, get HTML data and then use `beautifulsoup` to parse and extract required information.

## Additional Dependencies
- `selenium`
- `beautifulsoup4`

## Estimated Processing Time
The processing time for the crawler is estimated < one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/liechtenstein/liechtenstein_selenium.py`