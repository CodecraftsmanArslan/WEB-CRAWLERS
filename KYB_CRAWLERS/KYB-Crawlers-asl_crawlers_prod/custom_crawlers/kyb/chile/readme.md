# Crawler: Chile

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Open Data portal, Government of Chile](https://datos.gob.cl/km/dataset/registro-de-empresas-y-sociedades). The script fetches data from CSV, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "zonal consultores limitada",
  "meta_detail": {
    "capital": "2000000",
    "trade_code": "SRL",
    "approval_date": "25-06-2013",
    "approval_year": "2013",
    "governing_law": "CONSTITUCIÓN",
    "tax_id_number": "76290016-5",
    "approval_month": "Junio",
    "last_registration_date": "25-06-2013"
  },
  "country_name": "Chile",
  "crawler_name": "custom_crawlers.kyb.chile.chile_kyb",
  "addresses_detail": [
    {
      "type": "business_address",
      "address": "ALTO HOSPICIO, 1",
      "description": "",
      "meta_detail": { "country": "Chile" }
    },
    {
      "type": "tax_address",
      "address": "ALTO HOSPICIO, 1",
      "description": "",
      "meta_detail": { "country": "Chile" }
    }
  ],
  "registration_date": "25-06-2013",
  "registration_number": "5095"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` and `pandas`libraries for scraping data.

## Additional Dependencies
- `Request`
- `pandas`


## Estimated Processing Time
The processing time for the crawler is estimated 20 minniutes.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt` 
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the scrip for source 1: `python3 ASL-Crawlers/custom_crawlers/kyb/chile/chile_kyb.py`
