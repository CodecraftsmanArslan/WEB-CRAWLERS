# Crawler: Bolivia

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Bolivia Ministry of Productive Development and Plural Economy](https://miempresa.seprec.gob.bo/#/consulta-empresas?q=A). The script fetches data from the specified API endpoint by searching Alphabets and digit (0 to 9), processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "+ 18 HELADOS",
  "type": "EMPRESA UNIPERSONAL",
  "status": "MATRICULA ACTUALIZADA",
  "tax_number": "8311931015",
  "meta_detail": {
    "previous_registration_number": "00284138"},
  "country_name": "Bolivia",
  "crawler_name": "Bolivia Official Registry",
  "jurisdiction": "LA PAZ",
  "registration_number": "8311931015"
}
```

## Crawler Type
This is a web scraper crawler that use the `Request` library for scraping.

## Additional Dependencies
- `Request`

## Estimated Processing Time
The processing time for the crawler is estimated 3 days.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 ASL-Crawlers/crawlers_v2/official_registries/bolivia/bolivia.py`