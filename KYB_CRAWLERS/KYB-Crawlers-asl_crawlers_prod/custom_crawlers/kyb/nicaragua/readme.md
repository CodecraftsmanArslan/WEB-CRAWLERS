# Crawler: Nicaragua

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Registro Público de la Propiedad](https://www.registropublico.gob.ni/Servicios/Consultas/ConsultaSociedad.aspx). The script use request to get the JSON data and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "DAYVIN ALEXANDER TRUJILLO RAYO",
  "status": "",
  "meta_detail": {
    "location": "ESTELI",
    "trade_name": "IMPORT-EXPORT T.R"
  },
  "country_name": "Nicaragua",
  "crawler_name": "custom_crawlers.kyb.nicaragua.nicaragua.py",
  "registration_number": "MC-XGPQAU"
}
```

## Crawler Type
This is a web scraper crawler that uses the `request` library to get API data and extract required information.

## Additional Dependencies
- `requests`

## Estimated Processing Time
The processing time for the crawler is estimated < one day.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/nicaragua/nicaragua.py`