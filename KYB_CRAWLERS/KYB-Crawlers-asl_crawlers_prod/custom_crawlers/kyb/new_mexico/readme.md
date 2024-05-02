# Crawler: New Mexico

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [New Mexico Secretary of State Business Services Division](https://portal.sos.state.nm.us/BFS/online/CorporationBusinessSearch). The script use selenium driver to get the data HTML page, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports". There are two scripts, one for companies and other for partnership and both use the same approach.

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"company_data": {
  "name": "TAYLORMADE ENTERPRISES LLC",
  "type": "Domestic Limited Liability Company",
  "status": "Active",
  "meta_detail": {
    "standing": "Good Standing",
    "state_law_code": "53-19-1 to 53-19-74"
  },
  "country_name": "New Mexico",
  "crawler_name": "custom_crawlers.kyb.new_mexico.new_mexico.py",
  "jurisdiction": "New Mexico",
  "people_detail": [
    {
      "name": "BASIL HUBBELL",
      "address": "213 W MAIN ST, FARMINGTON, NM  87401",
      "designation": "registered_agent",
      "appointment_date": "04-05-2015"
    },
    {
      "name": "BASIL HUBBELL",
      "address": "NM",
      "designation": "Organizer"
    },
    {
      "name": "HILLARY A HUBBELL",
      "address": "NM",
      "designation": "Organizer"
    }
  ],
  "fillings_detail": [
    {
      "date": "04-05-2015",
      "title": "TAYLORMADE ENTERPRISES",
      "filing_code": "979291",
      "filing_type": "Certificate Of Organization",
      "meta_detail": {
        "entity": "",
        "post_mark": "",
        "processed_date": "13-05-2015",
        "fiscal_year_end_date": ""
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "principal_business_address",
      "address": "213 W MAIN ST, FARMINGTON, NM  87401"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "organization_date_in_new_mexico": "04-05-2015"
        }
      ],
      "type": "incorporation_date_information"
    },
    {
      "data": [
        {
          "duration_period": "Perpetual"
        }
      ],
      "type": "existence_and_purpose_information"
    }
  ],
  "registration_date": "",
  "incorporation_date": "",
  "registration_number": "5056411"
}
```

```json
"company_data": {
  "name": "1021 HENNEPIN ASSOCIATES, LIMITED PARTNERSHIP",
  "type": "New Mexico Limited Partnership",
  "status": "Active",
  "meta_detail": {
    "duration": "Perpetual",
    "additonal_detail": [
      {
        "name": "BGK EQUITIES INC.",
        "type": "memo_information",
        "address": "330 GARFIELD ST. STE. 200, SANTA FE, NM  USA",
        "postal_address": ""
      }
    ],
    "registartion_date": "13-01-1997"
  },
  "country_name": "New Mexico",
  "crawler_name": "custom_crawlers.kyb.new_mexico.new_mexico_ps.py",
  "people_detail": [
    {
      "name": "EDWARD M. GILBERT",
      "address": "330 GARFIELD ST. STE. 200, SANTA FE, NM  USA",
      "designation": "registered_agent"
    },
    {
      "name": "BGK EQUITIES INC.",
      "address": "330 GARFIELD ST. STE. 200, SANTA FE, NM  USA",
      "designation": "partner"
    }
  ],
  "fillings_detail": [
    {
      "date": "13-01-1997",
      "filing_code": "6605",
      "filing_type": "Business Formation"
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": "330 GARFIELD ST. STE. 200, SANTA FE, NM  USA"
    }
  ],
  "registration_number": "0806NM"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to get HTML data from results page and then use `beautifulsoup` to parse and extract required information for companies.

## Additional Dependencies
- `selenium`
- `beautifulsoup4`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/new_mexico/new_mexico_co.py`
5. Run the script: `python3 custom_crawlers/kyb/new_mexico/new_mexico_ps.py`