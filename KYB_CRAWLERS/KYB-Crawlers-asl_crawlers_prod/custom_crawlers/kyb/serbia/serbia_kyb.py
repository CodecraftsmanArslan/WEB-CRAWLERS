"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from pyvirtualdisplay import Display

meta_data = {
    'SOURCE' :'Serbian Business Registers Agency (SBRA) - Serbian Business Registry',
    'COUNTRY' : 'Serbia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://pretraga2.apr.gov.rs/unifiedentitysearch", 
                        "Source Description": "Register of business entities, in accordance with the Law on the procedure of registration in the Agency for Business Registers (began operation on January 1, 2005). The following are kept within this register: Register of business companies (started on January 1, 2005) Register of entrepreneurs (maintained since January 1, 2006) Register of foreign representative offices (maintained since January 1, 2006)"},
    'URL' : 'https://pretraga2.apr.gov.rs/unifiedentitysearch',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Serbia Official Registry'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://pretraga2.apr.gov.rs/unifiedentitysearch'

display = Display(visible=0,size=(800,600))
display.start()
serbia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper =  serbia_crawler.get_selenium_helper()
driver = selenium_helper.create_driver(headless=False,Nopecha=True)
driver.set_page_load_timeout(120)
wait = WebDriverWait(driver, 10)

def wait_for_captcha_to_be_solved(browser):
    while True:
        iframe_element = browser.find_element(By.XPATH, '//*[@id="captcha"]//iframe[@title="reCAPTCHA"]')
        browser.switch_to.frame(iframe_element)
        time.sleep(3)
        if len(browser.find_elements(By.CLASS_NAME,"recaptcha-checkbox-checked")) > 0:
            browser.switch_to.default_content()
            print("Captcha has been Solved")
            return browser 
        browser.switch_to.default_content()

def get_next_sibling_td_txt(soup, keyword):
    ths = soup.find_all('th')
    for th in ths:
        if keyword in th.text:
            td = th.find_next_sibling('td')
            if td:
                return td.text.strip()
    return ""

def get_next_td_txt(soup, keyword):
    ths = soup.find_all('th')
    for th in ths:
        if keyword in th.text:
            td = th.find_next('td')
            if td:
                return td.text.strip()
    return ""


def get_key_value_pair(soup):
    result = {}
    ths = soup.find_all('th')
    tbody = soup.find_all('tbody')
    tr = tbody[1].find('tr')
    tds = tr.find_all('td')
    for th, td in zip(ths, tds):
        result[th.text.strip()] = td.text.strip()
    return result
        
def key_value_pair(soup, keyword):
    res = []
    caption = soup.find('caption', string=keyword)
    if caption is not None:
        table = caption.find_parent('table')
        ths = table.find('thead').find_all('th')
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            key_value = {}
            tds = tr.find_all('td')
            if len(tds) == 9:
                for th, td in zip(ths, tds):
                    key_value[th.text.strip()] = td.text.strip()
                res.append(key_value)
    return res


def table_key_value_pair(table):
    res = []
    thead = table.find('thead')
    if thead is not None:
        ths = thead.find_all('th')
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        if len(trs) == 0:
            try:
                tbody = table.find_all('tbody')
                trs = tbody[1].find_all('tr')
            except:
                pass
        for tr in trs:
            key_value = {}
            tds = tr.find_all('td')
            if len(tds) == len(ths):
                for th, td in zip(ths, tds):
                    if td.text.strip() != '-' and td.text is not None:
                        key_value[th.text.strip()] = td.text.strip()
                res.append(key_value)
    return res

def get_table_th_td(table):
    key_value_pair = {}
    trs = table.find_all('tr')
    for tr in trs:
        key = tr.find('th').text.strip() if tr.find('th') else ''
        value = tr.find('td').text.strip() if tr.find('td') else ''
        if key != '':
            key_value_pair[key] = value
    return key_value_pair

def find_anchor(soup, keyword):
    anchors = soup.find_all('a')
    for anchor in anchors:
        if keyword in anchor.text:
            return anchor
        
def find_anchor_table(soup, keyword):
    anchors = soup.find_all('a')
    for anchor in anchors:
        if keyword in anchor.text:
            return anchor.find_next('table')
        
