# Crawler: Arizona

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Arizona Corporation Commission (ACC)](https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx). The script fetches data from the specified API endpoint by adding entity Number (23000001 to 23540336), processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "LAZY S-6 PROPERTIES, LLC",
  "type": "Domestic LLC",
  "status": "Active",
  "industries": "Real Estate and Rental and Leasing",
  "meta_detail": {
    "status_date": "6-30-2019",
    "formation_date": "6-30-2019",
    "reason_for_status": "In Good Standing"
  },
  "country_name": "Arizona",
  "crawler_name": "custom_crawlers.kyb.arizona.arizona.py",
  "jurisdiction": "Arizona",
  "people_detail": [
    {
      "name": "Gary Pisciotta",
      "address": "PO Box 1012, PALMER LAKE, CO, 80133,  El Paso County, USA",
      "designation": "Member and Manager",
      "meta_detail": {
        "last_updated": "7-8-2019"
      },
      "appointment_date": "6-30-2019"
    },
    {
      "name": "Pisciotta Family Trust April 26, 2019",
      "address": "312 E DEEPDALE RD, PHOENIX, AZ, 85022,  Maricopa County, USA",
      "designation": "Member and Manager",
      "meta_detail": {
        "last_updated": "7-8-2019"
      },
      "appointment_date": "6-30-2019"
    },
    {
      "name": "Pisciotta Family Trust 10/23/2009",
      "address": "6603 W. Via Dona Rd, PHOENIX, AZ, 85083,  Maricopa County, USA",
      "designation": "Member and Manager",
      "meta_detail": {
        "last_updated": "7-8-2019"
      },
      "appointment_date": "6-30-2019"
    },
    {
      "name": "STEVEN PISCIOTTA",
      "designation": "registered_agent",
      "meta_detail": {
        "status": "Active 7-8-2019",
        "last_updated": "7-8-2019"
      },
      "postal_address": "312 E DEEPDALE RD  , PHOENIX, AZ 85022, USA"
    }
  ],
  "fillings_detail": [
    {
      "date": "07-03-2019",
      "file_url": "https://ecorp.azcc.gov/CommonHelper/GetFilingDocuments?barcode=19070304130471",
      "filing_code": "19070304130471",
      "filing_type": "Articles of Organization",
      "meta_detail": {
        "status": "Approved"
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "312 E DEEPDALE RD, PHOENIX, AZ, 85022, USA",
      "meta_detail": {
        "county": "Maricopa",
        "last_updated": "7-8-2019"
      }
    }
  ],
  "registration_date": "7-8-2019",
  "incorporation_date": "6-30-2019",
  "registration_number": "23000007"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4`

## Estimated Processing Time
The processing time for the crawler is estimated 2 months.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/arizona/arizona_1.py`