# Crawler: Sri Lanka

## Crawler Introduction
 This Python script serves as a web scraper tailored to extract information from two distinct sources: Source 1,[listcompany, Business Directory](https://www.listcompany.org/Sri_Lanka_Country.html) and Source 2,[Powrbot Inc.](https://powrbot.com/companies/list-of-companies-in-sri-lanka/). Both scripts fetch data from their respective API endpoints, process the retrieved HTML content, and subsequently populate a PostgreSQL table named "reports" with pertinent information.

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
#### Source 1
```json
"data": {
  "name": "SUNRISE LANKA PRODUCTS (PVT) LTD",
  "type": "Manufacturer, Trading Company, Distributor/Wholesa",
  "meta_detail": {
    "country": "Sri Lanka",
    "total_employees": "51 - 100 People",
    "year_established": "2012",
    "business_location": "COLOMBO 09, Sri Lanka",
    "company_description": "Company Description"
  },
  "country_name": "Sri Lanka",
  "crawler_name": "custom_crawlers.kyb.sri_lanka.sri_lanka_unofficial_source1.py",
  "people_detail": [
    {
      "name": "Mr. Haseem Mohamed",
      "fax_number": "94-—27-2223073",
      "meta_detail": {
        "department": "",
        "mobile_number": "94777731772"
      },
      "phone_number": "94-—27-2225001",
      "postal_address": "51000"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "151,school Road,Gallela"
    },
    {
      "type": "operational_address",
      "address": "168/A,VeluwenaRoad,Colombo-09, Colombo, Sri Lanka"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "url": "https://www.listcompany.org/Rice_Product.html",
          "products": "Rice"
        },
        {
          "url": "https://www.listcompany.org/Rice_Bran_Product.html",
          "products": "Rice Bran"
        },
        {
          "url": "https://www.listcompany.org/Cattle_Feeds_Product.html",
          "products": "Cattle Feeds"
        },
        {
          "url": "https://www.listcompany.org/Rice_Product.html",
          "products": "Rice"
        }
      ],
      "type": "products_information"
    }
  ],
  "registration_number": ""
}
```

#### Source 2
```json
"data": {
  "name": "Millennium Airlines",
  "meta_detail": {
    "IATA": "IATAICAOCallsignDLKDECCAN LANKA",
    "hubs": "Bandaranaike International Airport, Ratmalana Airport",
    "destinations": "9",
    "headquarters": "Colombo, Sri Lanka",
    "year_founded": "2004",
    "fleet_size": "4",
    "company_description": "Simplifly is Sri Lanka´s leading internal airline and the only airline in Sri Lanka that operates helicopters, planes and sea planes. Charter a Helicopter or Plane and enjoy a breathtaking aerial experience."
  },
  "country_name": "Sri Lanka",
  "crawler_name": "custom_crawlers.kyb.sri_lanka.sri_lanka_unofficial_source2.py",
  "people_detail": [
    {
      "name": "Suren Mirchandani",
      "designation": "Founder"
    }
  ],
  "contacts_detail": [
    {
      "type": "website",
      "value": "www.simplifly.com"
    }
  ]
}
```

## Crawler Type
Both of these are web scraper crawlers that utilize the `Requests` library for scraping and employ `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Requests`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The processing time for both crawlers is estimated to be approximately one day.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the source 1 script: `python3 custom_crawlers/kyb/sri_lanka/sri_lanka_unofficial_source1.py`
6. Run the source 2 script: `python3 custom_crawlers/kyb/sri_lanka/sri_lanka_unofficial_source2.py`