# Crawler: Papua New Guinea

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Investment Promotion Authority (IPA)](https://www.ipa.gov.pg/corp/search.aspx). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "AINGDENG COFFEE ",
  "type": "Business Names",
  "status": "Registered",
  "industries": "A - AGRICULTURE, HUNTING AND FORESTRY",
  "meta_detail": {
    "commencement_date": "28-03-2023",
    "foreign_enterprise": "False",
    "has_own_constitution": "",
    "annual_return_due_date": "31-03-2024",
    "registration_expiry_date": "31-03-2024"
  },
  "country_name": "Papua New Guinea",
  "crawler_name": "custom_crawlers.kyb.papua_new_guinea_kyb",
  "contacts_detail": [
    {
      "type": "email",
      "value": "admin@ggaccountant.com"
    }
  ],
  "fillings_detail": [
    {
      "date": "28-03-2023",
      "filing_code": "9112600016",
      "filing_type": "A17  Application for registration of business name",
      "meta_detail": {
        "submission_date": "29-03-2023"
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "postal_address",
      "address": "C/-NENENG TRADE STORE PO BOX 201,   LAE, TEWAE-SIASSI, MOROBE,  PAPUA NEW GUINEA "
    },
    {
      "type": "general_address",
      "address": "BUTENGKA VILLAGE, WARD 13, SIALUM LLG,   LAE, LAE, MOROBE,  PAPUA NEW GUINEA "
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "note": "",
          "status": "Registered",
          "form_type": "A-17 - Application for registration of business name",
          "effective_date": "29-03-2023"
        }
      ],
      "type": "status_information"
    }
  ],
  "registration_date": "29-03-2023",
  "registration_number": "6-120740113"
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
5. Run the script: `python3 custom_crawlers/kyb/papua/papua_new_guinea_kyb.py`