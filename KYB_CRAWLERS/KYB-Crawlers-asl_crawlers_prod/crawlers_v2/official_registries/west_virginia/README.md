# Crawler: West Virginia

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [West Virginia Secretary of State](https://secure.dlca.vi.gov/license/Asps/Search/License_search.aspx). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "A. O. DODGE REALTY, INC.",
  "type": "C | Corporation",
  "industries": "",
  "meta_detail": {
    "class": "Profit",
    "charter": "Domestic",
    "excess_acres": "0",
    "control_number": "0",
    "effective_date": "1-1-1981",
    "dissolution_reason": "Revoked (Failure to File Annual Report)"
  },
  "country_name": "West Virginia",
  "crawler_name": "custom_crawlers.kyb.west_virginia.west_virginia_kyb.py",
  "jurisdiction": "West Virginia",
  "people_detail": [
    {
      "name": "A O DODGE",
      "address": "49 BRIARWOOD DR. WHEELING, WV, 26003",
      "designation": "Incorporator"
    },
    {
      "name": "JIM A DODGE",
      "address": "125 WALNUT ST LEMOYNE, PA, 17043",
      "designation": "President"
    },
    {
      "name": "DONALD A DODGE",
      "address": "10 WOODLAND DRIVE WHEELING, WV, 26003",
      "designation": "Secretary"
    }
  ],
  "addresses_detail": [
    {
      "type": "notice_address",
      "address": "DONALD A DODGE6251 HARDING AVE.HARRISBURG, PA, 17112"
    },
    {
      "type": "principal_office_address",
      "address": "6251 HARDING AVE.HARRISBURG, PA, 17112"
    }
  ],
  "dissolution_date": "6-15-2001",
  "additional_detail": [
    {
      "data": [
        {
          "capital_stock": "5000.0000",
          "share_par_value": "0.500000",
          "authorized_share": "10000"
        }
      ],
      "type": "shares_information"
    }
  ],
  "registration_date": "1-1-1981",
  "incorporation_date": "",
  "registration_number": "000077"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be approximately one week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/west_virginia/west_virginia_kyb.py`