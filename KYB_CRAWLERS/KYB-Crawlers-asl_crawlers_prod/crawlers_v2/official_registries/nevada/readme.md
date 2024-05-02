# Crawler: Nevada

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [SilverFlume- Nevada Secretary of State, Commercial Recordings Division](https://esos.nv.gov/EntitySearch/OnlineEntitySearch). The script use undetected selenium driver to get the data HTML page, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports."
The script use Multiprocessing to get data 4x faster.

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "K AND S PROPERTIES, INC.",
  "type": "Domestic Corporation (78)",
  "status": "Permanently Revoked",
  "meta_detail": {
    "entity_number": "C18-1980",
    "annual_due_date": "1-31-2006"
  },
  "country_name": "Nevada",
  "crawler_name": "custom_crawlers.kyb.nevada.nevada_selenium.py",
  "inactive_date": "Perpetual",
  "people_detail": [
    {
      "name": "ANNI H. BUTLER",
      "address": "268 SPANISH DR., LAS VEGAS, NV, 89110, USA",
      "designation": "Non-Commercial Registered Agent",
      "meta_detail": {
        "status": "Active"
      }
    },
    {
      "name": "GORDON E STEWART",
      "address": "2305 BELMONT A, REDONDO BEACH, CA, 90278, USA",
      "designation": "President",
      "meta_detail": {
        "status": "Active",
        "last_updated": "01-28-2005"
      }
    },
    {
      "name": "ANNI H BUTLER",
      "address": "268 SPANISH DRIVE, LAS VEGAS, NV, 89110, USA",
      "designation": "Secretary",
      "meta_detail": {
        "status": "Active",
        "last_updated": "01-28-2005"
      }
    },
    {
      "name": "ANNI H BUTLER",
      "address": "268 SPANISH DRIVE, LAS VEGAS, NV, 89110, USA",
      "designation": "Treasurer",
      "meta_detail": {
        "status": "Active",
        "last_updated": "01-28-2005"
      }
    }
  ],
  "fillings_detail": [
    {
      "date": "03-14-2005",
      "title": "Annual List",
      "filing_code": "20050029426-60",
      "meta_detail": {
        "source": "Internal",
        "effective_date": "03-14-2005"
      }
    },
    {
      "date": "12-15-2003",
      "title": "Annual List",
      "filing_code": "C18-1980-002",
      "meta_detail": {
        "source": "Internal",
        "effective_date": "12-15-2003"
      }
    },
    {
      "date": "01-15-2003",
      "title": "Annual List",
      "filing_code": "C18-1980-009",
      "meta_detail": {
        "source": "Internal",
        "effective_date": "01-15-2003"
      }
    },
    {
      "date": "01-05-2002",
      "title": "Annual List",
      "filing_code": "C18-1980-007",
      "meta_detail": {
        "source": "Internal",
        "effective_date": "01-05-2002"
      }
    },
    {
      "date": "01-27-2001",
      "title": "Annual List",
      "filing_code": "C18-1980-010",
      "meta_detail": {
        "source": "Internal",
        "effective_date": "01-27-2001"
      }
    },
    {
      "date": "01-25-2000",
      "title": "Annual List",
      "filing_code": "C18-1980-012",
      "meta_detail": {
        "source": "Internal",
        "effective_date": "01-25-2000"
      }
    },
    {
      "date": "01-11-1999",
      "title": "Annual List",
      "filing_code": "C18-1980-008",
      "meta_detail": {
        "source": "Internal",
        "effective_date": "01-11-1999"
      }
    },
    {
      "date": "01-22-1998",
      "title": "Annual List",
      "filing_code": "C18-1980-011",
      "meta_detail": {
        "source": "Internal",
        "effective_date": "01-22-1998"
      }
    },
    {
      "date": "02-06-1995",
      "title": "Registered Agent-Statement of Change",
      "filing_code": "C18-1980-006",
      "meta_detail": {
        "source": "Internal",
        "effective_date": "02-06-1995"
      }
    },
    {
      "date": "07-15-1985",
      "title": "Registered Agent-Statement of Change",
      "filing_code": "C18-1980-005",
      "meta_detail": {
        "source": "Internal",
        "effective_date": "07-15-1985"
      }
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "no_par_value": "2500",
          "total_authorized_capital": "2,500"
        }
      ],
      "type": "shares_information"
    }
  ],
  "registration_date": "01-02-1980",
  "registration_number": "NV19801000053"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to get HTML data from results page and then use `beautifulsoup` to parse and extract required information for companies.

## Additional Dependencies
- `selenium`
- `beautifulsoup4`
- `undetected-chromedriver`
- `multiprocessing`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/nevada/nevada_selenium.py`