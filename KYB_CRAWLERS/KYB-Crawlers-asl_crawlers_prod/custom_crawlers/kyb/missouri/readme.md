# Crawler: Missouri

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Missouri Secretary of State, Business Services Division](https://bsd.sos.mo.gov/BusinessEntity/BESearch.aspx?SearchType=0). The script use undetected selenium driver to get the data HTML page, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports".

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "INSTITUTE FOR BEAUTY, WOMEN'S HEALTH & FAMILY CLINIC",
  "type": "Fictitious Name",
  "status": "Fictitious Expired",
  "country_name": "missouri",
  "crawler_name": "custom_crawlers.kyb.missouri.missouri.py",
  "inactive_date": "11-27-2017",
  "people_detail": [
    {
      "name": "ALPHA HEALTH MANAGEMENT SERVICES, LLC",
      "designation": "owner",
      "meta_detail": {
        "since": "11/27/2012",
        "owner_type": "Organization"
      }
    }
  ],
  "fillings_detail": [
    {
      "date": "12-04-2017",
      "title": "Fictitious Name Expiration",
      "filing_type": "Administrative - Judicial Actions",
      "meta_detail": {
        "effective_date": "12-04-2017"
      }
    },
    {
      "date": "11-27-2012",
      "title": "Application for Fictitious Name Registration",
      "filing_type": "Creation",
      "meta_detail": {
        "effective_date": "11-27-2012"
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "mailing_address",
      "address": "590 W. PACIFICBRANSON, MO 65616",
      "meta_detail": {
        "since": "11-27-2012"
      }
    }
  ],
  "incorporation_date": "11-27-2012",
  "registration_number": "X01271771"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to get HTML data from results page and then use `beautifulsoup` to parse and extract required information.

## Additional Dependencies
- `selenium`
- `beautifulsoup4`
- `undetected chrome browser`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 missouri.py`