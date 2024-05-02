# Crawler: Maine

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Maine Secretary of State, Bureau of Corporations](https://apps1.web.maine.gov/nei-sos-icrs/ICRS?MainPage=x). The script use requests module to fetch HTML data, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports." It uses multiprocessing to get data 4x faster.

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "Androscoggin savings bank",
  "type": "Bank corporation",
  "status": "Good standing",
  "country_name": "Maine",
  "crawler_name": "custom_crawlers.kyb.maine.maine.py",
  "jurisdiction": "MAINE",
  "inactive_date": "",
  "people_detail": [
    {
      "name": "NEIL KIELY",
      "address": "P.O. BOX 1407, LEWISTON, ME 04243 1407",
      "designation": "registered_agent"
    }
  ],
  "fillings_detail": [
    {
      "date": "03-05-1870",
      "title": "ARTICLES OF INCORPORATION"
    },
    {
      "date": "03-26-1965",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "08-25-1969",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "03-25-1970",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "03-23-1971",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "12-30-1971",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "11-08-1973",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "05-28-1974",
      "title": "CHANGE OF LEGAL NAME"
    },
    {
      "date": "03-15-1977",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "05-13-1977",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "10-24-1977",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "01-07-1982",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "06-02-1987",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "08-04-1988",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "10-12-1988",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "10-30-1990",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "03-12-1993",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "03-12-1993",
      "title": "APPOINTMENT OF CLERK AND REGISTERED OFFICE"
    },
    {
      "date": "02-15-1994",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "02-02-1995",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "03-22-1995",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "03-29-1995",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "05-12-1995",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "09-29-1995",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "02-12-1996",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "04-24-1996",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "08-22-1996",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "03-31-1997",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "04-01-1998",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "08-18-1998",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "11-13-1998",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "12-22-1998",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "01-08-1999",
      "title": "MERGER"
    },
    {
      "date": "01-08-1999",
      "title": "REORGANIZATION"
    },
    {
      "date": "01-08-1999",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "01-20-1999",
      "title": "MARK"
    },
    {
      "date": "01-20-1999",
      "title": "MARK"
    },
    {
      "date": "01-25-1999",
      "title": "MERGER"
    },
    {
      "date": "03-04-1999",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "10-22-1999",
      "title": "RESTATEMENT"
    },
    {
      "date": "02-29-2000",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "04-10-2001",
      "title": "CHANGE OF CLERK AND REGISTERED OFFICE"
    },
    {
      "date": "04-17-2001",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "04-17-2002",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "03-11-2003",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "09-23-2003",
      "title": "ASSUMED NAME"
    },
    {
      "date": "02-18-2004",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "11-29-2004",
      "title": "ORDER FROM BANKING"
    },
    {
      "date": "02-14-2005",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "03-07-2006",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "03-15-2006",
      "title": "MARK"
    },
    {
      "date": "03-02-2007",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "03-07-2008",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "08-18-2008",
      "title": "ASSUMED NAME"
    },
    {
      "date": "02-10-2009",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "01-12-2010",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "02-01-2011",
      "title": "ASSUMED NAME"
    },
    {
      "date": "02-28-2011",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "03-02-2011",
      "title": "CHANGE OF CLERK"
    },
    {
      "date": "02-23-2012",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "08-28-2012",
      "title": "RESTATEMENT"
    },
    {
      "date": "12-19-2012",
      "title": "ASSUMED NAME"
    },
    {
      "date": "02-01-2013",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "02-04-2014",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "02-18-2015",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "02-18-2016",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "02-03-2017",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "02-09-2018",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "03-01-2019",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "01-17-2020",
      "title": "CHANGE OF CLERK"
    },
    {
      "date": "05-29-2020",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "05-26-2021",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "05-31-2022",
      "title": "ANNUAL REPORT"
    },
    {
      "date": "05-09-2023",
      "title": "ANNUAL REPORT"
    }
  ],
  "addresses_detail": [
    {
      "type": "mailing_address",
      "address": "30 LISBON STREET , LEWISTON, ME 04240"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "name": "ANDROSCOGGIN BANK TRUST AND WEALTH MANAGEMENT",
          "type": "assumed"
        },
        {
          "name": "ANDROSCOGGIN TRUST",
          "type": "assumed"
        },
        {
          "name": "ANDROSCOGGIN BANK",
          "type": "assumed"
        },
        {
          "name": "ANDROSCOGGIN TRUST & INVESTMENT SERVICES",
          "type": "assumed"
        },
        {
          "name": "ANDROSCOGGIN COUNTY SAVINGS BANK",
          "type": "former"
        }
      ],
      "type": "other_name_information"
    }
  ],
  "incorporation_date": "03-05-1870",
  "registration_number": "18700000 b"
}
```

## Crawler Type
This is a web scraper crawler that uses the `requests` library to get HTML data and then use `beautifulsoup` to parse and extract required information.

## Additional Dependencies
- `requests`
- `beautifulsoup4`
- `multiprocessing`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/maine/maine.py`