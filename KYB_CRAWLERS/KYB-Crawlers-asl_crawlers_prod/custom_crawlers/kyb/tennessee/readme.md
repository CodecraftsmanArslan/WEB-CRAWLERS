# Crawler: Tennessee

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Tennessee Secretary of State](https://tnbear.tn.gov/Ecommerce/FilingSearch.aspx). The script use selenium to get and extract data, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "ABC CONTRACTORS, INC.",
  "status": "Inactive - Revoked (Revenue)",
  "meta_detail": {
    "formrd_in": "06-19-1973",
    "fiscal_year": "June",
    "stock_share": "500",
    "term_of_duration": "Perpetual",
    "obligated_member_entity": "No",
    "accounts_receivable_date": "10-01-1988",
    "accounts_receivable_exempt": "No"
  },
  "country_name": "Tennessee",
  "crawler_name": "custom_crawlers.kyb.tennessee.tennessee_kyb.py",
  "inactive_date": "12-31-1987",
  "people_detail": [
    {
      "name": "BURTON, JOE C",
      "address": "ST UNKNOWN MT JULIET, TN 37122 USA",
      "designation": "registered_agent"
    }
  ],
  "fillings_detail": [
    {
      "date": "07-01-1981",
      "description": "",
      "filing_type": "1981 Annual Report Due 07/01/1981",
      "meta_detail": {
        "image_number": "321 00192"
      }
    },
    {
      "date": "10-04-1980",
      "description": "",
      "filing_type": "Dissolution/Revocation - Revenue",
      "meta_detail": {
        "image_number": "178 00803"
      }
    },
    {
      "date": "07-01-1980",
      "description": "",
      "filing_type": "1980 Annual Report Due 07/01/1980",
      "meta_detail": {
        "image_number": "440 02083"
      }
    },
    {
      "date": "04-23-1975",
      "description": "",
      "filing_type": "1974 Annual Report Due 04/23/1975",
      "meta_detail": {
        "image_number": "197505502"
      }
    },
    {
      "date": "06-19-1973",
      "description": "",
      "filing_type": "Initial Filing",
      "meta_detail": {
        "image_number": "BC07P2076"
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": "STREET UNKNOWN MT. JULIET, TN 00000 USA"
    },
    {
      "type": "postal_address",
      "address": "STREET UNKNOWN MT. JULIET, TN 00000 USA"
    }
  ],
  "registration_date": "06-19-1973",
  "registration_number": "000000005"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` to crawl and extract required information.

## Additional Dependencies
- `selenium`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/tennessee/tennessee_kyb.py`