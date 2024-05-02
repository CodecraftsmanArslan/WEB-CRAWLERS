# Israel Official Registry Crawler

## Introduction
    The Python script serves as a web scraper for extracting information from the Ministry of Justice - Israel Corporations Authority (ICA) official registry. 
    Tailored for company data retrieval, it utilizes HTTP requests to the registry's website, employs JavaScript code parsing for data extraction, and structures
    the information into a dictionary format. The script inserts the data into a database and logs the crawler's status, including success or failure, along with 
    relevant details. Configuration parameters for the crawler and metadata about the data source are specified within the script. The optional command-line arguments
    allow users to define a range of record numbers to scrape. Overall, the script provides a robust tool for systematically gathering company details from the Israeli 
    official registry.


## meta_data = {
  
    'SOURCE' :'Ministry of Justice - Israel Corporations Authority (ICA)',
    'COUNTRY' : 'Israel',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://ica.justice.gov.il/GenericCorporarionInfo/SearchCorporation?unit=8", 
                        "Source Description": ""},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://ica.justice.gov.il/GenericCorporarionInfo/SearchCorporation?unit=8'
}

## crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': True,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Israel Official Registry",
}

## Sample object = {
    "name": "סאבקו-דיאם בע\"מ",
    "status": "פעילה",
    "meta_detail": {
      "aliases": "סאבקו-דיאם בע\"מ",
      "purpose": "לעסוק בסוגי עיסוק שפורטו בתקנון",
      "limitation": "מוגבלת",
      "located_in": "ישראלית",
      "fee_in_2023": "1614.00 ש''ח לתשלום עד 31-12-2023",
      "fee_obligations": "יש",
      "law_compromised": "מפרה",
      "incorporation_year": 1997
    },
    "country_name": "Israel",
    "crawler_name": "custom_crawlers.kyb.israel.israel_kyb.py",
    "fillings_detail": [
      {
        "date": "13-03-2023",
        "title": "סילוק שעבוד",
        "meta_detail": {
          "filing_status": "מסורב",
          "contact_number": 29494326,
          "corporate_name": "סאבקו-דיאם בע\"מ",
          "treatment_date": "14-03-2023",
          "corporate_number": 511352429,
          "document_identification": "https://login.gov.il/nidp/saml2/sso?id=usernamePasswordSMSOtp&sid=2&option=credential&sid=2"
        }
      },
      {
        "date": "23-02-2023",
        "title": "סילוק שעבוד",
        "meta_detail": {
          "filing_status": "מסורב",
          "contact_number": 29342191,
          "corporate_name": "סאבקו-דיאם בע\"מ",
          "treatment_date": "01-03-2023",
          "corporate_number": 511352429,
          "document_identification": "https://login.gov.il/nidp/saml2/sso?id=usernamePasswordSMSOtp&sid=2&option=credential&sid=2"
        }
      }
    ],
    "addresses_detail": [
      {
        "type": "general_address",
        "address": "ישראל"
      }
    ],
    "incorporation_date": "03-01-1989",
    "registration_number": "511352429" }
## Crawler Type
    This is a web scraper crawler designed for extracting information from the Ministry of Justice - Israel Corporations Authority (ICA) official registry. The crawler is specifically tailored for company/organization data.

## Dependencies
    - `traceback`
    - `requests`
    - `sys`
    - `json`
    - `re`
    - `time`
    - `os`
    - `datetime`
    - `pathlib`

## Additionally, the script depends on custom modules:
    - `CustomCrawler` from `CustomCrawler.py`
    - `load_env` from `load_env/load_env.py`

## Global Variables
    - `STATUS_CODE`: Holds the HTTP status code.
    - `DATA_SIZE`: Keeps track of data size.
    - `CONTENT_TYPE`: Represents the content type (HTML in this case).
    - `CURRENT_NUMBER`: Holds the current record number.

## Metadata
    Metadata about the source and crawler configuration is specified in the `meta_data` and `crawler_config` dictionaries.

## How to run the crawler
    1. Install required dependencies: `pip install -r requirements.txt`
    2. Ensure the appropriate WebDriver (e.g., ChromeDriver) is downloaded and its path is correctly configured in the script.
    3. Run the script: `python3 your_script.py arg1 arg2`

    - `arg1`: Starting record number (optional, default is 510000000)
    - `arg2`: Ending record number (optional, default is 599999999)

    Example: `python3 your_script.py 510000000 510000010`

