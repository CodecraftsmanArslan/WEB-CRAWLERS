# Crawler: Seychelles

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Ministry of Finance, and Trade -Seygoconnect](https://www.registry.gov.sc/BizRegistration/WebSearchBusiness.aspx). The script use requests module to get HTML data, beautifulsoup to extract, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "F.J. VIDEO",
  "type": "Business",
  "industries": "ENTERTAINMENT SERVICES",
  "country_name": "Seychelles",
  "crawler_name": "custom_crawlers.kyb.seychelles.seychelles.py",
  "registration_number": "B940727"
}
```

## Crawler Type
This is a web scraper crawler that uses the `requests` library to get HTML data and `beautifulsoup` to extract required information.

## Additional Dependencies
- `rquests`
- `beautifulsoup`

## Estimated Processing Time
The processing time for the crawler is estimated twenty minutes.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/seychelles/seychelles.py`