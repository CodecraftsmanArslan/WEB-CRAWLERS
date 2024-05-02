# Crawler: Spain

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Comisión Nacional del Mercado de Valores (CNMV) - Ministry of Economy and Finance](https://sede.registradores.org/site/invitado/mercantil/busqueda). The script use selenium to get HTML data, beautifulsoup to extract, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "ANDBANK ESPAÑA BANCA PRIVADA SA",
  "status": "Vigente",
  "country_name": "Spain",
  "crawler_name": "custom_crawlers.kyb.spain.spain.py",
  "jurisdiction": "MADRID",
  "registration_number": "A58891672"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` to crawl and `beautifulsoup` to extract required information.

## Additional Dependencies
- `selenium`
- `beautifulsoup`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/spain/spain.py`