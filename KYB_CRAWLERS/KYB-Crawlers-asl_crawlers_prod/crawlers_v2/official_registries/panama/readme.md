# Panama Official Registry Crawler

## Introduction
    This is the website of the Public Registry of Panama (Registro Público de Panamá in Spanish). 
    The public registry is a government institution that manages and regulates public records related 
    to different legal matters in Panama, such as property ownership, mortgages, and business registration. 
    The website provides various services, including access to public registers, information about procedures, 
    forms, and regulations. It also offers online services for businesses, such as online registration and payment systems, 
    as well as tools for searching and obtaining information from the public records.

    URL : https://www.rp.gob.pa/

## Data Structure
    The extracted data is structured into a dictionary containing various key-value pairs. 
    The script defines functions such as `prepare_data` and `prapare_obj` to structure and 
    prepare data for insertion into a database.

## Crawler Type

    This is a web scraper crawler that utilizes Selenium for web page interaction and BeautifulSoup for HTML parsing.

## Sample object {
    "name": "",
    "status": "Recibido en el área y Pendiente de Asignación de Registrador",
    "industries": "Desconocido",
    "meta_detail": {
      "deed_date": "07-10-2006",
      "deed_number": ""
    },
    "country_name": "Panama",
    "crawler_name": "custom_crawlers.kyb.panama.panama_kyb",
    "people_detail": [
      {
        "name": "LUIS ARAUZ",
        "designation": "registered_agent"
      }
    ],
    "dissolution_date": "",
    "additional_detail": [
      {
        "data": [
          {
            "name": "Registro RESERVAServicio Derechos de Calificación"
          }
        ],
        "type": "procedures_and_services"
      },
      {
        "data": [
          {
            "name": "Número de Liquidación con identificador 7006130749 por importe de B/.30.00 y fecha de pago 07/10/2006"
          }
        ],
        "type": "payment_documents_detail"
      },
      {
        "data": [
          {
            "action": "Recibido en el área y Pendiente de Asignación de Registrador",
            "date_and_time": "10-22-2014"
          }
        ],
        "type": "processing_history"
      },
      {
        "data": [
          {
            "document": "DOCUMENTO ESCANEADO EN LA ENTRADA - 103147/2006 (0)",
            "file_url": "https://www.rp.gob.pa/Cotejo/ObtenerDocumentoPorIdentificadorConMarcaAgua/af20aac4-6b7f-45d3-929e-f00cb6f980db/False"
          },
          {
            "document": "DOCUMENTO ESCANEADO EN LA ENTRADA - 103147 - 1/2006 (0)",
            "file_url": "https://www.rp.gob.pa/Cotejo/ObtenerDocumentoPorIdentificadorConMarcaAgua/4c57c096-3076-4f06-9177-e6b10c013045/False"
          }
        ],
        "type": "documents"
      }
    ],
    "registration_date": "07-10-2006",
    "registration_number": "103147" }

## Additional Dependencies
    - `time`
    - `sys`
    - `selenium`
    - `beautifulsoup4`
    - `pyvirtualdisplay`

## Estimated Processing Time

    The processing time for the crawler may vary depending on the number of pages to be scraped and the website's responsiveness. The script includes sleep times to handle asynchronous loading of elements.

## How to Run the Crawler

    1. Install the required dependencies: `pip install -r requirements.txt`
    2. Set up a virtual environment if necessary.
    3. Ensure that the appropriate WebDriver (e.g., ChromeDriver) is downloaded and its path is correctly configured in the script.
    4. Run the script: `python3 your_script.py [all_arguments]`
    
    - `arg1`: Business number 
    - `arg2`: Search term
   
    Example: `python3 your_script.py 1234 sample_search_term`
