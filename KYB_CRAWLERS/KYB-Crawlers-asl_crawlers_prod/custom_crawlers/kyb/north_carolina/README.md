# Crawler: North Carolina

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [North Carolina Secretary of State, Business Registration Division](https://www.sosnc.gov/online_services/search/by_title/_Annual_Report). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "Bankable, L.L.C.",
  "type": "Limited Liability Company",
  "status": "Current-Active",
  "meta_detail": {
    "citizenship": "Domestic",
    "annual_report_status": "Current",
    "annual_report_due_date": "April 15th"
  },
  "country_name": "North Carolina",
  "crawler_name": "custom_crawlers.kyb.north_carolina.north_carolina.py",
  "jurisdiction": null,
  "people_detail": [
    {
      "name": "Anderson Plaza, L.L.C.",
      "designation": "registered_agent"
    },
    {
      "name": "Anderson Plaza LLC",
      "address": "976 Martin Luther King Jr Blvd, Ste 200 Chapel Hill NC 27514",
      "designation": "Managing Member",
      "meta_detail": {
        "profile_link": "https://www.sosnc.gov/?id=8991052"
      }
    }
  ],
  "fillings_detail": [
    {
      "file_url": "https://www.sosnc.gov/online_services/imaging/download/1b_70909768_7ce577fade224faebec0cc8b92a33784",
      "filing_code": "CA202304700523",
      "filing_type": "Annual Report",
      "meta_detail": {
        "is_accepted": "Yes"
      }
    },
    {
      "file_url": "https://www.sosnc.gov/online_services/imaging/download/1b_63980816_3e18e125148a4514ae2d5922e338a0c1",
      "filing_code": "C202201401645",
      "filing_type": "Creation Filing",
      "meta_detail": {
        "is_accepted": "Yes"
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "mailing_address",
      "address": "976 Martin Luther King Jr Blvd Ste 200 Chapel Hill,NC27514"
    },
    {
      "type": "general_address",
      "address": "976 Martin Luther King Jr Blvd Ste 200 Chapel Hill,NC27514"
    },
    {
      "type": "registered_address",
      "address": "Suite 200, The Cornerstone Building, 976 MartinLuther King, Jr. Boulevard Chapel Hill,NC27514"
    },
    {
      "type": "registered_mailing_address",
      "address": "Suite 200, The Cornerstone Building, 976 MartinLuther King, Jr. Boulevard Chapel Hill,NC27514"
    }
  ],
  "incorporation_date": "20-01-2022",
  "registration_number": "2340074"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Requests` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Requests`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be approximately one week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/north_carolina/north_carolina.py`