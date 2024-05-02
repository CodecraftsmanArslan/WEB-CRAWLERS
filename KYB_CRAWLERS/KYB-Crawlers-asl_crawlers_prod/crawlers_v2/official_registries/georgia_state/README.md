# Crawler: Georgia (US State)

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Secretary of State](https://ecorp.sos.ga.gov/BusinessSearch). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "MANNA FAMILY CHIROPRACTIC, PC",
  "type": "Domestic Professional Corporation",
  "status": "",
  "meta_detail": {
    "last_annual_registration_year": "2023"
  },
  "country_name": "Georgia (US State)",
  "jurisdiction": "Georgia",
  "people_detail": [
    {
      "name": "Thomas Michael Shepherd",
      "county": "Fulton",
      "address": "2970 Peachtree Road, Suite 825, Atlanta, GA, 30305, USA",
      "designation": "registered_agent"
    },
    {
      "name": "ROBERT J. MANNA, D.C.",
      "address": "310 SHORTER AVENUE, ROME, GA, 30165, USA",
      "designation": "CFO"
    },
    {
      "name": "ROBERT J. MANNA, D.C.",
      "address": "310 SHORTER AVENUE, ROME, GA, 30165, USA",
      "designation": "Secretary"
    },
    {
      "name": "ROBERT J. MANNA, D.C.",
      "address": "310 SHORTER AVENUE, ROME, GA, 30165, USA",
      "designation": "CEO"
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": "310 SHORTER AVE NW, ROME, GA, 30165-4268, USA"
    }
  ],
  "dissolution_date": "",
  "registration_date": "04-28-2020",
  "registration_number": "0000001"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Selenium` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Selenium`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be approximately one week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Change directory by using this command `cd crawlers_v2/official_registries/georgia_state`
6. Run the script: `python3 georgia.py`