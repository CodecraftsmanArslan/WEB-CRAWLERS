# Crawler: Netherlands

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Kamer van Koophandel (Chamber of Commerce)](https://www.kvk.nl/lei/zoeken/). The first script use selenium driver to get the data HTML page, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports" for companies. The second one use requests module to get the API data in JSON format and and inserts relevant information into a PosgreSQL data table named "reports." for LEI.

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "MoRe Care",
  "status": "Uitgeschreven uit het Handelsregister",
  "meta_detail": {
    "description": "51642255 0000 000021650543 MoRe Care Overige paramedische praktijken (geen fysiotherapie en psychologie) en alternatieve genezers Eenmanszaak Hulpverlening in de zorg. ...",
    "location_number": "000021650543"
  },
  "country_name": "Netherlands",
  "crawler_name": "custom_crawlers.kyb.netherlands.netherlands.py",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Oude Koningstraat 4 A 6655AN Puiflijk"
    }
  ],
  "registration_number": "51642255"
}
```

```json
"lei_data": {
  "name": "Pajong B.V.",
  "type": "Besloten Vennootschap",
  "status": "ACTIVE",
  "meta_detail": {
    "lei_status": "ISSUED",
    "last_edited_date": "2022-11-24",
    "next_renewal_date": "2023-11-22",
    "chamber_of_commerce_number": "32043945"
  },
  "country_name": "Netherlands",
  "crawler_name": "custom_crawlers.kyb.netherlands.netherlands_lei.py",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Bussummerweg 37 1261BZ Blaricum"
    }
  ],
  "registration_date": "2017-11-22",
  "registration_number": "7245009ZL2U20QOX1U84"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to get HTML data from results page and then use `beautifulsoup` to parse and extract required information for companies. For LEI data this crawler use `requests` module to get LEI data in json format.

## Additional Dependencies
- `selenium`
- `beautifulsoup4`
- `requests`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/netherlands/netherlands.py`
5. Run the script: `python3 custom_crawlers/kyb/netherlands/netherlands_lei.py`