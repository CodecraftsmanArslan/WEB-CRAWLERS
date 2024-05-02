import os
from datetime import datetime
from multiprocessing import Pool, Process, freeze_support
from CustomCrawler import CustomCrawler
import traceback
import sys
from pathlib import Path
import time
import threading
sys.path.append(str(Path(__file__).parent.parent))
from load_env.load_env import ENV

# Your existing code for meta_data, crawler_config, and other setup here
meta_data = {
    'SOURCE': 'gov.me',
    'COUNTRY': 'Mexico',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://siem.economia.gob.mx/ui/pubconsultaestablecimientos",
                      "Source Description": "gob.mx is the platform that promotes innovation in the government, boosts efficiency, and transforms processes to provide information, procedures, and a platform for participation to the population."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://siem.economia.gob.mx/ui/pubconsultaestablecimientos'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Mexico Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'


mexico_crawler = CustomCrawler(
    meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = mexico_crawler.get_requests_helper()



FILE_PATH = os.path.dirname(os.getcwd()) + "/mexico"


BASE_URL = "https://siem.economia.gob.mx/"

# Function to make a request and get data from a given URL

def get_data_from_url(path, headers=None):
    url = BASE_URL + path
    response = request_helper.make_request(url, headers=headers)
    STATUS_CODE= response.status_code
    return STATUS_CODE,response.json()

# Function to get details of an establishment using its ID


def get_establishment_details(establishment_id):
    path = f"detalle-establecimiento?id={establishment_id}"
    STATUS_CODE,response = get_data_from_url(path)
    if STATUS_CODE == 200:
        nombre_data = response.get("nombreComercial", " ")
        return nombre_data
   

# Function to get location details of an establishment using its ID


def get_location_details(establishment_id):
    path = f"establecimiento-ubicacion.json?id={establishment_id}"
    STATUS_CODE,response = get_data_from_url(path)
    if STATUS_CODE == 200:
        calle = response.get("calle", " ")
        exterior = response.get("exterior", " ")
        edificio = response.get("edificio", " ")
        if "N/A" in edificio:
            edificio = " "
        cp = response.get("cp", " ")
        colonia = response.get("colonia", " ")
        loc = response.get("localidad", " ")
        calle1 = response.get("calle1", " ")
        calle2 = response.get("calle2", " ")
        posterior = response.get("callePosterior", " ")
        tele = response.get("telefono", " ")
        mail = response.get("mail", " ")
        otro = response.get("otro", " ")
        web = response.get("web", " ")

        return calle, exterior, edificio, cp, colonia, loc, calle1, calle2, posterior, tele, mail, otro, web

# Function to get product details of an establishment using its ID


def get_product_details(establishment_id):
    path = f"establecimientoproducto-por-establecimiento?idEstablecimiento={establishment_id}"
    STATUS_CODE,response = get_data_from_url(path)
    if STATUS_CODE == 200:
        products_tipo_1 = [product["producto"] if product["producto"]
                        is not None else "" for product in response if product["tipo"] == 1]
        products_tipo_2 = [product["producto"] if product["producto"]
                        is not None else "" for product in response if product["tipo"] == 2]

        # Construct the names using the products of "tipo" 1 and "tipo" 2
        # Combine the first three products of "tipo" 1
        name_1 = " ".join(products_tipo_1)
        # Combine the first two products of "tipo" 2
        name_2 = " ".join(products_tipo_2)

        return name_1, name_2

# Function to get the main activity of an establishment using its ID


def get_main_activity(establishment_id):
    path = f"detalle-establecimiento?id={establishment_id}"
    STATUS_CODE,response = get_data_from_url(path)
    if STATUS_CODE == 200:
        main_activity = response.get("actividadPrincipal", " ")
        card = response.get("catActividad", " ")
        return main_activity, card

# Function to get detailed activity information of an establishment using its ID


def get_activity_details(establishment_id):
    path = f"detalle-establecimiento-perfil?id={establishment_id}"
    STATUS_CODE,response = get_data_from_url(path)
    if STATUS_CODE == 200:
        activities = []
        for i in range(1, 4):
            activity = response[f"actividad{i}"] if response[f"actividad{i}"] is not None else ""
            activities.append(activity)
        exporta = "SI" if "0" not in str(response["exporta"]) else "NO"
        importa = "SI" if "0" not in str(response["importa"]) else "NO"
        return activities, exporta, importa

# Function to get export and import details of an establishment using its ID


def get_export_import_details(establishment_id):
    path = f"establecimiento-pais-por-establecimiento?id={establishment_id}"
    STATUS_CODE,response = get_data_from_url(path)
    if STATUS_CODE == 200:
        try:
            country = response[0]["pais"]
        except IndexError:
            country = ""
        return country


def complemento_details(establishment_id):
    path = f"establecimiento-complemento?id={establishment_id}"
    STATUS_CODE,response = get_data_from_url(path)
    if STATUS_CODE == 200:
        des_loc = response.get("descripcionCalle"," ")
        return des_loc
# Function to get the company type from an external source


def get_company_type():
    path = f"consultar-registros-criterios-catalogo.json?activo=true&todos=true&tabla=CAT_TIPO_EMPRESA"
    try:
        STATUS_CODE,response = get_data_from_url(path)
        if STATUS_CODE == 200:
            company_type = response[2]["descripcion"]
    except Exception as e:
        company_type = ""
    return company_type

# Function to get the installation type from an external source


def get_installation_type():
    path = f"consultar-registros-criterios-catalogo.json?activo=true&todos=true&tabla=CAT_TIPO_INSTALACION"
    try:
        STATUS_CODE,response = get_data_from_url(path)
        if STATUS_CODE == 200:
            installation_type = response[0]["descripcion"]
    except Exception as e:
        installation_type = ""
    return installation_type


# Function to crawl pages in parallel using multiprocessing
def crawl_page(page_number):
    print(f"page_number {page_number}")
    path = f"establecimientos-publicos-x-criterios?id=&catEntidadFederativaFk=0&catActividad=0&catCamaraFk=&nombreComercial=&importa=2&exporta=2&publico=2&catEdoEstablecimientoFk=0&pageNum={page_number}&orderBy=&desc=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }

    while True:
        STATUS_CODE,response = get_data_from_url(path, headers)
        if not response:
            continue
        if STATUS_CODE == 200:
            establishment_ids = [item["id"] for item in response["list"]]
            break
        else:
            time.sleep(8)
    
    # Iterate over IDs and get data
    for establishment_id in establishment_ids:
        nombre_data = get_establishment_details(establishment_id)
        calle, exterior, edificio, cp, colonia, loc, calle1, calle2, posterior, tele, mail, otro, web = get_location_details(
            establishment_id)
        name_1, name_2 = get_product_details(establishment_id)
        main_activity, card = get_main_activity(establishment_id)
        des_loc=complemento_details(establishment_id)
        activities, exporta, importa = get_activity_details(
            establishment_id)
        country = get_export_import_details(establishment_id)
        company_type = get_company_type()
        installation_type = get_installation_type()

        address_details =[
                {
                    "type": "general_address",
                    "address": f"{calle} {exterior} {edificio} {cp}"
                },
                {
                    "type": "human_settlement",
                    "address": colonia,
                },
                {
                    "type": "intervialities",
                    "address": f"{calle1} {calle2}"
                },
                {
                    "type": "rear_road",
                    "address": posterior,
                },
                {
                    "type": "regional_location",
                    "address": f"{des_loc} {loc}",
                }
            ]
        # Prepare data object using external utility function (not defined in the provided snippet)
        OBJ = {
            "name": nombre_data,
            "addresses_detail": address_details,
            "contacts_detail": [
                {
                    "type": "phone_number",
                    "value": tele,
                },
                {
                    "type": "email",
                    "value": mail
                },
                {
                    "type": "website",
                    "value": web
                },
                {
                    "type": "other",
                    "value":otro


                }
            ],
            "type": company_type,
            "facilities_type": installation_type,
            "additional_detail": [
                {
                    "type": "export_and Import_information",
                    "data": [
                        {
                            "do_they_export?": exporta,
                            "countries": "",
                        },
                        {
                            "do_they_import?": importa,
                            "countries": country
                        }
                    ]
                },
                {
                    "type": "Activity_information",
                    "data": [
                        {
                            "main_activity": main_activity,
                            "main_services(1)": activities[0] if len(activities) > 0 else "",
                            "main_services(2)": activities[1] if len(activities) > 1 else "",
                            "main_services(3)": activities[2] if len(activities) > 2 else "",
                            "activity_code": str(card)
                        }
                    ]
                },
                {
                    "type": "product_information",
                    "data": [
                        {
                            "name": name_1,
                            "destination": "Nacional"
                        }
                    ]
                },
                {
                    "type": "services_used",
                    "data": [
                        {
                            "name": name_2,
                            "origin": "Nacional",
                        }
                    ]
                }
            ]
        }
        OBJ = mexico_crawler.prepare_data_object(OBJ)
        ENTITY_ID = mexico_crawler.generate_entity_id(company_name=OBJ['name'],reg_number=OBJ['addresses_detail'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = ""
        ROW = mexico_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
        mexico_crawler.insert_record(ROW)
        with open(f"{FILE_PATH}/crawled_records.txt", "a") as crawled_records:
                crawled_records.write(f"{establishment_id}- page_number {page_number} ""\n")
                print(f"Id_Number: {establishment_id}-{page_number}")


# Apply multithreading 
def crawl_pages_multithread(start, end):
    threads = []
    num_threads = 2  # Adjust the number of threads based on your needs
    step = (end - start) // num_threads

    for page in range(num_threads):
        thread_start = start + page * step
        thread_end = thread_start + step
        thread = threading.Thread(target=crawl_page_range, args=(thread_start, thread_end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    

def crawl_page_range(start, end):
    current_page_number = start
    while current_page_number < end:
        try:
            crawl_page(current_page_number)
        except:
            pass
        current_page_number += 1

    mexico_crawler.end_crawler()
    log_data = {"status": "success", "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"],
                "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",
                "crawler": "HTML", "ends_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    mexico_crawler.db_log(log_data)


if __name__ == '__main__':
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <start_page> <end_page>")
        sys.exit(1)

    start_page = int(sys.argv[1]) 
    end_page = int(sys.argv[2]) 
    print(f"start_page {start_page} end_page {end_page}")
    crawl_pages_multithread(start_page, end_page)
