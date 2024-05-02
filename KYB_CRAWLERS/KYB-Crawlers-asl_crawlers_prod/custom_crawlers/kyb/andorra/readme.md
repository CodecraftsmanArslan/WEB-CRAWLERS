# Crawler: Andorra

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [OFFICE OF TRADEMARKS AND PATENTS OF THE PRINCIPALITY OF ANDORRA](https://aplicacions.govern.ad/OMPA/RegistreResultats). The script fetches pdf from the source using selenium automation, extract data from it using pdfplumber and beautifulsoup, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "THE PILLSBURY COMPANY",
  "status": "Caducat",
  "meta_detail": {
    "expiry_date": "16-03-2005",
    "power_of_attorney_number": "960101"
  },
  "country_name": "Andorra",
  "crawler_name": "custom_crawlers.kyb.andorra.andorra.py",
  "people_detail": [
    {
      "name": "THE PILLSBURY COMPANY",
      "address": "PILLSBURY CENTER , 200 SOUTH 6TH STREET MINNEAPOLIS, MINNESOTA 55402 ESTATS UNITS",
      "designation": "owner",
      "meta_detail": {
        "type": "SOCIETAT ESTAT DE DELAWARE"
      }
    }
  ],
  "fillings_detail": [
    {
      "date": "05-12-1996",
      "title": "REGISTRE DE MARCA"
    },
    {
      "date": "16-03-2005",
      "title": "CESSIÓ (NOU REGISTRE DE MARCA 21554)"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "registration_number": "1329911",
          "date_of_registration": "06-11-1985",
          "country_where_the_registration_was_made": "FRANÇA",
          "products_services_for_which_priorty_is_claimed": "TOTS ELS QUE FIGUREN EN LA SOL·LICITUD"
        }
      ],
      "type": "property_right_claim_info"
    }
  ],
  "registration_date": "05-12-1996",
  "registration_number": "52"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to crawl, `beautifulsoup` and `pdfplumber` for scraping.

## Additional Dependencies
- `pdfplumber`
- `bs4` (BeautifulSoup)
- `selenium`

## Estimated Processing Time
The processing time for the crawler is estimated 15 days.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 kyb_crawlers/custom_crawlers/kyb/andorra/andorra.py`