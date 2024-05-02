# Crawler: Yemen

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Federation of Yemen Chambers of Commerce and Industry (FYCCI)](https://fycci-ye.org/?act=dalil&dsearch=&dfeaa=&gov=&lang=en). The script use requests module to get HTML and beautifulsoup to parse and extract data, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "Ahmed Abdul Rahman Abdul Rahman Al-Awadi for import",
  "type": "Importing &Exporting",
  "industries": "General Import and Export of Local Products",
  "country_name": "Yemen",
  "crawler_name": "custom_crawlers.kyb.yemen.yemen.py",
  "jurisdiction": "Al-Hodaidah",
  "people_detail": [
    {
      "name": "Ahmed Abdul Rahman Abdul Rahman Al-Awadi",
      "designation": "owner"
    }
  ],
  "contacts_detail": [
    {
      "type": "phone_number",
      "value": "222225"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Sikat Al-Garabiah - صالح زيد العوادي, Al-Meena'a, Al-Hodaidah"
    }
  ],
  "registration_number": "78"
}
```

## Crawler Type
This is a web scraper crawler that uses the `requests` to get HTML and `beautifulsoup` to extract required information.

## Additional Dependencies
- `requests`
- `beautifulsoup`

## Estimated Processing Time
The processing time for the crawler is estimated < two hours.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/yemen/yemen.py`