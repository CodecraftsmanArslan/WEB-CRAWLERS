# Crawler: Angola

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [GUICHÉ ÚNICO DA EMPRESA](https://gue.gov.ao/portal/publicacao?empresa=____). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "MAKEL KUZOLA - COMÉRCIO GERAL, LDA",
  "tax_number": "5000609714",
  "meta_detail": {
    "services": "Comércio por grosso de outros produtos alimentares;",
    "reg_details": "O/A Conservador(a), ISABEL ANGELINA RICARDO, assinado em 20-10-2020 08:43:35.",
    "obligtion_criteria": "intervenção de um gerente"
  },
  "country_name": "Angola",
  "crawler_name": "Angola Official Registry",
  "addresses_detail": [
    {
      "type": "headquarters_address",
      "address": "Província de Luanda, município de Talatona, distrito urbano de Talatona, CASA Nº 112."
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "description": "1º KELVIN PANZO DE MATOS MONTEIRO DA COSTA, solteiro, maior, de nacionalidade Angolana, natural de Luanda, província de Luanda, onde reside habitualmente no Bairro BENFICA, casa S/Nº, com uma quota no valor nominal de de KZ 50.000,00;2º MARIA MANUELA PONZO NARCISO, solteiro, maior, de nacionalidade Angolana, natural de Luanda, província de Luanda, onde reside habitualmente no Bairro Prenda, APTº 13, com uma quota no valor nominal de de KZ 50.000,00;"
        }
      ],
      "type": "UBOs_info"
    },
    {
      "data": [
        {
          "capital": "Kz.100.000,00"
        }
      ],
      "type": "capital_info"
    }
  ],
  "registration_number": "3171-20/201020"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to crawl and `beautifulsoup` for scraping.

## Additional Dependencies
- `bs4` (BeautifulSoup)
- `selenium`

## Estimated Processing Time
The processing time for the crawler is estimated 5 days.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/angola/angola.py`