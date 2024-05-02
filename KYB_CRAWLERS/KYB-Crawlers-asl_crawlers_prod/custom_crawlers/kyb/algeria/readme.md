# Crawler: Algeria

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [El Mouchir Directory of Algerian Companies](https://elmouchir.caci.dz/toutesentreprises?entreprise_search=bank#titre_page). The script fetches data from the specified API endpoint by adding page number (1 - 797), processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "CASBAH",
  "type": "SARL",
  "industries": "Produits de l'industrie des vinaigres et...",
  "meta_detail": {
    "about": "Casbah a démarré son activité dans un modeste local de 35m² situé dans la vallée de la rampe avec 3 salariés, aujourd'hui le producteur de vinaigre Casbah compte 150 salariés avec une usine à Ouled Chbel d'une superficie de 6400m² Casbah a toujours voulu partager le quotidien du peuple algérien ainsi que de nos chers consommateurs récompensés pour leur fidélité.",
    "nature": "ProducteurDistributeur",
    "services": "Produits agroalimentaires",
    "brand_name": "Casbah",
    "start_year": "1999",
    "working_hours": "Nous n’avons pas cette information.",
    "ownership_status": "Privé",
    "industries_url": "https://elmouchir.caci.dz/activite/5827"
  },
  "country_name": "Algeria",
  "crawler_name": "custom_crawlers.kyb.algeria.algeria.py",
  "contacts_detail": [
    {
      "type": "email",
      "value": "info@casbahdz.com   tahar.saada@casbahdz.com"
    },
    {
      "type": "phone_number",
      "value": "023 41 90 06      023 41 90 16"
    },
    {
      "type": "mobile_number",
      "value": "0555 04 16 16     0554 51 21 55"
    },
    {
      "type": "fax_number",
      "value": "023 41 90 48"
    },
    {
      "type": "social_media",
      "value": "info@casbahdz.com   tahar.saada@casbahdz.com"
    },
    {
      "type": "website",
      "value": "http://www.casbahdz.com"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Cité El Behairia, n°59.Ouled Chebel.Bp 63"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "url": "https://elmouchir.caci.dz/wilaya/16",
          "organization": "Alger"
        },
        {
          "last_updated": "il y a 6 mois",
          "member_since": "il y a 12 ans"
        }
      ],
      "type": "agency_details"
    }
  ]
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4`

## Estimated Processing Time
The processing time for the crawler is estimated 1 day.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/algeria/algeria.py`