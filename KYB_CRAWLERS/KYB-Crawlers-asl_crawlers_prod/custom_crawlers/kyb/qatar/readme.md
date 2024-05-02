# Crawler: Qatar

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Ministry of Commerce and Industry - Qatar Chamber ](https://qatarcid.com/). The script use requests module to get HTML data, use beautifulsoup4 to parse, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "QATAR GENRAL HOLDING",
  "type": "QATAR GENRAL HOLDING",
  "industries": "Share Investment",
  "meta_detail": {
    "qcci_number": "01-15549",
    "company_description": "Investing their money in stocks, bonds and securities"
  },
  "country_name": "Qatar",
  "crawler_name": "custom_crawlers.kyb.qatar.qatar.py",
  "jurisdiction": "Doha",
  "people_detail": [
    {
      "name": "HOSSAM ELREFAEI",
      "designation": "authorized_representative",
      "phone_number": "31010336"
    },
    {
      "name": "QATAR GENERAL INSURANCE & INSURANCE",
      "designation": "owner"
    }
  ],
  "contacts_detail": [
    {
      "type": "phone_number",
      "value": "44282222"
    },
    {
      "type": "email",
      "value": "metrash@qgirco.com"
    },
    {
      "type": "website",
      "value": "https://www.qgirco.com/ar/"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Area 4 - Street 880 - Building 23, 4500",
      "meta_detail": {
        "location": "7GCF+6R6, Doha, Qatar"
      }
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "day": "Monday :",
          "working_hours": "08:00-18:00"
        },
        {
          "day": "Tuesday :",
          "working_hours": "08:00-18:00"
        },
        {
          "day": "Wednesday :",
          "working_hours": "08:00-18:00"
        },
        {
          "day": "Thursday :",
          "working_hours": "08:00-18:00"
        },
        {
          "day": "Friday :",
          "working_hours": "Closed"
        },
        {
          "day": "Saturday :",
          "working_hours": "Closed"
        },
        {
          "day": "Sunday :",
          "working_hours": "08:00-18:00"
        }
      ],
      "type": "opening_hours"
    }
  ],
  "registration_number": "00038214"
}
```

## Crawler Type
This is a web scraper crawler that uses the `request` library to get HTML data and `beautifulsoup4` to extract required information.

## Additional Dependencies
- `requests`
- `beautifulsoup4`

## Estimated Processing Time
The processing time for the crawler is estimated < one week.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/qatar/qatar.py`