def get_data(browser):
    item = {}
    addresses_detail = []
    contacts_detail = []
    additional_detail = []
    people_detail = []
    filling_detail = []
    
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    item['name'] = get_next_sibling_td_txt(soup, 'Назив')
    item['aliases'] = get_next_sibling_td_txt(soup, 'Пословно име')
    item['status'] = get_next_sibling_td_txt(soup, 'Статус')
    item['type'] = get_next_sibling_td_txt(soup, 'Правна форма')
    item['registration_number'] = get_next_sibling_td_txt(soup, 'Матични број')
    item['registration_date'] = get_next_sibling_td_txt(soup, 'Датум оснивања').replace('.', '-')
    item['dissolution_date'] = get_next_sibling_td_txt(soup, 'Датум брисања из регистра').replace('.', '-')

    # Лични подаци предузетника
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Лични подаци предузетника')]")
    if len(element) > 0:
        time.sleep(3)
        element[0].click()
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        founder_name = get_next_sibling_td_txt(soup, 'Име и презиме ')
        founder_id = get_next_sibling_td_txt(soup, 'ЈМБГ')
        founder_gender = get_next_sibling_td_txt(soup, 'Пол')
        if founder_name != "":
            people_detail.append({
                'designation': 'founder',
                'name': founder_name,
                'meta_detail': {
                    'id': founder_id,
                    'gender': founder_gender
                }
            })

    
    # Пословно име
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Пословно име')]")
    if len(element) > 0:
        time.sleep(3)
        element[0].click()
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        item['aliases_1'] = get_next_sibling_td_txt(soup, 'Пословно име')
        item['aliases_2'] = get_next_sibling_td_txt(soup, 'Скраћено пословно име')


    # Подаци о адресама
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Подаци о адресама')]")
    if len(element) > 0:
        time.sleep(3)
        element[0].click()
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        general_address = f"{get_next_sibling_td_txt(soup, 'Назив општине')} {get_next_sibling_td_txt(soup, 'Место')} {get_next_sibling_td_txt(soup, 'Улица, број и слово')} {get_next_sibling_td_txt(soup, 'Број поште')} {get_next_sibling_td_txt(soup, 'Назив поште')}"
        addresses_detail.append({
            'type': 'general_address',
            'address': general_address,
        })
        postal_address = f"{get_next_sibling_td_txt(soup, 'Назив општине')} {get_next_sibling_td_txt(soup, 'Место')} {get_next_sibling_td_txt(soup, 'Улица, број и слово')} {get_next_sibling_td_txt(soup, 'Спрат, број стана и слово')}"
        addresses_detail.append({
            'type': 'postal_address',
            'address': postal_address
        })
        email = get_next_sibling_td_txt(soup, 'Е-пошта:')
        if email != '':
            contacts_detail.append({
                'type': 'email',
                'value': email
            })


    # Пословни подаци
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Пословни подаци')]")
    if len(element) > 0:
        time.sleep(3)
        element[0].click()
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        item['duration'] = get_next_sibling_td_txt(soup, 'Време трајања')
        item['tax_number'] = get_next_sibling_td_txt(soup, 'Порески идентификациони број ПИБ')
        item['rzzo_id'] = get_next_sibling_td_txt(soup, 'РЗЗО број')

        name_and_code_of_activity = get_next_sibling_td_txt(soup, 'Шифра делатности')
        if name_and_code_of_activity != '':
            additional_detail.append({
                'type': 'predominant_activity_info',
                'data':[{
                    'name': name_and_code_of_activity.split('-')[0] if '-' in name_and_code_of_activity and len(name_and_code_of_activity.split('-')) > 0 else '',
                    "code": name_and_code_of_activity.split('-')[-1] if '-' in name_and_code_of_activity and len(name_and_code_of_activity.split('-')) > 1 else '',
                    'description': get_next_sibling_td_txt(soup, 'Опис делатности'),
                    'activities_commenced': get_next_sibling_td_txt(soup, 'Датум почетка обављања делатности').replace('.', '-')
                }]
            })

        item['term'] = get_next_sibling_td_txt(soup, 'Трајање ограничено до')
        item['temporary_suspension_date'] = get_next_sibling_td_txt(soup, 'Датум привременог прекида')
        
        
        # Пословни подаци
        account_number = get_next_td_txt(soup, 'Бројеви текућих рачуна')
        if account_number != '':
            additional_detail.append({
                'type': 'payment_details',
                'data': [{
                    'account_number': account_number
                }]
            })

    # Контакт подаци
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Контакт подаци')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        telephone_1 = get_next_sibling_td_txt(soup, 'Телефон 1')
        if telephone_1 != '':
            contacts_detail.append({
                'type': 'phone_number',
                'value': telephone_1
            })
        telephone_2 = get_next_sibling_td_txt(soup, 'Телефон 2')
        if telephone_2 != '':
            contacts_detail.append({
                'type': 'phone_number',
                'value': telephone_2
            })

    # Legal Representatives
    # Законски заступници
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Законски заступници')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        legal_repre_anchor = find_anchor(soup, 'Законски заступници')
        if legal_repre_anchor:
            legal_repre_anchor_div = legal_repre_anchor.find_parent('div')
            legal_repre_div = legal_repre_anchor_div.find_next_sibling('div')
            legal_repre_tbl = legal_repre_div.find('table')
            if legal_repre_tbl:
                legal_repre_data = table_key_value_pair(legal_repre_tbl)
                for legal_repre_d in legal_repre_data:
                    people_detail.append({
                        'name': legal_repre_d.get('Име и презиме', ''),
                        'designation': legal_repre_d.get('Функција', ''),
                        'meta_detail': {
                            'id': legal_repre_d.get('ЈМБГ', ''),
                            'foriegner_id': legal_repre_d.get('Број личне карте странца', ''),
                            'passport_id': legal_repre_d.get('Број пасоша', ''),
                            'country_issued': legal_repre_d.get('Држава издавања3', ''),
                            'foreigner_personal_number': legal_repre_d.get('Лични број за странце', ''),
                            'gender': legal_repre_d.get('Пол', ''),
                            'represents_himself': legal_repre_d.get('Самостално заступа', ''),
                            'restrictions_by_cosignature': legal_repre_d.get('Ограничења супотписом', '')
                        }
                    })


    # Other representatives
    # Остали заступници
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Остали заступници')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        other_repres_anchor = find_anchor(soup, 'Остали заступници')
        if other_repres_anchor:
            other_repres_anchor_div = other_repres_anchor.find_parent('div')
            other_repres_div = other_repres_anchor_div.find_next_sibling('div')
            other_repres_tbl = other_repres_div.find('table')
            if other_repres_tbl:
                other_repres_data = table_key_value_pair(other_repres_tbl)
                for other_repres_d in other_repres_data:
                    people_detail.append({
                        'name': other_repres_d.get('Име и презиме', ''),
                        'designation': other_repres_d.get('Функција', ''),
                        'meta_detail': {
                            'id': other_repres_d.get('ЈМБГ', ''),
                            'foriegner_id': other_repres_d.get('Број личне карте странца', ''),
                            'passport_id': other_repres_d.get('Број пасоша', ''),
                            'country_issued': other_repres_d.get('Држава издавања3', ''),
                            'foreigner_personal_number': other_repres_d.get('Лични број за странце', ''),
                            'gender': other_repres_d.get('Пол', ''),
                            'represents_himself': other_repres_d.get('Самостално заступа', ''),
                            'restrictions_by_cosignature': other_repres_d.get('Ограничења супотписом', '')
                        }
                    })


    # Извршни одбор
    # Executive Board
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Извршни одбор')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        executive_board_anchor = find_anchor(soup, 'Извршни одбор')
        if executive_board_anchor:
            executive_board_anchor_div = executive_board_anchor.find_parent('div')
            executive_board_div = executive_board_anchor_div.find_next_sibling('div')
            executive_board_tbl = executive_board_div.find('table')
            if executive_board_tbl:
                executive_board = table_key_value_pair(executive_board_tbl)
                for exe_board in executive_board:
                    people_detail.append({
                        'name': exe_board.get('Име и презиме', ''),
                        'designation': exe_board.get('Функција', ''),
                        'meta_detail': {
                            'id': exe_board.get('ЈМБГ', ''),
                            'foriegner_id': exe_board.get('Број личне карте странца', ''),
                            'passport_id': exe_board.get('Број пасоша', ''),
                            'country_issued': exe_board.get('Држава издавања', ''),
                            'foreigner_personal_number': exe_board.get('Лични број за странце', ''),
                            'gender': exe_board.get('Пол', '')
                        }
                    })

    # Управни одбор
    # Board of Directors
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Управни одбор')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        board_of_directors_tbl = find_anchor_table(soup, 'Управни одбор')
        if board_of_directors_tbl:
            board_of_directors = table_key_value_pair(board_of_directors_tbl)
            if len(board_of_directors) > 0: 
                for directive in board_of_directors:
                    people_detail.append({
                        'name': directive.get('Име и презиме', ''),
                        'designation': directive.get('Функција', ''),
                        'meta_detail': {
                            'id': directive.get('ЈМБГ', ''),
                            'foriegner_id': directive.get('Број личне карте странца', ''),
                            'passport_id': directive.get('Број пасоша', ''),
                            'country_issued': directive.get('Држава издавања', ''),
                            'foreigner_personal_number': directive.get('Лични број за странце', ''),
                            'gender': directive.get('ПолPol', '')
                        }
                    })

    # Издвојена места
    # Separated places
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Издвојена места')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        activities_info = []
        separated_places_anchor = find_anchor(soup, 'Издвојена места')
        if separated_places_anchor:
            separated_places_div = separated_places_anchor.find_parent('div')
            separated_places_sib = separated_places_div.find_next_sibling('div')
            separated_places_sib_tbls = separated_places_sib.find_all('table')
            for sep_places_tbl in separated_places_sib_tbls:
                sep_places_data = get_table_th_td(sep_places_tbl)
                separated_place_address = f"{sep_places_data.get('Општина', '')} {sep_places_data.get('Место', '')} {sep_places_data.get('Улица', '')} {sep_places_data.get('Број и слово', '')} {sep_places_data.get('Спрат, број стана и слово', '')}"
                activities_info.append({
                    'code': sep_places_data.get('Шифра делатности:', ''),
                    'name': sep_places_data.get('Назив делатности', ''),
                    'description': sep_places_data.get('Додатни опис', ''),
                    'address': separated_place_address
                })
            additional_detail.append({
                'type': 'activities_info',
                'data': activities_info
            })


    # Основни капитал
    # fixed_capital
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Основни капитал')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        fixed_capital_info = []
        fixed_capital_anchor = find_anchor(soup, 'Основни капитал')
        if fixed_capital_anchor:
            fixed_capital_div = fixed_capital_anchor.find_parent('div')
            fixed_capital_sib = fixed_capital_div.find_next_sibling('div')
            fixed_capital_tbl = fixed_capital_sib.find('table')
            if fixed_capital_tbl:
                fixed_capital_tbody = fixed_capital_tbl.find('tbody')
                fixed_capital_trs = fixed_capital_tbody.find_all('tr')
                for fixed_capital_tr in fixed_capital_trs:
                    fixed_capital_tds = fixed_capital_tr.find_all('td')
                    fixed_capital_info.append({
                        'status': fixed_capital_tds[0].text.strip(),
                        'value': fixed_capital_tds[1].text.strip(),
                        'date': fixed_capital_tds[2].text.strip().replace('.', '-'),
                    })
                additional_detail.append({
                    'type': 'fixed_capital_info',
                    'data': fixed_capital_info
                })

    # Чланови
    # Members
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Чланови')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        member_tb_info = []
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        members_anchor = find_anchor(soup, 'Чланови')
        if members_anchor:
            members_anchor_div = members_anchor.find_parent('div')
            members_div = members_anchor_div.find_next_sibling('div')
            members_table = members_div.find_all('table', class_='apr-table-with-labels-upright')
            for member_tbl in members_table:
                member_shareholder_name = get_next_td_txt(member_tbl, 'Пословно име')
                if member_shareholder_name == '':
                    member_shareholder_name = get_next_td_txt(member_tbl, 'Име и презиме')

                people_detail.append({
                    'name': member_shareholder_name,
                    'address': get_next_td_txt(member_tbl, 'Адреса'),
                    'designation': get_next_td_txt(member_tbl, 'Улога члана'),
                    'meta_detail': {
                        'id': get_next_td_txt(member_tbl, 'Матични број'),
                    }
                })
                member_tb_tbl = member_tbl.find_next('table')
                if member_tb_tbl:
                    member_tb_tbody = member_tb_tbl.find('tbody')
                    member_tb_trs = member_tb_tbody.find_all('tr')
                    for member_tb_tr in member_tb_trs:
                        member_tb_tds = member_tb_tr.find_all('td')
                        member_tb_info.append({
                            'shareholder_name': member_shareholder_name,
                            'status': member_tb_tds[0].text.strip(),
                            'value': member_tb_tds[1].text.strip(),
                            'date': member_tb_tds[2].text.strip().replace('.', '-'),
                        })

            additional_detail.append({
                'type': 'shareholder_cash_stake_info',
                'data': member_tb_info
            })


    # Забележбе
    # Note
    time.sleep(3)
    note_info = []
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Забележбе')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        note_anchor = find_anchor(soup, 'Забележбе')
        if note_anchor:
            note_anchor_div = note_anchor.find_parent('div')
            note_div_main = note_anchor_div.find_next_sibling('div')
            note_span_div = note_div_main.find('div', class_='span12')
            if note_span_div:
                notes_div = note_span_div.find_all('div', class_='row-fluid')
                for note_div in notes_div:
                    if note_div.find('caption'):
                        note_info.append({
                            'title': note_div.find('caption').text.strip() if note_div.find('caption') else '',
                            'date': get_next_td_txt(note_div, 'Датум').replace('.', '-'),
                            'description': get_next_td_txt(note_div, 'Текст')
                        }) 
                if len(note_info) > 0:
                    additional_detail.append({
                        'type': 'notes',
                        'data': note_info
                    })

    # Огласи и обавештења
    # Advertisements and Notices
    time.sleep(3)
    element = driver.find_elements(By.XPATH, "//a[contains(text(), 'Огласи и обавештења')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        adver_notices_anchor = find_anchor(soup, 'Огласи и обавештења')
        if adver_notices_anchor:
            adver_notices_anchor_div = adver_notices_anchor.find_parent('div')
            adver_notices_div = adver_notices_anchor_div.find_next_sibling('div')
            additional_detail.append({
                'type': 'advertisements_and_notices',
                'data': [{
                    'date_published': get_next_td_txt(adver_notices_div, 'Датум објаве ').replace('.', '-'),
                    'date': get_next_td_txt(adver_notices_div, 'Датум истека важења - архивирања').replace('.', '-'),
                    'description': get_next_td_txt(adver_notices_div, 'Aрхивирани оглас/обавештење'),
                }]
            }) 


    # Документи о стечају
    # Bankruptcy Documents
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Документи о стечају')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        bankruptcy_info = []
        bankrupty_doc_anchor = find_anchor(soup, 'Документи о стечају')
        if bankrupty_doc_anchor:
            bankrupty_doc_anchor_div = bankrupty_doc_anchor.find_parent('div')
            bankrupty_doc_div = bankrupty_doc_anchor_div.find_next_sibling('div')
            bankrupty_doc_tbl = bankrupty_doc_div.find('table')
            if bankrupty_doc_tbl:
                bankrupty_doc_tbody = bankrupty_doc_tbl.find('tbody')
                bankrupty_doc_trs = bankrupty_doc_tbody.find_all('tr')
                for bankrupty_doc_tr in bankrupty_doc_trs:
                    bankrupty_doc_tds = bankrupty_doc_tr.find_all('td')
                    bankruptcy_info.append({
                        'court': bankrupty_doc_tds[0].text.strip(),
                        'type': bankrupty_doc_tds[1].text.strip(),
                        'code': bankrupty_doc_tds[2].text.strip(),
                        'date': bankrupty_doc_tds[3].text.strip().replace('.', '-'),
                        'url': bankrupty_doc_tds[4].find('a')['href'] if bankrupty_doc_tds[4].find('a') else '',
                    })
                additional_detail.append({
                    'type': 'bankruptcy_info',
                    'data': bankruptcy_info
                })

    # Објављени документи
    # Published Documents
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Објављени документи')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        published_doc_anchor = find_anchor(soup, 'Објављени документи')
        if published_doc_anchor:
            published_doc_anchor_div = published_doc_anchor.find_parent('div')
            published_doc_div = published_doc_anchor_div.find_next_sibling('div')
            item['obligated_to_certify_founding_act'] = get_next_td_txt(published_doc_div, 'Постоји обавеза овере измене оснивачког акта')
            published_doc_tbl = published_doc_div.find_all('table')
            if len(published_doc_tbl) == 2:
                published_doc_tbody = published_doc_tbl[1].find('tbody')
                published_doc_trs = published_doc_tbody.find_all('tr')
                for published_doc_tr in published_doc_trs:
                    published_doc_tds = published_doc_tr.find_all('td')
                    filling_detail.append({
                        'filing_code': published_doc_tds[0].text.strip(),
                        'date': published_doc_tds[1].text.strip().replace('.', '-'),
                        'filing_type': published_doc_tds[2].text.strip(),
                        'file_url': published_doc_tds[2].find('a')['href'] if published_doc_tds[2].find('a') else '',
                        'meta_detail': {
                            'effective_date': published_doc_tds[3].text.strip().replace('.', '-')
                        }
                    })

    # Одлуке регистратора
    # Decisions of the registrar
    time.sleep(3)
    element = browser.find_elements(By.XPATH, "//a[contains(text(), 'Одлуке регистратора')]")
    if len(element) > 0:
        element[0].click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        registrar_details = []
        deci_reg_anchor = find_anchor(soup, 'Одлуке регистратора')
        if deci_reg_anchor:
            deci_reg_anchor_div = deci_reg_anchor.find_parent('div')
            deci_reg_div = deci_reg_anchor_div.find_next_sibling('div')
            deci_reg_tbl = deci_reg_div.find('table')
            if deci_reg_tbl:
                
                deci_reg_tbody = deci_reg_tbl.find('tbody')
                deci_reg_trs = deci_reg_tbody.find_all('tr', class_='apr-details-row')
                for deci_reg_tr in deci_reg_trs:
                    deci_reg_tds = deci_reg_tr.find_all('td')
                    registrar_details.append({
                        'url': deci_reg_tds[0].find('a')['href'] if deci_reg_tds[0].find('a') else '',
                        'title': deci_reg_tds[0].text.strip().replace('\n', ' ').replace('  ',''),
                    })
                additional_detail.append({
                    'type': 'registrar_details',
                    'data': registrar_details
                })

    item['fillings_detail'] = filling_detail
    item['people_detail'] = people_detail
    item['contacts_detail'] = contacts_detail
    item['additional_detail'] = additional_detail

    return item

try:
    max_retries = 3
    start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 0 #60825947
    for reg_num in range(start_number, 69000000):
        retries = 0
        while retries < max_retries:
            try:
                reg_num = str(reg_num).zfill(8)
                print(f"Record No: {reg_num}")
                driver.get(BASE_URL)
                radio_btn = driver.find_elements(By.XPATH, '//div[@id="content"]//input[@name="rdbtnSelectInputType"]')
                try:
                    radio_btn[6].click()
                    input_box = driver.find_elements(By.NAME, 'SearchByRegistryCodeString')
                    input_box[1].clear()
                    input_box[1].send_keys(reg_num)
                    submit_btn = driver.find_elements(By.CLASS_NAME, 'btn-primary')
                    submit_btn[1].click()
                except:
                    radio_btn[2].click()
                    input_box = driver.find_elements(By.NAME, 'SearchByRegistryCodeString')
                    input_box[0].clear()
                    input_box[0].send_keys(reg_num)
                    submit_btn = driver.find_elements(By.CLASS_NAME, 'btn-primary')
                    submit_btn[0].click()
                
                td_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*/table/tbody/tr/td[5]/a')))
                td_btn.click()
                wait_for_captcha_to_be_solved(driver)
                detail_btn = driver.find_element(By.XPATH, '//*[@id="captcha"]/div[2]/button')
                detail_btn.click()
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='results']//div[@id='content']")))
                data = get_data(driver)
                print(data)
                if data.get('name') == '' and data.get('registration_number') == '':
                    continue
                ENTITY_ID = serbia_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
                BIRTH_INCORPORATION_DATE = ''
                DATA = serbia_crawler.prepare_data_object(data)
                ROW = serbia_crawler.prepare_row_for_db(ENTITY_ID, data.get('name'), BIRTH_INCORPORATION_DATE, DATA)
                serbia_crawler.insert_record(ROW)
                break
            except (TimeoutException, ElementClickInterceptedException) as e:
                time.sleep(10)
                print(f"Timeout exception occurred on {reg_num}. Retrying...")
                start_number = reg_num
                retries += 1

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    serbia_crawler.db_log(log_data)
    serbia_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    serbia_crawler.db_log(log_data)
display.stop()