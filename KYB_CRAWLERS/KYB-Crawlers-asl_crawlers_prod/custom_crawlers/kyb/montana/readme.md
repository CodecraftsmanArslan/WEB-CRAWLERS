# Crawler: Montana

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Montana Secretary of State, Business Services Division](https://biz.sosmt.gov/search/business). The script use undetected selenium driver to get the data HTML page, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports".

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "EMCC, INC.",
  "status": "Voluntary Withdrawal",
  "meta_detail": {
    "subtype": "General For Profit Corporation",
    "qualified_date": "31-03-2000",
    "annual_return_due_date": "15-04-2010",
    "registered_in_jurisdiction_date": "09-12-1993"
  },
  "country_name": "Montana",
  "crawler_name": "custom_crawlers.kyb.montana.montana.py",
  "jurisdiction": "Delaware",
  "inactive_date": "14-01-2010",
  "fillings_detail": [
    {
      "date": "14-01-2010",
      "title": "Articles of Dissolution (VOLUNTARY DISS OR WITHDRAWAL)",
      "filing_type": "Articles of Dissolution (VOLUNTARY DISS OR WITHDRAWAL)",
      "meta_detail": {
        "delayed_effective_date": "22-01-2010"
      },
      "filling_code": "396794"
    },
    {
      "date": "14-01-2010",
      "title": "Comment (WITHDRAWL SERV OF PROC ADDRESS 4343 N SCOTTSDALE RD STE 270 SCOTTSDALE AZ 85251 OLD AGENT CORPORATION SERVICE COMPANY)",
      "filing_type": "Comment (WITHDRAWL SERV OF PROC ADDRESS 4343 N SCOTTSDALE RD STE 270 SCOTTSDALE AZ 85251 OLD AGENT CORPORATION SERVICE COMPANY)",
      "meta_detail": {
        "delayed_effective_date": "22-01-2010"
      },
      "filling_code": "396794"
    },
    {
      "date": "14-01-2010",
      "title": "Amendment (REGISTERED AGENT ADDRESS)",
      "filing_type": "Amendment (REGISTERED AGENT ADDRESS)",
      "meta_detail": {
        "delayed_effective_date": "22-01-2010"
      },
      "filling_code": "396794"
    },
    {
      "date": "14-01-2010",
      "title": "Amendment (REGISTERED AGENT NAME)",
      "filing_type": "Amendment (REGISTERED AGENT NAME)",
      "meta_detail": {
        "delayed_effective_date": "22-01-2010"
      },
      "filling_code": "396794"
    },
    {
      "date": "12-03-2009",
      "title": "Annual Report 2009 (2009 E-FILED)",
      "filing_type": "Annual Report 2009 (2009 E-FILED)",
      "meta_detail": {
        "delayed_effective_date": "12-03-2009"
      },
      "filling_code": "380550"
    },
    {
      "date": "04-04-2008",
      "title": "Annual Report 2008 (2008 E-FILED)",
      "filing_type": "Annual Report 2008 (2008 E-FILED)",
      "meta_detail": {
        "delayed_effective_date": "04-04-2008"
      },
      "filling_code": "362527"
    },
    {
      "date": "09-04-2007",
      "title": "Annual Report 2007 (2007 E-FILED)",
      "filing_type": "Annual Report 2007 (2007 E-FILED)",
      "meta_detail": {
        "delayed_effective_date": "09-04-2007"
      },
      "filling_code": "340580"
    },
    {
      "date": "07-04-2006",
      "title": "Annual Report 2006 (2006)",
      "filing_type": "Annual Report 2006 (2006)",
      "meta_detail": {
        "delayed_effective_date": "12-05-2006"
      },
      "filling_code": "323247"
    },
    {
      "date": "01-07-2005",
      "title": "Comment (ABN REG--RESORT MANAGEMENT INTERNATIONAL--A9124(3))",
      "filing_type": "Comment (ABN REG--RESORT MANAGEMENT INTERNATIONAL--A9124(3))",
      "meta_detail": {
        "delayed_effective_date": "15-07-2005"
      },
      "filling_code": "124091"
    },
    {
      "date": "13-04-2005",
      "title": "Annual Report 2005 (2005)",
      "filing_type": "Annual Report 2005 (2005)",
      "meta_detail": {
        "delayed_effective_date": "18-05-2005"
      },
      "filling_code": "304578"
    },
    {
      "date": "09-07-2004",
      "title": "Annual Report 2004 (REGISTERED AGENT ADDRESS)",
      "filing_type": "Annual Report 2004 (REGISTERED AGENT ADDRESS)",
      "meta_detail": {
        "delayed_effective_date": "18-08-2004"
      },
      "filling_code": "289687"
    },
    {
      "date": "09-07-2004",
      "title": "Annual Report 2004 (2004)",
      "filing_type": "Annual Report 2004 (2004)",
      "meta_detail": {
        "delayed_effective_date": "18-08-2004"
      },
      "filling_code": "289687"
    },
    {
      "date": "09-07-2004",
      "title": "Annual Report 2004 (REGISTERED AGENT NAME)",
      "filing_type": "Annual Report 2004 (REGISTERED AGENT NAME)",
      "meta_detail": {
        "delayed_effective_date": "18-08-2004"
      },
      "filling_code": "289687"
    },
    {
      "date": "02-04-2003",
      "title": "Annual Report 2003 (2003)",
      "filing_type": "Annual Report 2003 (2003)",
      "meta_detail": {
        "delayed_effective_date": "06-06-2003"
      },
      "filling_code": "268755"
    },
    {
      "date": "08-04-2002",
      "title": "Annual Report 2002 (2002)",
      "filing_type": "Annual Report 2002 (2002)",
      "meta_detail": {
        "delayed_effective_date": "02-08-2002"
      },
      "filling_code": "253306"
    },
    {
      "date": "15-04-2001",
      "title": "Annual Report 2001 (2001)",
      "filing_type": "Annual Report 2001 (2001)",
      "meta_detail": {
        "delayed_effective_date": "24-04-2001"
      },
      "filling_code": "665340"
    },
    {
      "date": "24-07-2000",
      "title": "Comment (ABN REGISTRATION--D.B.A. RESORT MANAGEMENT INTERNATIONAL --A6154(3))",
      "filing_type": "Comment (ABN REGISTRATION--D.B.A. RESORT MANAGEMENT INTERNATIONAL --A6154(3))",
      "meta_detail": {
        "delayed_effective_date": "17-08-2000"
      },
      "filling_code": "81582"
    },
    {
      "date": "24-07-2000",
      "title": "Amendment (ASSUMED BUSINESS NAME)",
      "filing_type": "Amendment (ASSUMED BUSINESS NAME)",
      "meta_detail": {
        "delayed_effective_date": "17-08-2000"
      },
      "filling_code": "81582"
    },
    {
      "date": "31-03-2000",
      "title": "Initial Filing",
      "filing_type": "Initial Filing",
      "filling_code": "238511"
    }
  ],
  "addresses_detail": [
    {
      "type": "mailing_address",
      "address": "4343 N. SCOTTSDALE RD STE 270, SCOTTSDALE, AZ 85251"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "url": "https://biz.sosmt.gov/search/business?prefill=A081582",
          "title": "D.B.A. RESORT MANAGEMENT INTERNATIONAL (A081582)"
        },
        {
          "url": "https://biz.sosmt.gov/search/business?prefill=A124091",
          "title": "RESORT MANAGEMENT INTERNATIONAL (A124091)"
        },
        {
          "url": "https://biz.sosmt.gov/search/business?prefill=A124091",
          "title": "RESORT MANAGEMENT INTERNATIONAL (A124091)"
        },
        {
          "url": "https://biz.sosmt.gov/search/business?prefill=A124091",
          "title": "RESORT MANAGEMENT INTERNATIONAL (A124091)"
        }
      ],
      "type": "active/inactive_abn_and_tm"
    }
  ],
  "registration_date": "31-03-2000",
  "registration_number": "F034904"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to get HTML data from results page and then use `beautifulsoup` to parse and extract required information.

## Additional Dependencies
- `selenium`
- `beautifulsoup4`
- `undetected chrome browser`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/montana/montana.py`