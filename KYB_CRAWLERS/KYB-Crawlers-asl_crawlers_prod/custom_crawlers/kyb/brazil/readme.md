# Crawler: Brazil

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Federal Revenue of Brazil (RFB)](https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-jurdica---cnpj). The script fetches data from the zip URL to extract into CSV file inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "YASMIN SINDY NOGUEIRA FELIX",
  "tax_number": "000000",
  "meta_detail": {
    "member_code": "2",
    "cpf_or_cnpj_of_the_member_number": "190521",
    "foreign_member_of_the_country_code": ""
  },
  "country_name": "Brazil",
  "crawler_name": "crawlers.custom_crawlers.kyb.brazil.brazil_kyb2",
  "additional_detail": [
    {
      "data": [
        {
          "name": "Administrator",
          "qualification_code": "5"
        }
      ],
      "type": "qualification_information"
    },
    {
      "data": [
        {
          "legal_authority": "",
          "legal_authority_qualification_code": "0"
        }
      ],
      "type": "legal_authority_information"
    }
  ],
  "registration_date": "1970-01-01 10:37:00.429000",
  "registration_number": "46209503",
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping.

## Additional Dependencies
- `Request`
- `pandas`

## Estimated Processing Time
The processing time for the crawler is estimated 2 months.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/brazil/brazil_kyb1.py`