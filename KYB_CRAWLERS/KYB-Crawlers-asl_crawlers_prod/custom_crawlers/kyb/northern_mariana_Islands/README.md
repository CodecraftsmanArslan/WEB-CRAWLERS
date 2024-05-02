# Crawler: Northern Mariana Islands

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Commonwealth of the Northern Mariana Islands (CNMI) - Saipan Chamber of Commerce](https://business.saipanchamber.com/list/search?sa=true). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "Pacific Marine Enterprises, Inc.",
  "meta_detail": {
    "category": "RetailMarine Products & Services",
    "pin_location": "https://www.google.com/maps/embed/v1/place?key=AIzaSyAACLyaFddZFsbbsMCsSY4lq7g6N4ycArE&q=Pai%20Pai%20Drive%20Corner,%20Saipan,%20MP,%2096950",
    "working_hours": "Mon - Fri \r8:00AM to 5:00PM"
  },
  "country_name": "Northern Mariana Islands",
  "crawler_name": "custom_crawlers.kyb.northern_mariana_Islands.northern_mariana_Islands.py",
  "people_detail": [
    {
      "name": "Ms. Danilyn David Varela",
      "designation": "General Manager",
      "meta_detail": {
        "mobile_number": "(670) 233-0744"
      },
      "phone_number": "(670) 989-8601",
      "postal_address": "P.O. BOX 10001 PMB 181 Saipan MP 96950"
    }
  ],
  "contacts_detail": [
    {
      "type": "phone_number",
      "value": "(670) 233-0744"
    },
    {
      "type": "fax_number",
      "value": "(670) 322-0744"
    },
    {
      "type": "website",
      "value": "https://www.facebook.com/pmecnmi/"
    },
    {
      "type": "social_media_1",
      "value": "https://www.facebook.com/pmecnmi/"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Pai Pai Drive Corner Tanapag Saipan MP 96950"
    }
  ],
  "registration_number": ""
}
```

## Crawler Type
This is a web scraper crawler that uses the `Requests` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Requests`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler is anticipated to complete its processing within approximately one hour.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/northern_mariana_Islands/northern_mariana_Islands.py`