# Crawler: North Dakota

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [North Dakota Secretary of State](https://firststop.sos.nd.gov/search/business). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "1520 Hawks Investments inc",
  "type": "Corporation - Business - Domestic",
  "status": "Active",
  "industries": "",
  "meta_detail": {
    "expiration_date": "",
    "term_of_duration": "Perpetual",
    "initial_filing_date": "01-25-2023",
    "accounts_receivable_date": "08-01-2024"
  },
  "jurisdiction": "NORTH DAKOTA",
  "people_detail": [
    {
      "name": "JORDANSIFUENTES",
      "address": "749 3RD AVE SE, DICKINSON, ND58601",
      "designation": "registered_agent"
    }
  ],
  "fillings_detail": [
    {
      "date": "1-25-2023",
      "filing_code": "0006159846",
      "filing_type": "Initial Filing"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "749 3RD AVE SE DICKINSON, ND 58601"
    },
    {
      "type": "postal_address",
      "address": "749 3RD AVE SE DICKINSON, ND 58601-6018"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "standing_ar": "Good",
          "standing_ra": "Good",
          "standing_other": "Good"
        }
      ],
      "type": "standing_information"
    }
  ],
  "registration_number": "0006159846"
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
5. Run the script: `python3 custom_crawlers/kyb/north_dakota/north_dakota.py`