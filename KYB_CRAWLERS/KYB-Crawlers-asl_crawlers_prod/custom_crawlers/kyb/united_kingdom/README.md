# Crawler: Crawler for United Kingdom (England, Scotland, wales, Northern Ireland)

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Companies House United Kingdom](https://find-and-update.company-information.service.gov.uk/company/).The script initially downloads a zip file, extracts its contents, loads a CSV file to obtain company IDs, and then proceeds to make API calls, as part of the search process, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports"

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "! LTD",
  "type": "Private limited Company",
  "status": "Active",
  "country_name": "United Kingdom",
  "crawler_name": "crawlers.custom_crawlers.kyb.united_kingdom.united_kingdom_kyb",
  "people_detail": [
    {
      "name": "FELDMAN, Marc",
      "address": "9 Princes Square, Harrogate, England, HG1 1ND",
      "designation": "Director",
      "meta_detail": {
        "occupation": "Director",
        "date_of_birth": "December 1961",
        "residence_country": "United Kingdom"
      },
      "nationality": "British",
      "appointment_date": "09-11-2012",
      "termination_date": ""
    }
  ],
  "fillings_detail": [
    {
      "date": "07-24-2023",
      "title": "Registered office address changed",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzM4NzIwOTIxNWFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AD01",
      "filing_type": "Change of registered office address"
    },
    {
      "date": "06-27-2023",
      "title": "Accounts for a dormant company",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzM4NDE5ODAxNWFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AA",
      "filing_type": "Annual Accounts"
    },
    {
      "date": "10-10-2022",
      "title": "Confirmation statement",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzM1NDUyNTU2MGFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "CS01",
      "filing_type": ""
    },
    {
      "date": "05-11-2022",
      "title": "Accounts for a dormant company",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzMzODgwNDE5OWFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AA",
      "filing_type": "Annual Accounts"
    },
    {
      "date": "12-15-2021",
      "title": "Notification",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzMyMzQ0Nzk4NWFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "PSC01",
      "filing_type": ""
    },
    {
      "date": "12-13-2021",
      "title": "Withdrawal",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzMyMzQ0Nzk3MWFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "PSC09",
      "filing_type": ""
    },
    {
      "date": "10-26-2021",
      "title": "Confirmation statement",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzMxODAwMjMyNWFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "CS01",
      "filing_type": ""
    },
    {
      "date": "06-29-2021",
      "title": "Accounts for a dormant company",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzMwNTg2NjU2OWFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AA",
      "filing_type": "Annual Accounts"
    },
    {
      "date": "09-17-2020",
      "title": "Confirmation statement",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzI3Nzk2NDYyM2FkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "CS01",
      "filing_type": ""
    },
    {
      "date": "07-16-2020",
      "title": "Accounts for a dormant company",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzI3MzE1MDA4OWFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AA",
      "filing_type": "Annual Accounts"
    },
    {
      "date": "09-25-2019",
      "title": "Confirmation statement",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzI0NTA0MjIzNmFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "CS01",
      "filing_type": ""
    },
    {
      "date": "06-13-2019",
      "title": "Accounts for a dormant company",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzIzNjcxNzk4OGFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AA",
      "filing_type": "Annual Accounts"
    },
    {
      "date": "09-19-2018",
      "title": "Confirmation statement",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzIxNDgyODU3NmFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "CS01",
      "filing_type": ""
    },
    {
      "date": "05-22-2018",
      "title": "Accounts for a dormant company",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzIwNTUwMDY3MmFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AA",
      "filing_type": "Annual Accounts"
    },
    {
      "date": "09-18-2017",
      "title": "Confirmation statement",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzE4NTUzNjY0M2FkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "CS01",
      "filing_type": ""
    },
    {
      "date": "05-31-2017",
      "title": "Accounts for a dormant company",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzE3Njg5MTI4N2FkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AA",
      "filing_type": "Annual Accounts"
    },
    {
      "date": "09-22-2016",
      "title": "Confirmation statement",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzE1Nzg2ODM4OGFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "CS01",
      "filing_type": ""
    },
    {
      "date": "06-06-2016",
      "title": "Accounts for a dormant company",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzE1MDA5NzE5NGFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AA",
      "filing_type": "Annual Accounts"
    },
    {
      "date": "09-22-2015",
      "title": "Annual return",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzEzMTM2MzM3N2FkaXF6a2N4/document?format=pdf&download=0",
      "description": "GBP 1",
      "filing_code": "AR01",
      "filing_type": "Annual Return"
    },
    {
      "date": "06-03-2015",
      "title": "Accounts for a dormant company",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzEyNDM4ODQwOGFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AA",
      "filing_type": "Annual Accounts"
    },
    {
      "date": "09-16-2014",
      "title": "Annual return",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzEwNzUyMzExM2FkaXF6a2N4/document?format=pdf&download=0",
      "description": "GBP 1",
      "filing_code": "AR01",
      "filing_type": "Annual Return"
    },
    {
      "date": "05-07-2014",
      "title": "Accounts for a dormant company",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzA5OTU5MTYzMGFkaXF6a2N4/document?format=pdf&download=0",
      "description": "",
      "filing_code": "AA",
      "filing_type": "Annual Accounts"
    },
    {
      "date": "09-23-2013",
      "title": "Annual return",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzA4NTU2OTQxMGFkaXF6a2N4/document?format=pdf&download=0",
      "description": "GBP 1",
      "filing_code": "AR01",
      "filing_type": "Annual Return"
    },
    {
      "date": "09-11-2012",
      "title": "Incorporation",
      "file_url": "https://find-and-update.company-information.service.gov.uk//company/08209948/filing-history/MzA2Mzg3NDMzM2FkaXF6a2N4/document?format=pdf&download=0",
      "description": "MODEL ARTICLES ‐Model articles adopted",
      "filing_code": "NEWINC",
      "filing_type": "New incorporation documents"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "9 Princes Square, Harrogate, England, HG1 1ND"
    }
  ],
  "dissolution_date": "",
  "additional_detail": [
    {
      "data": [
        {
          "next_due_date": "",
          "next_account_due_date": "06-30-2024",
          "last_account_made_date": "09-30-2022",
          "next_account_made_date": "09-30-2023",
          "first_account_made_date": ""
        }
      ],
      "type": "account_details"
    },
    {
      "data": [
        {
          "next_due_date": "",
          "first_account_made_date": "",
          "next_confirmation_statement_due_date": "09-25-2023",
          "last_confirmation_statement_made_date": "09-11-2022",
          "next_confirmation_statement_made_date": "09-11-2023"
        }
      ],
      "type": "statement_details"
    },
    {
      "data": [
        "99999 - Dormant Company"
      ],
      "type": "SIC_codes"
    },
    {
      "data": [
        {
          "name": "Mr Marc Anthony Feldman",
          "legal_form": "",
          "governing_law": "",
          "notified_date": "12-13-2021",
          "nature_of_control": "",
          "country_of_residence": "Ownership of shares – 75% or more",
          "correspondence_address": "9 Princes Square, Harrogate, England, HG1 1ND",
          "principal_office_address": ""
        }
      ],
      "type": "beneficial_owners"
    }
  ],
  "incorporation_date": "09-11-2012",
  "registration_number": "08209948",
  "announcements_detail": [
    
  ],
  "previous_names_detail": [
    
  ]
}
```

## Crawler Type
This is a web scraper crawler that uses the `Requests` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Requests`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be more than a week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/united_kingdom/united_kingdom_kyb.py`