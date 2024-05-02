# Crawler: California

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [California Secretary of State](https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx). The script fetches data from specified API endpoint, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "123 AVIATION LLC",
  "type": "Limited Liability Company - CA",
  "status": "Active",
  "meta_detail": {
    "initial_filing_date": "04-08-2020",
    "statement_filing_due_date": "31-08-2024"
  },
  "country_name": "California",
  "crawler_name": "custom_crawlers.kyb.california.california_kyb.py",
  "jurisdiction": "CALIFORNIA",
  "inactive_date": "",
  "people_detail": [
    {
      "name": "JOYCE YI",
      "address": "101 N BRAND BLVD 11TH FL, GLENDALE, CA",
      "designation": "ca_registered_agent"
    },
    {
      "name": "SANDRA MENJIVAR",
      "address": "101 N BRAND BLVD 11TH FL, GLENDALE, CA",
      "designation": "ca_registered_agent"
    },
    {
      "name": "LEGALZOOM.COM, INC.",
      "designation": "registered_agent",
      "meta_detail": {
        "type": "1505 Corporation"
      }
    }
  ],
  "fillings_detail": [
    {
      "date": "3-12-2023",
      "title": "Statement of Information",
      "file_url": "https://bizfileonline.sos.ca.gov/api/report/GetImageByNum/087142029081015088074241081114160183013146092163",
      "filing_code": "BA20230422179",
      "filing_type": "Statement of Information",
      "meta_detail": {
        "field_1": "Annual Report Due Date",
        "field_2": "Labor Judgement",
        "changed_to_1": "31-08-2024",
        "changed_from_1": "31-08-2022"
      }
    },
    {
      "date": "3-12-2021",
      "title": "Statement of Information",
      "file_url": "https://bizfileonline.sos.ca.gov/api/report/GetImageByNum/220073206076152196118228026250128197125245252238",
      "filing_code": "LBA31789745",
      "filing_type": "Statement of Information",
      "meta_detail": {
        "field_1": "Legacy Comment"
      }
    },
    {
      "date": "3-2-2021",
      "title": "System Amendment - SI Delinquency for the year of 0",
      "filing_code": "LBA31789744",
      "filing_type": "System Amendment - SI Delinquency for the year of 0"
    },
    {
      "date": "8-4-2020",
      "title": "Initial Filing",
      "file_url": "https://bizfileonline.sos.ca.gov/api/report/GetImageByNum/071120252082096173149111180209062123094082211219",
      "filing_code": "202021910223",
      "filing_type": "Initial Filing"
    }
  ],
  "addresses_detail": [
    {
      "type": "principal_address",
      "address": "3211 AVIATION DR. MADERA, CA 93637"
    },
    {
      "type": "mailing_address",
      "address": "3211 AVIATION DR. MADERA,CA93637"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "standing_ftb": "Good",
          "standing_sos": "Good",
          "standing_agent": "Good",
          "standing_vcfcf": "Good"
        }
      ],
      "type": "standings_information"
    }
  ],
  "registration_number": "202021910223"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request`library for scraping data.

## Additional Dependencies
- `Request`
- `dateutil`


## Estimated Processing Time
The processing time for the crawler is estimated 4 month.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the scrip for source 1: `python3 ASL-Crawlers/custom_crawlers/kyb/california/california_kyb.py`
