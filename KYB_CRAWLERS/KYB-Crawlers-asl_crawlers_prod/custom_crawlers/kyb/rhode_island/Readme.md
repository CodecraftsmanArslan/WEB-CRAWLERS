# Crawler: rhode_island_kyb

## Crawler Introduction
This Python script is an HTML crawler designed to extract information from the [Rhode Island Secretary of State website](https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearch.aspx). The script fetches data related to business entities, filings, and people from the specified API endpoint. Extracted data is processed and stored in a PostgreSQL database.

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `get_listed_object` and `prepare_data` to structure and prepare data for insertion into a PostgreSQL database.

### Sample Data Structure
```json
"data": {
  "name": "Cindy Salvato & Company, Inc.",
  "type": "Domestic Profit Corporation",
  "meta_detail": {
    "purpose": "CULINARY TOURISMTITLE: 7-1.1-51",
    "effective_date": "06-06-1996"
  },
  "country_name": "Rhode Island",
  "crawler_name": "Rhode Island Official Registry",
  "people_detail": [
    {
      "name": "PETER J. FURNESS, ESQ.",
      "address": "182 WATERMAN STREET PROVIDENCE, RI 02906 USA",
      "designation": "registered_agent"
    },
    {
      "name": "CYNTHIA JEAN SALVATO",
      "address": "80 HOPKINS AVE JOHNSTON, RI 02919 USA",
      "designation": "PRESIDENT"
    }
  ],
  "fillings_detail": [
    {
      "date": "10-18-2019",
      "title": "Revocation Certificate For Failure to File the Annual Report for the Year",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/1029/000202193/0024/201924562410_1.pdf",
      "filing_code": "201924562410"
    },
    {
      "date": "07-24-2019",
      "title": "Revocation Notice For Failure to File An Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0809/000196850/0040/201907003970_1.pdf",
      "filing_code": "201907003970"
    },
    {
      "date": "01-22-2018",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2018/0122/000000000/2974/201856470300_1.pdf",
      "filing_code": "201856470300",
      "meta_detail": {
        "year": "2018"
      }
    },
    {
      "date": "03-06-2017",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2017/0306/000000000/5719/201737461070_1.pdf",
      "filing_code": "201737461070",
      "meta_detail": {
        "year": "2017"
      }
    },
    {
      "date": "03-02-2016",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2016/0302/000000000/8461/201693592230_1.pdf",
      "filing_code": "201693592230",
      "meta_detail": {
        "year": "2016"
      }
    },
    {
      "date": "02-18-2015",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2015/0218/000000000/9888/201555244130_1.pdf",
      "filing_code": "201555244130",
      "meta_detail": {
        "year": "2015"
      }
    },
    {
      "date": "01-16-2014",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2014/0116/000000000/8855/201433077520_1.pdf",
      "filing_code": "201433077520",
      "meta_detail": {
        "year": "2014"
      }
    },
    {
      "date": "03-28-2013",
      "title": "Statement of Change of Registered/Resident Agent Office",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2013/0328/000090627/0018/201314514210_1.pdf",
      "filing_code": "201314514210"
    },
    {
      "date": "02-18-2013",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2013/0218/000000000/8420/201311881720_1.pdf",
      "filing_code": "201311881720",
      "meta_detail": {
        "year": "2013"
      }
    },
    {
      "date": "01-24-2012",
      "title": "Statement of Change of Registered/Resident Agent Office",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2012/0127/000072506/0008/201288575370_1.pdf",
      "filing_code": "201288575370"
    },
    {
      "date": "01-12-2012",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2012/0112/000000000/0335/201287922490_1.pdf",
      "filing_code": "201287922490",
      "meta_detail": {
        "year": "2012"
      }
    },
    {
      "date": "01-18-2011",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2011/0118/000000000/5028/201173559900_1.pdf",
      "filing_code": "201173559900",
      "meta_detail": {
        "year": "2011"
      }
    },
    {
      "date": "02-25-2010",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2010/0225/000000000/2836/201059411470_1.pdf",
      "filing_code": "201059411470",
      "meta_detail": {
        "year": "2010"
      }
    },
    {
      "date": "01-19-2010",
      "title": "Fictitious Business Name Statement",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2010/0119/000044123/0001/201056453040_1.pdf",
      "filing_code": "201056453040"
    },
    {
      "date": "02-26-2009",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2009/0226/000000000/5886/200943043890_1.pdf",
      "filing_code": "200943043890",
      "meta_detail": {
        "year": "2009"
      }
    },
    {
      "date": "01-11-2008",
      "title": "Annual Report",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2008/0111/000000000/9289/200805417340_1.pdf",
      "filing_code": "200805417340",
      "meta_detail": {
        "year": "2008"
      }
    },
    {
      "date": "01-25-2007",
      "title": "Annual Report",
      "meta_detail": {
        "year": "2007"
      }
    },
    {
      "date": "01-26-2006",
      "title": "Fictitious Business Name Statement",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0004/201989267420_1.pdf",
      "filing_code": "201989267420"
    },
    {
      "date": "03-22-2005",
      "title": "Annual Reports - Prior to 2006",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0005/201989267600_1.pdf",
      "filing_code": "201989267600",
      "meta_detail": {
        "year": "2005"
      }
    },
    {
      "date": "02-19-2004",
      "title": "Statement of Change of Registered/Resident Agent Office",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0006/201989267790_1.pdf",
      "filing_code": "201989267790"
    },
    {
      "date": "03-19-2002",
      "title": "Articles of Amendment",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0007/201989267880_1.pdf",
      "filing_code": "201989267880"
    },
    {
      "date": "03-11-2002",
      "title": "Statement of Change of Registered/Resident Agent",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0008/201989267970_1.pdf",
      "filing_code": "201989267970"
    },
    {
      "date": "02-20-2002",
      "title": "Revocation Notice",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0009/201989268030_1.pdf",
      "filing_code": "201989268030"
    },
    {
      "date": "01-08-2002",
      "title": "Revocation Notice",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0010/201989268120_1.pdf",
      "filing_code": "201989268120"
    },
    {
      "date": "01-03-2002",
      "title": "Agent Resigned",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0011/201989268210_1.pdf",
      "filing_code": "201989268210"
    },
    {
      "date": "12-29-1997",
      "title": "Statement of Change of Registered/Resident Agent",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0012/201989268580_1.pdf",
      "filing_code": "201989268580"
    },
    {
      "date": "12-29-1997",
      "title": "Fictitious Business Name Statement",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0013/201989268670_1.pdf",
      "filing_code": "201989268670"
    },
    {
      "date": "12-29-1997",
      "title": "Articles of Amendment",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0014/201989268300_1.pdf",
      "filing_code": "201989268300"
    },
    {
      "date": "10-31-1996",
      "title": "Statement of Change of Registered/Resident Agent",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0015/201989268850_1.pdf",
      "filing_code": "201989268850"
    },
    {
      "date": "06-06-1996",
      "title": "Articles of Incorporation",
      "file_url": "https://business.sos.ri.gov/CorpWeb/CorpSearch/CorpSearchRedirector.aspx?Action=PDF&Path=CORP_DRIVE1/2019/0327/000190126/0016/201989268940_1.pdf",
      "filing_code": "201989268940"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "80 HOPKINS AVENUE JOHNSTON, RI 02919 USA"
    }
  ],
  "dissolution_date": "10-18-2019",
  "additional_detail": [
    {
      "data": [
        {
          "stock_class": "CWP",
          "issued_share": "100",
          "share_per_value": "$ 0.0100",
          "authorized_share": "8,000"
        }
      ],
      "type": "share_information"
    },
    {
      "data": [
        {
          "naics_code": "561520 Tour Operators"
        }
      ],
      "type": "naics_code"
    },
    {
      "data": [
        {
          "date": "01-19-2010",
          "name": "Savoring Rhode Island",
          "description": "The fictitious name of:Savoring Rhode Island was filed on 01-19-2010"
        },
        {
          "date": "01-26-2006",
          "name": "R.I. MARKET TOURS",
          "description": "The fictitious name of:R.I. MARKET TOURS was filed on 01-26-2006"
        },
        {
          "date": "12-29-1997",
          "name": "The Dowry Cookie Company",
          "description": "The fictitious name of:The Dowry Cookie Company was filed on 12-29-1997"
        }
      ],
      "type": "fictitious_name_details"
    }
  ],
  "incorporation_date": "06-06-1996",
  "registration_number": "000089921",
  "previous_names_detail": [
    {
      "name": "The Dowry Collection, Incorporated",
      "update_date": "03-19-2002"
    },
    {
      "name": "The Dowry Cookie Company",
      "update_date": "12-29-1997"
    }
  ]
}
```

## Crawler Type
This is an HTML crawler that uses the requests library for making HTTP requests and BeautifulSoup for HTML parsing.

## Additional Dependencies
requests
beautifulsoup4


# Estimated Processing Time
The processing time for the crawler is 1 month.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/rhode_island/rhode_island.py`


