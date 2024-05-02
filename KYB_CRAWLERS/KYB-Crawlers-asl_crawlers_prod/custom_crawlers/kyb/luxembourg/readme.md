# Crawler: Luxembourg

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [LUXEMBOURG BUSINESS REGISTERS](https://www.lbr.lu/). The script use selenium to crawl to data page, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "Owel & Co's International Registered Trust Company Bankverwaltungsgesellschaft  m.b.H., Luxemburg",
  "type": "Société à responsabilité limitée",
  "status": "radiée",
  "meta_detail": {
    "file_deletion_date": "31-03-2020"
  },
  "country_name": "Luxembourg",
  "crawler_name": "custom_crawlers.kyb.luxembourg.luxembourg.py",
  "fillings_detail": [
    {
      "date": "31-03-2020",
      "file_url": "https://gd.lu/rcsl/6fr8L0",
      "filing_code": "L200057446",
      "filing_type": "Deletion"
    }
  ],
  "addresses_detail": [
    {
      "type": "registered_address",
      "address": "1, Glesenerstrasse"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "nace_code": "64.201",
          "description": "Holding 1929 (law of 31st July1929)"
        }
      ],
      "type": "nace_code_info"
    },
    {
      "data": [
        {
          "date": "25-10-1950",
          "file_url": "https://gd.lu/ercs_archive/6hnSkM",
          "filing_type": "Publication",
          "meta_detail": {
            "total_documents": "2 documents"
          }
        },
        {
          "date": "25-10-1950",
          "file_url": "https://gd.lu/ercs_archive/DFlrv",
          "filing_type": "Requisition",
          "meta_detail": {
            "total_documents": "1 document"
          }
        }
      ],
      "type": "archived_files_info"
    },
    {
      "data": [
        {
          "name": "Owel  Co's International Registered Trust Company Bankverwaltungsgesellschaft  m.b.H., Luxemburg"
        },
        {
          "name": "Owel  Co's International Registered Trust Company, société à responsabilité limitée de gestion des banques, Luxembourg"
        },
        {
          "name": "Owel  Co's International Registered Trust Company, Bank Management Limited, Luxembourg"
        },
        {
          "name": "Owel  Co's International Registered Trust Company, Bank-Beheers Naamloze Vennootschap, Luxemburg"
        }
      ],
      "type": "other_names"
    }
  ],
  "registration_date": "09-11-1970",
  "registration_number": "B9180"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library crawl to data page, get HTML data and then use `beautifulsoup` to parse and extract required information.

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
5. Run the script: `python3 custom_crawlers/kyb/luxembourg/luxembourg.py`