# Crawler: New Zealand

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [New Zealand Companies Office](https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/search?q=&entityTypes=ALL&entityStatusGroups=ALL&incorpFrom=&incorpTo=&addressTypes=ALL&addressKeyword=&start=0&limit=15&sf=&sd=&advancedPanel=true&mode=advanced#results). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "AFFCO LIMITED",
  "type": "NZ Limited Company",
  "status": "Registered",
  "industries": "",
  "meta_detail": {
    "aliases": "No trading name",
    "ar_filing_month": "June",
    "business_number": "9429040751832",
    "constitution_filed": "Yes",
    "company_record_link": "https://app.companiesoffice.govt.nz/co/40960"
  },
  "country_name": "New Zealand",
  "crawler_name": "custom_crawlers.kyb.new_zealand.new_zealand_kyb.py",
  "people_detail": [
    {
      "name": "AFFCO HOLDINGS LIMITED",
      "address": "AFFCO Corporate Office, 6128 Great South Road, Hamilton, 3288, New Zealand",
      "designation": "shareholder",
      "meta_detail": {
        "share_allocation": "18482038 shares (100.00%)"
      }
    },
    {
      "name": "Samuel  LEWIS",
      "address": "72 Mangapiko School Road, Rd 6, Te Awamutu, 3876, New Zealand",
      "designation": "director",
      "consent_link": "javascript:goTo('/companies/app/ui/pages/companies/40960/documents');",
      "appointment_date": "02-27-2001"
    },
    {
      "name": "Rowan  Mcpherson OGG",
      "address": "49 Puflett Road, Havelock North, Havelock North, 4130, New Zealand",
      "designation": "director",
      "consent_link": "https://app.companiesoffice.govt.nz/companies/app/service/services/documents/2FCBC33CC49BC779E776F084AB199E0D",
      "appointment_date": "01-01-2015"
    }
  ],
  "contacts_detail": [
    {
      "type": "telephone_number",
      "value": "+64 7 8292888"
    },
    {
      "type": "email",
      "value": "legal@affco.co.nz"
    },
    {
      "type": "website_link",
      "value": "www.affco.co.nz"
    }
  ],
  "fillings_detail": [
    {
      "date": "06-19-2023",
      "title": "Annual Return Filed",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/35007627/entityFilingRequirement"
    },
    {
      "date": "06-14-2022",
      "title": "Annual Return Filed",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/33242263/entityFilingRequirement"
    },
    {
      "date": "06-09-2021",
      "title": "Annual Return Filed",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/31361417/entityFilingRequirement"
    },
    {
      "date": "06-09-2021",
      "title": "Particulars of Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/31361404/entityFilingRequirement"
    },
    {
      "date": "06-09-2021",
      "title": "Particulars of Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/31361392/entityFilingRequirement"
    },
    {
      "date": "06-09-2021",
      "title": "Particulars of Company Address",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/31361378/entityFilingRequirement"
    },
    {
      "date": "10-06-2020",
      "title": "Annual Return Filed",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/30108442/entityFilingRequirement"
    },
    {
      "date": "10-06-2020",
      "title": "Particulars of ultimate holding company",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/30108408/entityFilingRequirement"
    },
    {
      "date": "10-11-2019",
      "title": "Annual Return Filed",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/28426922/entityFilingRequirement"
    },
    {
      "date": "10-10-2018",
      "title": "Annual Return Filed",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/26617345/entityFilingRequirement"
    },
    {
      "date": "11-03-2017",
      "title": "Annual Return Filed",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/25110697/entityFilingRequirement"
    },
    {
      "date": "10-26-2016",
      "title": "Annual Return Filed",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/23544971/entityFilingRequirement"
    },
    {
      "date": "10-30-2015",
      "title": "Annual Return Filed",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/21893758/entityFilingRequirement"
    },
    {
      "date": "10-30-2015",
      "title": "Particulars of ultimate holding company",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/21893736/entityFilingRequirement"
    },
    {
      "date": "01-06-2015",
      "title": "Particulars of Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/20544503/entityFilingRequirement"
    },
    {
      "date": "01-06-2015",
      "title": "Particulars of Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/20543784/entityFilingRequirement"
    },
    {
      "date": "01-06-2015",
      "title": "Director Consent",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/20544476/entityFilingRequirement"
    },
    {
      "title": "Director Consent",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/service/services/documents/2FCBC33CC49BC779E776F084AB199E0D"
    },
    {
      "date": "10-09-2014",
      "title": "File Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/20252407/entityFilingRequirement"
    },
    {
      "date": "10-07-2013",
      "title": "File Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/18763977/entityFilingRequirement"
    },
    {
      "date": "04-12-2013",
      "title": "Particulars of Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/17993134/entityFilingRequirement"
    },
    {
      "date": "12-17-2012",
      "title": "File Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/17596014/entityFilingRequirement"
    },
    {
      "date": "10-11-2011",
      "title": "File Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/15863707/entityFilingRequirement"
    },
    {
      "date": "10-01-2010",
      "title": "File Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/14270270/entityFilingRequirement"
    },
    {
      "date": "02-12-2010",
      "title": "Online Particulars of Directors",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/10661868/entityFilingRequirement"
    },
    {
      "date": "02-12-2010",
      "title": "Consent of Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/10668361/entityFilingRequirement"
    },
    {
      "title": "Consent of Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/service/services/documents/29E79BCEC0AC149CC5115DDDC079B5EF"
    },
    {
      "date": "02-12-2010",
      "title": "Online Particulars of Directors",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/10661849/entityFilingRequirement"
    },
    {
      "date": "09-29-2009",
      "title": "Online Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/10233579/entityFilingRequirement"
    },
    {
      "date": "01-28-2009",
      "title": "Online Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/8643968/entityFilingRequirement"
    },
    {
      "date": "01-28-2009",
      "title": "Online Particulars Of Company Address",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/8644581/entityFilingRequirement"
    },
    {
      "date": "11-20-2007",
      "title": "Online Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/6458698/entityFilingRequirement"
    },
    {
      "date": "03-16-2007",
      "title": "Consent of Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/141886/entityFilingRequirement"
    },
    {
      "title": "Consent of Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/service/services/documents/804F38F899619A9E68E17F2073CB7D58"
    },
    {
      "date": "03-16-2007",
      "title": "Online Particulars of Directors",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/4994836/entityFilingRequirement"
    },
    {
      "date": "03-15-2007",
      "title": "Online Particulars of Directors",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/4994812/entityFilingRequirement"
    },
    {
      "date": "10-09-2006",
      "title": "Online Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/4168877/entityFilingRequirement"
    },
    {
      "date": "10-09-2006",
      "title": "Online Particulars Of Company Address",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/4169616/entityFilingRequirement"
    },
    {
      "date": "10-05-2005",
      "title": "Online Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/557215/entityFilingRequirement"
    },
    {
      "date": "10-01-2004",
      "title": "Online Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/13792320/entityFilingRequirement"
    },
    {
      "date": "09-27-2004",
      "title": "Online Particulars of Directors",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/4864091/entityFilingRequirement"
    },
    {
      "date": "02-02-2004",
      "title": "Online Particulars of Directors",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/2944489/entityFilingRequirement"
    },
    {
      "date": "02-02-2004",
      "title": "Consent Form - Newly Appointed Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/2950189/entityFilingRequirement"
    },
    {
      "title": "Consent Form - Newly Appointed Director",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/service/services/documents/8F522DB09D46791A6457AD25237611FA"
    },
    {
      "date": "02-02-2004",
      "title": "Online Particulars of Directors",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/2944488/entityFilingRequirement"
    },
    {
      "date": "11-06-2003",
      "title": "Online Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/1791044/entityFilingRequirement"
    },
    {
      "date": "12-06-2002",
      "title": "Online Particulars Of Company Address",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/12356417/entityFilingRequirement"
    },
    {
      "date": "10-11-2002",
      "title": "Online Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/12760176/entityFilingRequirement"
    },
    {
      "date": "07-01-2002",
      "title": "Online Particulars Of Company Address",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/12545022/entityFilingRequirement"
    },
    {
      "date": "04-23-2002",
      "title": "Particulars of Directors",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/11923957/entityFilingRequirement"
    },
    {
      "title": "Particulars of Directors",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/service/services/documents/E5044817D70AB2CAB67B7617275889EE"
    },
    {
      "date": "10-18-2001",
      "title": "Online Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/11931978/entityFilingRequirement"
    },
    {
      "date": "10-05-2000",
      "title": "Online Annual Return",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/10726231/entityFilingRequirement"
    },
    {
      "date": "04-17-1997",
      "title": "Adoption of Constitution on rereg",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/7100837/entityFilingRequirement"
    },
    {
      "title": "Adoption of Constitution on rereg",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/service/services/documents/B475FE022C295464D7361136FBCD49F0"
    },
    {
      "date": "08-31-1996",
      "title": "Amalgamation Certificate",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/40960/9762951/entityFilingRequirement"
    },
    {
      "title": "Amalgamation Certificate",
      "file_url": "https://app.companiesoffice.govt.nz/companies/app/service/services/documents/10E4DCCE9A32AC16DE6709F8511F3232"
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": "Affco Head Office, S H 1, Horotiu, Waikato\r\n, New Zealand"
    },
    {
      "type": "service_address",
      "address": "Affco Head Office, S H 1, Horotiu, Waikato\r\n, New Zealand"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "name": "AFFCO HOLDINGS LIMITED",
          "source_url": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/623635",
          "entity_type": "NZ Limited Company",
          "jurisdiction": "New Zealand",
          "business_number": "9429038715105",
          "registration_number": "623635"
        }
      ],
      "type": "holding_company_information"
    },
    {
      "data": [
        {
          "total_share": "18482038",
          "extensive_shareholding": "No"
        }
      ],
      "type": "shares_information"
    }
  ],
  "incorporation_date": "12-22-1903",
  "registration_number": "40960",
  "previous_names_detail": [
    {
      "name": "AFFCO NEW ZEALAND LIMITED",
      "meta_detail": {
        "inact_date": "11-24-1989"
      },
      "update_date": "09-30-1994"
    },
    {
      "name": "AUCKLAND FARMERS' FREEZING CO-OPERATIVE LIMITED",
      "meta_detail": {
        "inact_date": "10-30-1962"
      },
      "update_date": "11-24-1989"
    },
    {
      "name": "THE AUCKLAND FARMERS' FREEZING COMPANY LIMITED",
      "meta_detail": {
        "inact_date": "12-22-1903"
      },
      "update_date": "10-30-1962"
    }
  ]
}
```


## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to exceed one month.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/new_zealand/new_zealand_kyb.py`