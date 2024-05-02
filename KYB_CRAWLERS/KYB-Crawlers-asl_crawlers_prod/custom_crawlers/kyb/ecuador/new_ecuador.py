"""Set System Path"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import requests, os, glob, shutil, base64
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
import nopecha as nopecha
from pyvirtualdisplay import Display
import undetected_chromedriver as uc 
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
nopecha.api_key = os.getenv('NOPECHA_API_KEY2')
FILE_PATH = os.path.dirname(os.getcwd()) + 'ecuador/'
meta_data = {
    'SOURCE' :'Superintendencia de Compañías, Valores y Seguros (Superintendency of Companies, Securities and Insurance)',
    'COUNTRY' : 'Ecuador',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://mercadodevalores.supercias.gob.ec/reportes/directorioCompanias.jsf", 
                        "Source Description": "Official directory of companies registered in Ecuador. The directory is maintained by the Superintendencia de Compañías, Valores y Seguros (Superintendency of Companies, Securities and Insurance), which is a government agency responsible for overseeing and regulating the financial sector in Ecuador. The directory includes a list of registered companies and businesses operating in Ecuador, as well as their contact information and financial statements."},
    'URL' : 'https://mercadodevalores.supercias.gob.ec/reportes/directorioCompanias.jsf',
    'SOURCE_TYPE' : 'HTML'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Ecuador Official Registry'
}
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
display = Display(visible=0,size=(800,600))
display.start()
ecuador_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = ecuador_crawler.get_requests_helper()
selenium_helper = ecuador_crawler.get_selenium_helper()
# proxy_response = request_helper.make_request('https://proxy.webshare.io/api/v2/proxy/list/download/qtwdnlorrbofjrfyjjolbsiyvvkvcvocabovaehs/-/any/sourceip/direct/malta/')
options = uc.ChromeOptions()
# options.add_argument(f'--proxy-server=http://{proxy_response.text}')
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
driver = uc.Chrome(version_main=119, options=options)

wait = WebDriverWait(driver, 30)

def get_pdf_url(browser, xpath):
    """
    Description: Get the URL of a PDF document from a specified XPath on a web page using the given browser.
    @param:
    - browser (WebDriver): The browser instance to use for interacting with the web page.
    - xpath (str): The XPath of the element containing the PDF link.
    @return:
    - str: The URL of the PDF document.
    @raises:
    - Exception: If any error occurs during the process.
    """
    try:
        document_url = ""
        td_elements = browser.find_element(By.XPATH, xpath)
        pdf_anchor = td_elements.find_element(By.TAG_NAME, 'a')
        browser.execute_script("arguments[0].click();", pdf_anchor)
        identify_captcha(browser)
        pdf_btn = browser.find_element(By.TAG_NAME, "object")
        document_url = download_pdf(pdf_btn.get_attribute("data"))
        close_btn = browser.find_elements(By.CLASS_NAME, "ui-icon-closethick")
        if len(close_btn) > 3:
            close_btn[3].click()
        time.sleep(1)
        return document_url
    except Exception as e:
        print(e)
        close_btn = browser.find_elements(By.CLASS_NAME, "ui-icon-closethick")
        if len(close_btn) > 3:
            try: close_btn[4].click() 
            except: pass
        return document_url
def download_pdf(filename):
    """
    Description: Download a PDF file from a given URL and save it locally.This function sends an HTTP GET request to the provided PDF URL, downloads the PDF content,
    and saves it locally. The local file path is returned upon successful download.
    If the HTTP request is unsuccessful (status code other than 200), an error message is printed.
    @param:
    - filename (str): The URL of the PDF file.
    @return:
    - str: The local file path where the PDF is saved.
    """
    # Send an HTTP GET request to the PDF URL
    response = requests.get(filename)
    filename = filename.split('/')[-1].replace('?pfdrid_c=true', '')
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Specify the local file path where you want to save the PDF
        local_file_path = f"{FILE_PATH}pdf/{filename}"
        # Open the local file in binary write mode and write the PDF content to it
        with open(local_file_path, "wb") as local_file:
            local_file.write(response.content)
        
        print(f"PDF file downloaded and saved as {local_file_path}")
        return local_file_path
    else:
        print(f"Failed to download PDF (HTTP status code: {response.status_code})")


def get_filename():
    """
    Description: Move PDF files from a temporary directory to a designated PDF directory.This function creates a PDF directory if it doesn't exist, looks for PDF files in a temporary
    directory, and moves each file to the PDF directory. The function returns the local file path
    of the last moved PDF file.
    @return:
    
    - str: The local file path of the moved PDF file.
    If any error occurs during the process, the function silently handles it without raising an exception.
    """
    try:
        # Create the PDF directory if it doesn't exist
        pdf_directory = os.path.join(FILE_PATH, 'pdf')
        os.makedirs(pdf_directory, exist_ok=True)
        # Define the source directory and pattern to find PDF files
        source_directory = os.path.join(FILE_PATH, 'temp')
        pattern = os.path.join(source_directory, '*.pdf')
        # Get a list of PDF files in the source directory
        pdf_files = glob.glob(pattern)
        # Move each PDF file to the PDF directory
        for pdf_file in pdf_files:
            # Build the destination file path by combining the PDF directory and the source file name
            destination_file_path = os.path.join(pdf_directory, os.path.basename(pdf_file))
            # Move the file to the PDF directory
            shutil.move(pdf_file, destination_file_path)
            print(f"Moved '{os.path.basename(pdf_file)}' to '{pdf_directory}'")
        return f"{pdf_directory}/{os.path.basename(pdf_file)}"
    except:
        pass
def skip_pages(page):
    """
    Description: Skip a specified number of pages in a paginated UI by clicking the 'Next' button. This function simulates the action of clicking the 'Next' button in a paginated UI to navigate
    forward by the specified number of pages. It uses an explicit wait for the 'Next' button to be clickable
    before performing the click. Additionally, a short delay of 2 seconds is added after clicking the button.
    @param:
    - page (int): The number of pages to skip.
    """
    while page > 1:
        next_page_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ui-paginator-next")))
        next_page_button.click()
        time.sleep(2)
        page -= 1

def next_page_button():
    """
    Description: Click the 'Next' button in a paginated UI. This function attempts to click the 'Next' button in a paginated UI using an explicit wait
    for the button to be clickable. After clicking, it adds a short delay of 2 seconds. If successful,
    it returns False; otherwise, it returns True.
    @return:
    - bool: True if the 'Next' button is not clickable or an error occurs, False otherwise.
    """
    try:
        next_page_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ui-paginator-next")))
        next_page_button.click()
        time.sleep(2)
        return False
    except:
        return True
    
def get_image_text(div_element):
    """
    Description: Extract text from an image within a specified div element. This function takes a WebElement representing a div element containing an image. It extracts
    the image, saves it as 'captcha/captcha.png', and uses a CAPTCHA solving library (nopecha) to
    recognize the text in the image. The recognized text is cleaned and returned.
    
    @param:
    - div_element (WebElement): The WebElement representing the div containing the image.
    @return:
    - str: The extracted text from the image.
    """
    max_retries = 5
    for retry in range(1, max_retries + 1):
        try:
            time.sleep(2)
            tag = div_element.find_element(By.TAG_NAME, 'img')
            tag.screenshot('captcha/captcha.png')
            with open('captcha/captcha.png', 'rb') as image_file:
                image_64_encode = base64.b64encode(image_file.read()).decode('utf-8')
                captcha_text = nopecha.Recognition.solve(
                    type='textcaptcha',
                    image_urls=[image_64_encode],
                )
                captcha_text_cleaned = str(captcha_text).replace("[","").replace("]","").replace("'","")
                return captcha_text_cleaned           
        except Exception as e:
            print(e)
            if retry < max_retries:
                print(f"Retrying... Attempt {retry} of {max_retries}")
            else:
                print(f"Maximum retries ({max_retries}) reached. Giving up.")

def identify_captcha(browser):
    """
    Description: Identify and resolve a CAPTCHA prompt in a web page. This function checks if a CAPTCHA prompt is displayed in a web page (identified by the element
    with ID 'dlgCaptcha'). If a CAPTCHA is detected, it attempts to resolve it using the `get_image_text`
    function to extract text from the CAPTCHA image.
    The function interacts with the CAPTCHA input field, enters the extracted text, and clicks the
    verification button. It retries the process for a maximum number of attempts (max_retries).
    If the CAPTCHA is resolved successfully, it returns True; otherwise, it returns False.

    @param:
    - browser (WebDriver): The browser instance where the CAPTCHA prompt is present.
    @return:
    - bool: True if the CAPTCHA is resolved successfully or not present, False otherwise.
    """
    time.sleep(2)
    max_retries = 5
    div_element = browser.find_element(By.ID, "dlgCaptcha")
    style_attribute = div_element.get_attribute("style")
    
    if "display: block;" in style_attribute:
        print("Captcha detected")
        while max_retries > 0:
            print("Trying to resolve captcha")
            image_text = get_image_text(div_element)
            input_elements = div_element.find_elements(By.TAG_NAME, 'input')
            captcha_input = input_elements[1]
            captcha_input.clear()
            captcha_input.send_keys(image_text)
            verify_button = div_element.find_element(By.ID, "frmCaptcha:btnPresentarContenido")
            verify_button.click()
            time.sleep(2)
            warning_element = div_element.find_elements(By.CLASS_NAME, "ui-messages-close")
            if not warning_element:
                print("captcha resloved successfully")
                return True
            
            max_retries -= 1
    else:
        return True

def get_notificaciones_generales(browser):
    """
    Description: Retrieve information from the 'Notificaciones generales' section on a web page. This function navigates to the 'Notificaciones generales' section, extracts information from the HTML,
    and organizes it into a list of dictionaries. Each dictionary represents details about a notice,
    including procedure number, trade number, notice date, notifying person, designation, company name,
    description, and file URL.
    
    @param:
    - browser (WebDriver): The browser instance where the 'Notificaciones generales' section is present.
    @return:
    - list: A list of dictionaries containing additional details from the 'Notificaciones generales' section.
    """
    additional_detail = []
    target_anchor = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Notificaciones generales")))
    if target_anchor:
        browser.execute_script("arguments[0].click();", target_anchor)
        identify_captcha(browser)
        wait.until(EC.presence_of_element_located((By.ID, "frmInformacionCompanias:tblNotificacionesGenerales_data")))
        while True:
            soup = BeautifulSoup(browser.page_source, "html.parser")
            tbody = soup.find("tbody", {"id": "frmInformacionCompanias:tblNotificacionesGenerales_data"})
            trs = tbody.find_all("tr")
            if len(trs) > 1:
                for tr in trs:
                    tds = tr.find_all("td")
                    additional_detail.append({
                        "type": "notice_information",
                        "data": [{
                            "procedure_number": tds[0].text.strip().replace("\n", " ").replace("  ", " ") if tds[0].text is not None else "",
                            "trade_number": tds[1].text.strip().replace("\n", " ").replace("  ", " ") if tds[1].text is not None else "",
                            "notice_date": tds[2].text.strip().replace("\n", " ").replace("  ", " ") if tds[2].text is not None else "",
                            "notifying_person": tds[3].text.strip().replace("\n", " ").replace("  ", " ") if tds[3].text is not None else "",
                            "designation": tds[4].text.strip().replace("\n", " ").replace("  ", " ") if tds[4].text is not None else "",
                            "company name": tds[5].text.strip().replace("\n", " ").replace("  ", " ") if tds[5].text is not None else "",
                            "description": tds[6].text.strip().replace("\n", " ").replace("  ", " ") if tds[6].text is not None else "",
                            "file_url": tds[7].text.strip().replace("\n", " ").replace("  ", " ") if tds[7].text is not None else ""
                        }]
                    })
            if(next_page_button()):
                break
    return additional_detail

def get_administradores_anteriores(browser):
    """
    Description: Retrieve information about previous administrators from the 'Administradores anteriores' section. This function navigates to the 'Administradores anteriores' section, extracts information from the HTML,
    and organizes it into a list of dictionaries. Each dictionary represents details about a previous administrator,
    including name, nationality, designation, appointment date, and additional metadata such as identification number,
    period, commercial register number, commercial registration date, rl_or_adm, and file URL.

    @param:
    - browser (WebDriver): The browser instance where the 'Administradores anteriores' section is present.
    @return:
    - list: A list of dictionaries containing details about previous administrators.
    """
    people_detail = []
    target_anchor = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Administradores anteriores")))
    if target_anchor:
        browser.execute_script("arguments[0].click();", target_anchor)
        identify_captcha(browser)
        wait.until(EC.presence_of_element_located((By.ID, "frmInformacionCompanias:tblAdministradoresAnteriores_data")))
        while True:
            soup = BeautifulSoup(browser.page_source, "html.parser")
            tbody = soup.find("tbody", {"id": "frmInformacionCompanias:tblAdministradoresAnteriores_data"})
            trs = tbody.find_all("tr")
            if len(trs) > 1:
                for row_index, tr in enumerate(trs):
                    tds = tr.find_all("td")
                    xpath =f"/html/body/div[3]/div/form/span[1]/div/div/table[2]/tbody/tr[2]/td/div/div[1]/table/tbody/tr[{row_index+1}]/td[10]"
                    file_url = get_pdf_url(browser, xpath)
                    meta_detail = {
                        "identification_number": tds[0].text.strip().replace("\n", " ").replace("  ", " ") if tds[0].text is not None else "",
                        "period": tds[5].text.strip().replace("\n", " ").replace("  ", " ") if tds[5].text is not None else "",
                        "commercial_register_number": tds[6].text.strip().replace("\n", " ").replace("  ", " ") if tds[6].text is not None else "",
                        "commercial registration date": tds[7].text.strip().replace("\n", " ").replace("  ", " ") if tds[7].text is not None else "",
                        "rl_or_adm": tds[8].text.strip().replace("\n", " ").replace("  ", " ") if tds[8].text is not None else "",
                        "file_url": file_url if file_url is not None else "",
                    }
                    designation = tds[3].text.strip().replace('\n', ' ').replace('  ', ' ') if tds[3].text is not None else ""
                    people_detail.append({
                        "name": tds[1].text.strip().replace("\n", " ").replace("  ", " ") if tds[1].text is not None else "",
                        "nationality": tds[2].text.strip().replace("\n", " ").replace("  ", " ") if tds[2].text is not None else "",
                        "designation": f"previous {designation}" if designation is not None and designation != "" else "",
                        "appointment_date": tds[4].text.strip().replace("\n", " ").replace("  ", " ") if tds[4].text is not None else "",
                        "meta_detail": meta_detail
                    })
            if(next_page_button()):
                break
    return people_detail

def get_consulta_de_cumplimiento(browser):
    """
    Description: Retrieve compliance information from the 'Consulta de cumplimiento' section. This function navigates to the 'Consulta de cumplimiento' section, extracts compliance information from the HTML,
    and organizes it into a list of dictionaries. Each dictionary represents compliance details, including
    registration number, proceeding number, legal representative, social capital, legal status, and compliance status.

    @param:
    - browser (WebDriver): The browser instance where the 'Consulta de cumplimiento' section is present.
    @return:
    - list: A list of dictionaries containing compliance details.
    """
    additional_detail = []
    target_anchor = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Consulta de cumplimiento")))
    if target_anchor:
        browser.execute_script("arguments[0].click();", target_anchor)
        identify_cap = identify_captcha(browser)
        while True:
            time.sleep(2)
            if identify_cap:
                break
        soup = BeautifulSoup(browser.page_source, "html.parser")
        target_td = soup.find('td', string="Representante legal:")
        if target_td:
            tbody = target_td.find_parent('tbody')
            trs = tbody.find_all("tr")
            item = {}
            for tr in trs:
                tds = tr.find_all('td')
                if len(tds) == 2:
                    item[tds[0].text] = tds[1].text
            if len(item) > 0:
                additional_detail.append({
                    "type": "compliance_information",
                    "data": [{
                        "registration_number": item.get("R.U.C.:"),
                        "proceeding_number": item.get("Expediente:"),
                        "legal_representative": item.get("Representante legal:"),
                        "social_capital": item.get("Capital social:"),
                        "legal_status": item.get("Situación legal:"),
                        "compliance": item.get("Cumplimiento de obligaciones y existencia legal:")
                    }]
                })
    return additional_detail

def get_documentos_online(browser):
    """
    Description: Retrieve information about online documents from the 'Documentos online' section. This function navigates to the 'Documentos online' section, extracts information from the HTML,
    and organizes it into a list of dictionaries. Each dictionary represents details about an online document,
    including document name, date, and document URL.

    @param:
    - browser (WebDriver): The browser instance where the 'Documentos online' section is present.
    @return:
    - list: A list of dictionaries containing details about online documents.
    """
    additional_detail = []
    target_anchor = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Documentos online")))
    if target_anchor:
        browser.execute_script("arguments[0].click();", target_anchor)
        identify_captcha(browser)
        wait.until(EC.presence_of_element_located((By.ID, "frmInformacionCompanias:tabViewDocumentacion:tblDocumentosGenerales_data")))
        while True:
            soup = BeautifulSoup(browser.page_source, "html.parser")
            tbody = soup.find("tbody", {"id": "frmInformacionCompanias:tabViewDocumentacion:tblDocumentosGenerales_data"})
            trs = tbody.find_all("tr")
            if len(trs) > 1:
                for row_index, tr  in enumerate(trs):
                    tds = tr.find_all("td")
                    xpath = f"/html/body/div[3]/div/form/span[1]/div/div/div/div/div[1]/table/tbody/tr/td/div/div[1]/table/tbody/tr[{row_index+1}]/td[5]"
                    document_url = get_pdf_url(browser, xpath)
                    additional_detail.append({
                        "type": "company_documents",
                        "data": [{
                            "document_name": tds[0].text.strip().replace("\n", " ").replace("  ", " ") if tds[0].text is not None else "",
                            "date": tds[1].text.strip().replace("\n", " ").replace("  ", " ") if tds[1].text is not None else "",
                            "document_url": document_url if document_url is not None else ""
                        }]
                    })
            if(next_page_button()):
                break
    return additional_detail

def get_inf_sociedades_extranjeras(browser):
    """
    Description: Retrieve information about foreign company reports from the 'Inf. sociedades extranjeras' section. This function navigates to the 'Inf. sociedades extranjeras' section, extracts information from the HTML,
    and organizes it into a list of dictionaries. Each dictionary represents details about a foreign company report,
    including identification number, name, reason for presentation, year date, presentation date, and details URL.
    @param:
    - browser (WebDriver): The browser instance where the 'Inf. sociedades extranjeras' section is present.
    @return:
    - list: A list of dictionaries containing details about foreign company reports.
    """
    additional_detail = []
    target_anchor = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Inf. sociedades extranjeras")))
    if target_anchor:
        browser.execute_script("arguments[0].click();", target_anchor)
        identify_captcha(browser)
        wait.until(EC.presence_of_element_located((By.ID, "frmInformacionCompanias:tblInformesSociedadesExtranjeras_data")))
        while True:
            soup = BeautifulSoup(browser.page_source, "html.parser")
            tbody = soup.find("tbody", {"id": "frmInformacionCompanias:tblInformesSociedadesExtranjeras_data"})
            trs = tbody.find_all("tr")
            if len(trs) > 1:
                for tr in trs:
                    tds = tr.find_all("td")
                    additional_detail.append({
                        "type": "foreign_company_reports",
                        "data": [{
                            "identification_number": tds[0].text.strip().replace("\n", " ").replace("  ", " ") if tds[0].text is not None else "",
                            "name": tds[1].text.strip().replace("\n", " ").replace("  ", " ") if tds[1].text is not None else "",
                            "reason_for_presentation": tds[2].text.strip().replace("\n", " ").replace("  ", " ") if tds[2].text is not None else "", 
                            "year_date": tds[3].text.strip().replace("\n", " ").replace("  ", " ") if tds[3].text is not None else "",
                            "presentation_date": tds[4].text.strip().replace("\n", " ").replace("  ", " ") if tds[4].text is not None else "",
                            "details_url": tds[5].text.strip().replace("\n", " ").replace("  ", " ") if tds[5].text is not None else "",
                        }]
                    })
            if(next_page_button()):
                break
    return additional_detail

def get_informacion_anual_presentada(browser):
    """
    Description: Retrieve information about annually presented documents from the 'Información anual presentada' section. This function navigates to the 'Información anual presentada' section, extracts information from the HTML,
    and organizes it into a list of dictionaries. Each dictionary represents details about an annually presented document,
    including year, document code, document name, presentation date, and file URL.
    @param:
    - browser (WebDriver): The browser instance where the 'Información anual presentada' section is present.
    @return:
    - list: A list of dictionaries containing details about annually presented documents.

    """
    additional_detail = []
    target_anchor = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Información anual presentada")))
    if target_anchor:
        browser.execute_script("arguments[0].click();", target_anchor)
        identify_captcha(browser)
        wait.until(EC.presence_of_element_located((By.ID, "frmInformacionCompanias:tblInformacionAnual_data")))
        while True:
            soup = BeautifulSoup(browser.page_source, "html.parser")
            tbody = soup.find("tbody", {"id": "frmInformacionCompanias:tblInformacionAnual_data"})
            trs = tbody.find_all("tr")
            if len(trs) > 1:
                for row_index, tr in enumerate(trs):
                    tds = tr.find_all("td")
                    xpath = f"/html/body/div[3]/div/form/span[1]/div/div/table[2]/tbody/tr/td/div/div[1]/table/tbody/tr[{row_index+1}]/td[5]"
                    document_url = get_pdf_url(browser, xpath)
                    additional_detail.append({
                        "type": "company_documents",
                        "data": [{
                            "year": tds[0].text.strip().replace("\n", " ").replace("  ", " ") if tds[0].text is not None else "",
                            "document_code": tds[1].text.strip().replace("\n", " ").replace("  ", " ") if tds[1].text is not None else "",
                            "document_name": tds[2].text.strip().replace("\n", " ").replace("  ", " ") if tds[2].text is not None else "",
                            "presentation_date": tds[3].text.strip().replace("\n", " ").replace("  ", " ") if tds[3].text is not None else "",
                            "file_url": document_url if document_url is not None else "",
                        }]
                    })
            if(next_page_button()):
                break
    return additional_detail

def get_beneficiarios_finales(browser):
    """
    Description: Retrieve information about beneficial owners from the 'Beneficiarios finales' section. This function navigates to the 'Beneficiarios finales' section, extracts information from the HTML,
    and organizes it into a list of dictionaries. Each dictionary represents details about a beneficial owner,
    including identification number, name, nationality, investment type, capital, and restriction.
    @param:
    - browser (WebDriver): The browser instance where the 'Beneficiarios finales' section is present.
    @return:
    - list: A list of dictionaries containing details about beneficial owners.
    """
    additional_detail = []
    try:
        target_anchor = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Beneficiarios finales")))
        if target_anchor:
            browser.execute_script("arguments[0].click();", target_anchor)
            identify_captcha(browser)
            wait.until(EC.presence_of_element_located((By.ID, "frmInformacionCompanias:tblBeneficiarioFinales_data")))
            soup = BeautifulSoup(browser.page_source, "html.parser")
            tbody = soup.find("tbody", {"id": "frmInformacionCompanias:tblBeneficiarioFinales_data"})
            trs = tbody.find_all("tr")
            if len(trs) > 1:
                for tr in trs:
                    tds = tr.find_all("td")
                    additional_detail.append({
                        "type": "beneficial_owner",
                        "data": [{
                            "identification number": tds[0].text.strip().replace("\n", " ").replace("  ", " ") if tds[0].text is not None else "",
                            "name": tds[1].text.strip().replace("\n", " ").replace("  ", " ") if tds[1].text is not None else "",
                            "nationality": tds[2].text.strip().replace("\n", " ").replace("  ", " ") if tds[2].text is not None else "",
                            "investment type": tds[3].text.strip().replace("\n", " ").replace("  ", " ") if tds[3].text is not None else "",
                            "capital": tds[4].text.strip().replace("\n", " ").replace("  ", " ") if tds[4].text is not None else "",
                            "restriction": tds[5].text.strip().replace("\n", " ").replace("  ", " ") if tds[5].text is not None else "",
                        }]
                    })
    except Exception as e:
        pass
    return additional_detail

def get_accionistas(browser):
    """
    Description: Retrieve information about shareholders from the 'Accionistas' section. This function navigates to the 'Accionistas' section, extracts information from the HTML,
    and organizes it into a list of dictionaries. Each dictionary represents details about a shareholder,
    including name, nationality, designation, and additional metadata such as identification number,
    investment type, capital, and restriction.
    @param:
    - browser (WebDriver): The browser instance where the 'Accionistas' section is present.
    @return:
    - list: A list of dictionaries containing details about shareholders.
    """
    people_detail = []
    target_anchor = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Accionistas")))
    if target_anchor:
        browser.execute_script("arguments[0].click();", target_anchor)
        identify_captcha(browser)
        wait.until(EC.presence_of_element_located((By.ID, "frmInformacionCompanias:tblAccionistas_data")))
        while True:
            soup = BeautifulSoup(browser.page_source, "html.parser")
            tbody = soup.find("tbody", {"id": "frmInformacionCompanias:tblAccionistas_data"})
            trs = tbody.find_all("tr")
            if len(trs) > 1:
                for tr in trs:
                    tds = tr.find_all("td")
                    meta_detail = {
                        "restriction": tds[5].text.strip().replace("\n", " ").replace("  ", " ") if tds[5].text is not None else "",
                        "identification_number": tds[0].text.strip().replace("\n", " ").replace("  ", " ") if tds[0].text is not None else "",
                        "investment_type": tds[3].text.strip().replace("\n", " ").replace("  ", " ") if tds[3].text is not None else "",
                        "capital": tds[4].text.strip().replace("\n", " ").replace("  ", " ") if tds[4].text is not None else "",
                    }
                    people_detail.append({
                        "name": tds[1].text.strip().replace("\n", " ").replace("  ", " ") if tds[1].text is not None else "",
                        "nationality": tds[2].text.strip().replace("\n", " ").replace("  ", " ") if tds[2].text is not None else "",
                        "designation": "shareholder",
                        "meta_detail": meta_detail
                    })
            if(next_page_button()):
                break
    return people_detail

def get_fillings_detail(browser):
    """
    Description: Retrieve details about legal filings from the 'Actos jurídicos' section. This function navigates to the 'Actos jurídicos' section, extracts information from the HTML,
    and organizes it into a list of dictionaries. Each dictionary represents details about a legal filing,
    including title, filing code, date, and additional metadata such as commercial register number,
    commercial registration date, and effective date.

    @param:
    - browser (WebDriver): The browser instance where the 'Actos jurídicos' section is present.

    @return:
    - list: A list of dictionaries containing details about legal filings.
    """
    fillings_detail = []
    target_anchor = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Actos jurídicos")))
    if target_anchor:
        browser.execute_script("arguments[0].click();", target_anchor)
        identify_captcha(browser)
        wait.until(EC.presence_of_element_located((By.ID, "frmInformacionCompanias:tblActosJuridicos_data")))
        while True:
            soup = BeautifulSoup(browser.page_source, "html.parser")
            tbody = soup.find("tbody", {"id": "frmInformacionCompanias:tblActosJuridicos_data"})
            trs = tbody.find_all("tr")
            if len(trs) > 1:
                for tr in trs:
                    tds = tr.find_all("td")
                    meta_detail = {
                        # "details_url": tds[6].text.strip().replace("\n", " ").replace("  ", " ") if tds[6].text is not None else "",
                        "commercial_register_number": tds[3].text.strip().replace("\n", " ").replace("  ", " ") if tds[3].text is not None else "",
                        "commercial_registration_date": tds[4].text.strip().replace("\n", " ").replace("  ", " ") if tds[4].text is not None else "",
                        "effective_date": tds[5].text.strip().replace("\n", " ").replace("  ", " ") if tds[5].text is not None else ""
                    }
                    fillings_detail.append({
                        "title": tds[0].text.strip().replace("\n", " ").replace("  ", " ") if tds[0].text is not None else "",
                        "filing_code": tds[1].text.strip().replace("\n", " ").replace("  ", " ") if tds[1].text is not None else "",
                        "date": tds[2].text.strip().replace("\n", " ").replace("  ", " ") if tds[2].text is not None else "",
                        "meta_detail": meta_detail,
                    })
            if(next_page_button()):
                break
    return fillings_detail

def get_people_detail(driver):
    """
    Description: Retrieve details about current administrators from the 'Administradores actuales' section. This function navigates to the 'Administradores actuales' section, extracts information from the HTML,
    and organizes it into a list of dictionaries. Each dictionary represents details about a current administrator,
    including name, nationality, designation, appointment date, and additional metadata such as identification number,
    commercial register number, commercial registration date, rl_or_adm, file URL, and period.
    @param:
    - driver (WebDriver): The WebDriver instance where the 'Administradores actuales' section is present.
    @return:
    - list: A list of dictionaries containing details about current administrators.
    """
    people_detail = []
    target_anchor = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Administradores actuales")))
    if target_anchor:
        driver.execute_script("arguments[0].click();", target_anchor)
        identify_captcha(driver)
        wait.until(EC.presence_of_element_located((By.ID, "frmInformacionCompanias:tblAdministradoresActuales_data")))
        while True:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            tbody = soup.find("tbody", {"id": "frmInformacionCompanias:tblAdministradoresActuales_data"})
            trs = tbody.find_all("tr")
            if len(trs) > 1:
                for row_index, tr in enumerate(trs):
                    tds = tr.find_all("td")
                    xpath = f"/html/body/div[3]/div/form/span[1]/div/div/table[2]/tbody/tr[2]/td/div/div[1]/table/tbody/tr[{row_index+1}]/td[10]"
                    document_url = get_pdf_url(driver, xpath)
                    meta_detail = {
                        "identification_number": tds[0].text.strip().replace("\n", " ").replace("  ", " ") if tds[0].text is not None else "",
                        "commercial_register_number": tds[6].text.strip().replace("\n", " ").replace("  ", " ") if tds[6].text is not None else "",
                        "commercial_registration_date": tds[7].text.strip().replace("\n", " ").replace("  ", " ") if tds[7].text is not None else "",
                        "rl_or_adm": tds[8].text.strip().replace("\n", " ").replace("  ", " ") if tds[8].text is not None else "",
                        "file_url": document_url if document_url is not None else "",
                        "period": tds[5].text.strip().replace("\n", " ").replace("  ", " ") if tds[5].text is not None else ""
                    }
                    people_detail.append({
                        "name": tds[1].text.strip().replace("\n", " ").replace("  ", " ") if tds[1].text is not None else "",
                        "nationality": tds[2].text.strip().replace("\n", " ").replace("  ", " ") if tds[2].text is not None else "",
                        "designation": tds[3].text.strip().replace("\n", " ").replace("  ", " ") if tds[3].text is not None else "",
                        "appointment_date": tds[4].text.strip().replace("\n", " ").replace("  ", " ") if tds[4].text is not None else "",
                        "meta_detail": meta_detail
                    })
            if(next_page_button()):
                break
    return people_detail

def get_page_data(soup):
    """
    Extract label-value pairs from a BeautifulSoup object representing a page. This function takes a BeautifulSoup object representing the HTML structure of a page,
    extracts label-value pairs from the specified elements (columna1 and columna2),
    and organizes them into a dictionary. The function is designed to work with pages
    that have rows containing label and value elements.
    @param:
    - soup (BeautifulSoup): The BeautifulSoup object representing the HTML structure of the page.
    @return:
    - dict: A dictionary containing label-value pairs extracted from the page.
    """
    rows = soup.find_all('tr', class_='ui-widget-content')
    # Initialize a list to store label-value pairs for each row
    label_value_pairs = {}
    # Iterate through each row
    for row in rows:
        columna1_elements = row.find_all('td', class_='columna1')
        columna2_elements = row.find_all('td', class_='columna2')
        for label_elem, value_elem in zip(columna1_elements, columna2_elements):
            label = label_elem.text.strip()
            if label in label_value_pairs:
                continue
            value_elem_input = value_elem.find('input')
            if value_elem_input:
                value = value_elem_input.get('value', '').strip()
            else:
                value = value_elem.text.strip()
            
            label_value_pairs[label] = value.replace("\n", " ").replace("  ", " ") if value is not None else ""
    return label_value_pairs

def get_data(soup, driver):
    """
    Extracts detailed information about a company from its web page.
    @param:
    - soup (BeautifulSoup): The BeautifulSoup object representing the HTML structure of the page.
    - driver: The WebDriver instance for browser automation.
    @return:
    - dict: A dictionary containing various details about the company.
    """
    data = {}
    contacts_detail = []
    additional_detail = []
    addresses_detail = []
    people_detail = []
    fillings_detail = []
    res = get_page_data(soup)
    data["registration_number"] = res.get("R.U.C.:")
    data["status"] = res.get("Situación legal:")
    data["type_of_company"] = res.get("Tipo de compañía:")
    data["proceeding_number"] = res.get("EXPEDIENTE:")
    contacts_detail.append({"type": "phone_number", "value": res.get("Teléfono 1:")})
    contacts_detail.append({"type": "mobile_number", "value": res.get("Celular:")})
    contacts_detail.append({"type": "phone_number_2", "value": res.get("Teléfono 2:")})
    contacts_detail.append({"type": "website", "value": res.get("Sitio web:")})
    contacts_detail.append({"type": "email", "value": res.get("Correo 1:")})
    contacts_detail.append({"type": "email_2", "value": res.get("Correo 2:")})
    data["term_date"] = res.get("Plazo social:")
    data["jurisdiction"] = res.get("Nacionalidad:")
    data["control_office"] = res.get("Oficina de control:")
    data["are_you_a_supplier_of_goods_or_services_to_the_state"] = res.get("¿Es proveedora de bienes o servicios del Estado?:")
    data["does_it_belong_to_mv"] = res.get("¿Pertenece a MV?:")
    data["year_since_it_is_a_bic_company"] = res.get("Año desde que es una compañía BIC:")
    data["judicial_provision_that_affects_the_company"] = res.get("Disposición judicial que afecta a la compañía:")
    data["do_you_offer_remittance_payment_services"] = res.get("¿Ofrece servicios de pagos a remesas?:")
    data["is_it_a_public_interest_company"] = res.get("Es sociedad de interés público?")
    data["bic_impact_areas"] = res.get("Areas impacto BIC:")
    data["date_of_last_corporate_update"] = res.get("Fecha última actualización societaria:")
    data["does_the_company_sell_on_credit"] = res.get("¿Compañía vende a crédito?:")
    data["is_it_a_bic_company"] = res.get("¿Es una compañía BIC?:")
    data["industries"] = res.get("Objeto social:")
    labels = soup.find_all('label', string="Descripción:")
    if labels:
        description = []
        for label in labels:
            description.append(label.find_next('textarea').get_text(strip=True))
    additional_detail.append({
        "type": "activities_information",
        "data": [{
            "activity_level_2": res.get("CIIU actividad nivel 2:"),
            "main_activity": res.get("CIIU operación principal:"),
            "activity_level_2_description": description[0] if len(description) > 0 else "",
            "main_activity_description": description[1] if len(description) > 1 else "",
        }]
    })
    additional_detail.append({
        "type": "capital_information",
        "data": [{
            "subscribed_capital": res.get("Capital suscrito:"),
            "authorized_capital": res.get("Capital autorizado:"),
            "shares_nominal_value": res.get("Valor nominal acciones:")
        }]
    })
    addresses_detail.append({
        "type": "general_address",
        "address": f'{res.get("Piso:")} {res.get("Conjunto:")} {res.get("Edificio/Centro comercial:")} {res.get("Barrio:")} {res.get("Intersección:")} {res.get("Número:")} {res.get("Calle:")} {res.get("Ciudad:")} {res.get("Cantón:")} {res.get("Provincia:")}'
    })
    people_detail.extend(get_people_detail(driver))
    people_detail.extend(get_accionistas(driver))
    fillings_detail.extend(get_fillings_detail(driver))
    additional_detail.extend(get_beneficiarios_finales(driver))
    additional_detail.extend(get_informacion_anual_presentada(driver))
    additional_detail.extend(get_inf_sociedades_extranjeras(driver))
    additional_detail.extend(get_documentos_online(driver))
    additional_detail.extend(get_consulta_de_cumplimiento(driver))
    people_detail.extend(get_administradores_anteriores(driver))
    additional_detail.extend(get_notificaciones_generales(driver))
    data["people_detail"] = people_detail
    data["fillings_detail"] = fillings_detail
    data["addresses_detail"] = addresses_detail
    data["contacts_detail"] = contacts_detail
    data["additional_detail"] = additional_detail
    return data
try:
    max_retries = 3
    page_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    driver.get("https://mercadodevalores.supercias.gob.ec/reportes/directorioCompanias.jsf")
    skip_pages(page_no)
    while True:
        print(f"Page No: {page_no}")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ui-commandlink.ui-widget")))
        elements = driver.find_elements(By.CSS_SELECTOR, ".ui-commandlink.ui-widget")
        for element in elements:
            retries = 0
            while retries < max_retries:
                try:
                    tr_element = element.find_element(By.XPATH, './ancestor::tr')
                    td_elements = tr_element.find_elements(By.TAG_NAME, 'td')
                    country = td_elements[7].text
                    region = td_elements[8].text
                    registration_date = td_elements[5].text
                    element.click()
                    while True:
                        if len(driver.window_handles) > 1:
                            driver.switch_to.window(driver.window_handles[1])
                            break
                    name_element = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]")))
                    NAME = name_element.text
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    DATA = get_data(soup, driver)
                    DATA["registration_date"] = registration_date.replace("/", "-") if registration_date is not None else ""
                    address = f'{DATA["addresses_detail"][0]["address"]} {region} {country}'
                    DATA["addresses_detail"][0]["address"] = address.replace("  ", " ").strip() if address is not None else ""
                    registration_number  = DATA.get('registration_number')
                    ENTITY_ID = ecuador_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
                    BIRTH_INCORPORATION_DATE = ''
                    print(f"Registration_number: {registration_number}, Name: {NAME}, Page: {page_no}")
                    DATA = ecuador_crawler.prepare_data_object(DATA)
                    ROW = ecuador_crawler.prepare_row_for_db(ENTITY_ID, NAME.replace("%","%%"), BIRTH_INCORPORATION_DATE, DATA)
                    ecuador_crawler.insert_record(ROW)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    break
                except (TimeoutException, ElementClickInterceptedException) as e:
                    print(f"Timeout exception occurred on page {page_no}. Retrying...")
                    retries += 1
                    if len(driver.window_handles) == 2:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
        page_no += 1
        try:
            next_page_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ui-paginator-next")))
            next_page_button.click()
        except:
            break
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    ecuador_crawler.db_log(log_data)
    ecuador_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    ecuador_crawler.db_log(log_data)
display.stop()