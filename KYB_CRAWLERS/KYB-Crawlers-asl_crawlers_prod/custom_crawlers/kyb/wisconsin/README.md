# Crawler: Wisconsin

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Wisconsin Department of Financial Institutions](https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "A AAACE ASSOCIATED AUTO AGENCIES, INC.",
  "type": "Domestic Business",
  "status": "Administratively Dissolved",
  "meta_detail": {
    "status_date": "03-12-2013",
    "period_of_existence": "PER",
    "annual_report_requirements": "Business Corporations are required to file an Annual Report under s.180.1622 WI Statutes."
  },
  "country_name": "Wisconsin",
  "crawler_name": "custom_crawlers.kyb.wisconsin.wisconsin_kyb.py",
  "jurisdiction": "",
  "people_detail": [
    {
      "name": "ALLIED CORPORATE SERVICES, LLC",
      "address": "757 N. BROADWAY STE. 300 MILWAUKEE , WI 53202",
      "designation": "registered_agent"
    },
    {
      "name": "GREG GRISWOLD",
      "address": "5017 RISSER RD MADISON , WI 53705",
      "designation": "registered_agent"
    },
    {
      "name": "MARTIN D JOCZ",
      "address": "6655 INDUSTRIAL LOOP RD P O BOX 137 GREENDALE , WI 53129",
      "designation": "registered_agent"
    },
    {
      "name": "VIRGINIA LONTZ",
      "address": "312 E WISCONSIN AVE MILWAUKEE , WI 53202",
      "designation": "registered_agent"
    },
    {
      "name": "CAROL PFITZINGER",
      "address": "2137 N 74TH WAUWATOSA , WI 53213",
      "designation": "registered_agent"
    },
    {
      "name": "RICHARD A BETZ",
      "address": "7132 WEST BRADLEY ROAD MILWAUKEE , WI 53223",
      "designation": "registered_agent"
    },
    {
      "name": "CHRIS M CLEMENS",
      "address": "3535 W. WISCONSIN AVE. MILWAUKEE , WI 53208",
      "designation": "registered_agent"
    },
    {
      "name": "HARRY A BROWN",
      "address": "4234 N 76TH MILWAUKEE , WI 53222",
      "designation": "registered_agent"
    }
  ],
  "fillings_detail": [
    {
      "date": "07-06-2017",
      "title": "Organized",
      "description": "E-Form",
      "meta_detail": {
        "effective_date": "07-06-2017"
      }
    },
    {
      "date": "01-06-2019",
      "title": "Change of Registered Agent",
      "description": "OnlineForm 13",
      "meta_detail": {
        "effective_date": "01-06-2019"
      }
    },
    {
      "date": "07-01-2019",
      "title": "Delinquent",
      "description": "",
      "meta_detail": {
        "effective_date": "07-01-2019"
      }
    },
    {
      "date": "07-13-2020",
      "title": "Notice of Administrative Dissolution",
      "description": "RTND UNDELIVERABLE",
      "meta_detail": {
        "effective_date": "07-13-2020"
      }
    },
    {
      "date": "07-30-2020",
      "title": "Change of Registered Agent",
      "description": "OnlineForm 5",
      "meta_detail": {
        "effective_date": "07-30-2020"
      }
    },
    {
      "date": "07-30-2020",
      "title": "Restored to Good Standing",
      "description": "OnlineForm 5",
      "meta_detail": {
        "effective_date": "07-30-2020"
      }
    },
    {
      "date": "11-27-2020",
      "title": "Change of Registered Agent",
      "description": "FM13-E-Form",
      "meta_detail": {
        "effective_date": "11-27-2020"
      }
    },
    {
      "date": "07-01-2022",
      "title": "Delinquent",
      "description": "",
      "meta_detail": {
        "effective_date": "07-01-2022"
      }
    },
    {
      "date": "09-12-1986",
      "title": "Incorporated/Qualified/Registered",
      "description": "",
      "meta_detail": {
        "effective_date": "09-12-1986"
      }
    },
    {
      "date": "07-01-1988",
      "title": "In Bad Standing",
      "description": "****RECORD IMAGED****",
      "meta_detail": {
        "effective_date": "07-01-1988"
      }
    },
    {
      "date": "06-11-1991",
      "title": "Notice of Administrative Dissolution",
      "description": "",
      "meta_detail": {
        "effective_date": "06-11-1991"
      }
    },
    {
      "date": "08-15-1991",
      "title": "Restored to Good Standing",
      "description": "",
      "meta_detail": {
        "effective_date": "08-15-1991"
      }
    },
    {
      "date": "07-01-1993",
      "title": "Delinquent",
      "description": "",
      "meta_detail": {
        "effective_date": "07-01-1993"
      }
    },
    {
      "date": "10-08-1993",
      "title": "Notice of Administrative Dissolution",
      "description": "932161713",
      "meta_detail": {
        "effective_date": "10-08-1993"
      }
    },
    {
      "date": "12-14-1993",
      "title": "Administrative Dissolution",
      "description": "932190030",
      "meta_detail": {
        "effective_date": "12-14-1993"
      }
    },
    {
      "date": "04-29-1996",
      "title": "Incorporated/Qualified/Registered",
      "description": "",
      "meta_detail": {
        "effective_date": "04-29-1996"
      }
    },
    {
      "date": "03-13-1998",
      "title": "Change of Registered Agent",
      "description": "FM 16 1997",
      "meta_detail": {
        "effective_date": "03-13-1998"
      }
    },
    {
      "date": "07-23-1999",
      "title": "Change of Registered Agent",
      "description": "FM 16 1999",
      "meta_detail": {
        "effective_date": "07-23-1999"
      }
    },
    {
      "date": "04-01-2001",
      "title": "Delinquent",
      "description": "***RECORD IMAGED***",
      "meta_detail": {
        "effective_date": "04-01-2001"
      }
    },
    {
      "date": "04-14-2008",
      "title": "Notice of Administrative Dissolution",
      "description": "",
      "meta_detail": {
        "effective_date": "04-14-2008"
      }
    },
    {
      "date": "06-16-2008",
      "title": "Administrative Dissolution",
      "description": "",
      "meta_detail": {
        "effective_date": "06-16-2008"
      }
    },
    {
      "date": "02-14-1979",
      "title": "Incorporated/Qualified/Registered",
      "description": "",
      "meta_detail": {
        "effective_date": "02-14-1979"
      }
    },
    {
      "date": "01-01-1982",
      "title": "In Bad Standing",
      "description": "",
      "meta_detail": {
        "effective_date": "01-01-1982"
      }
    },
    {
      "date": "04-17-1986",
      "title": "Intent to Involuntary",
      "description": "",
      "meta_detail": {
        "effective_date": "04-17-1986"
      }
    },
    {
      "date": "07-16-1986",
      "title": "Involuntary Dissolution",
      "description": "",
      "meta_detail": {
        "effective_date": "07-16-1986"
      }
    },
    {
      "date": "01-01-1981",
      "title": "In Bad Standing",
      "description": "",
      "meta_detail": {
        "effective_date": "01-01-1981"
      }
    },
    {
      "date": "08-02-1988",
      "title": "Intent to Involuntary",
      "description": "",
      "meta_detail": {
        "effective_date": "08-02-1988"
      }
    },
    {
      "date": "11-01-1988",
      "title": "Involuntary Dissolution",
      "description": "",
      "meta_detail": {
        "effective_date": "11-01-1988"
      }
    },
    {
      "date": "04-21-1965",
      "title": "Incorporated/Qualified/Registered",
      "description": "",
      "meta_detail": {
        "effective_date": "04-21-1965"
      }
    },
    {
      "date": "01-01-1968",
      "title": "In Bad Standing",
      "description": "****RECORD IMAGED****",
      "meta_detail": {
        "effective_date": "01-01-1968"
      }
    },
    {
      "date": "11-24-1969",
      "title": "Restored to Good Standing",
      "description": "",
      "meta_detail": {
        "effective_date": "11-24-1969"
      }
    },
    {
      "date": "01-13-1986",
      "title": "Change of Registered Agent",
      "description": "",
      "meta_detail": {
        "effective_date": "01-13-1986"
      }
    },
    {
      "date": "04-01-1989",
      "title": "In Bad Standing",
      "description": "",
      "meta_detail": {
        "effective_date": "04-01-1989"
      }
    },
    {
      "date": "04-27-1993",
      "title": "Notice of Administrative Dissolution",
      "description": "932080205",
      "meta_detail": {
        "effective_date": "04-27-1993"
      }
    },
    {
      "date": "07-02-1993",
      "title": "Administrative Dissolution",
      "description": "932120093",
      "meta_detail": {
        "effective_date": "07-02-1993"
      }
    },
    {
      "date": "03-28-1988",
      "title": "Incorporated/Qualified/Registered",
      "description": "",
      "meta_detail": {
        "effective_date": "03-28-1988"
      }
    },
    {
      "date": "04-19-1993",
      "title": "Change of Registered Agent",
      "description": "",
      "meta_detail": {
        "effective_date": "04-15-1993"
      }
    },
    {
      "date": "01-01-1996",
      "title": "Delinquent",
      "description": "",
      "meta_detail": {
        "effective_date": "01-01-1996"
      }
    },
    {
      "date": "04-15-1996",
      "title": "Notice of Administrative Dissolution",
      "description": "962030001",
      "meta_detail": {
        "effective_date": "04-15-1996"
      }
    },
    {
      "date": "06-20-1996",
      "title": "Administrative Dissolution",
      "description": "962041056",
      "meta_detail": {
        "effective_date": "06-20-1996"
      }
    },
    {
      "date": "02-03-2005",
      "title": "Restored to Good Standing",
      "description": "",
      "meta_detail": {
        "effective_date": "01-28-2005"
      }
    },
    {
      "date": "02-03-2005",
      "title": "Certificate of Reinstatement",
      "description": "",
      "meta_detail": {
        "effective_date": "01-28-2005"
      }
    },
    {
      "date": "02-03-2005",
      "title": "Change of Registered Agent",
      "description": "FM 12 2004",
      "meta_detail": {
        "effective_date": "01-28-2005"
      }
    },
    {
      "date": "07-11-2005",
      "title": "Change of Registered Agent",
      "description": "FM 12 2005",
      "meta_detail": {
        "effective_date": "07-11-2005"
      }
    },
    {
      "date": "05-29-2013",
      "title": "Change of Registered Agent",
      "description": "FM12-2013",
      "meta_detail": {
        "effective_date": "05-29-2013"
      }
    },
    {
      "date": "12-07-2016",
      "title": "Change of Registered Agent",
      "description": "OnlineForm 13",
      "meta_detail": {
        "effective_date": "12-07-2016"
      }
    },
    {
      "date": "01-01-2021",
      "title": "Delinquent",
      "description": "",
      "meta_detail": {
        "effective_date": "01-01-2021"
      }
    },
    {
      "date": "01-14-2022",
      "title": "Notice of Administrative Dissolution",
      "description": "",
      "meta_detail": {
        "effective_date": "01-14-2022"
      }
    },
    {
      "date": "03-16-2022",
      "title": "Administrative Dissolution",
      "description": "",
      "meta_detail": {
        "effective_date": "03-16-2022"
      }
    },
    {
      "date": "03-28-1972",
      "title": "Incorporated/Qualified/Registered",
      "description": "",
      "meta_detail": {
        "effective_date": "03-28-1972"
      }
    },
    {
      "date": "03-29-2006",
      "title": "Change of Registered Agent",
      "description": "FM16-E-Form***RECORD IMAGED***",
      "meta_detail": {
        "effective_date": "03-29-2006"
      }
    },
    {
      "date": "06-02-2009",
      "title": "Change of Registered Agent",
      "description": "FM16-E-Form",
      "meta_detail": {
        "effective_date": "06-02-2009"
      }
    },
    {
      "date": "01-01-2012",
      "title": "Delinquent",
      "description": "",
      "meta_detail": {
        "effective_date": "01-01-2012"
      }
    },
    {
      "date": "01-07-2013",
      "title": "Notice of Administrative Dissolution",
      "description": "",
      "meta_detail": {
        "effective_date": "01-07-2013"
      }
    },
    {
      "date": "03-12-2013",
      "title": "Administrative Dissolution",
      "description": "",
      "meta_detail": {
        "effective_date": "03-12-2013"
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": "PO BOX 12054 MILWAUKEE , WI 53212"
    },
    {
      "type": "office_address",
      "address": "3202 W BELTLINE HWY MIDDLETON , WI 53562 United States of America"
    },
    {
      "type": "office_address",
      "address": "6655 INDUSTRIAL LOOP RD GREENDALE , WI 53129 United States of America"
    },
    {
      "type": "office_address",
      "address": "161 W. WISCONSIN AVE SUITE 3054 MILWAUKEE , WI 00000 United States of America"
    },
    {
      "type": "office_address",
      "address": "7132 W BRADLEY MILWAUKEE , WI 53223 United States of America"
    },
    {
      "type": "office_address",
      "address": "3535 W WISCONSIN AVE MILWAUKEE , WI 53208"
    },
    {
      "type": "office_address",
      "address": "4234 N 76TH ST MILWAUKEE , WI 53222 United States of America"
    }
  ],
  "registration_date": "03-28-1972",
  "incorporation_date": "",
  "registration_number": "1A08866"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler is expected to complete processing in just a few hours.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/wisconsin/wisconsin_kyb.py`