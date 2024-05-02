"""Import required library"""
import sys, traceback,time, re,requests
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from CustomCrawler import CustomCrawler


meta_data = {
    'SOURCE' :'Open Corporates Albania',
    'COUNTRY' : 'Albania',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://opencorporates.al/sq/searching", 
                        "Source Description": "The Open Corporates Albania website, which provides information of an economic nature, in the Albanian language, boasts a record number of clicks. Over 20 thousand unique users every month, Open Corporates Albania has resulted to be a favourable website for the information it provides for business companies contracted by public institutions."},
    'URL' : 'https://opencorporates.al/sq/searching',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Albania Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'


Albania = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
selenium_helper = Albania.get_selenium_helper()

# driver.get("https://opencorporates.al/sq/searching")


# search_element=driver.find_element(By.XPATH,"//input[@name='nuis']")
# search_element.send_keys("J61911005B")


# time.sleep(2)

# submit_value=driver.find_element(By.XPATH,"//input[@value='Kërko']")
# submit_value.click()

# time.sleep(2)




r=requests.get("https://opencorporates.al/sq/nipt/j61911005b")

soup = BeautifulSoup(r.content, 'html.parser')


additional_detail=[]
data = []
pattern = re.compile(r"Fitimi para Tatimit\(Lekë\) (\d{4}):\s([\d\s,.]+)")
for item in soup.find_all(text=pattern):
    match = pattern.search(item)
    year, profit = match.group(1), match.group(2).replace(" ", "").replace(",", ".")
    data.append((year, profit))

# Print the extracted data
for year, profit in data:
    additional_detail.append({
        'type': 'financial_details',
        'year':year,
        'pre_tax_profit':profit

    })

data = []
pattern = re.compile(r"Xhiro Vjetore\(Lekë\) (\d{4}):\s([\d\s,.]+)")
for item in soup.find_all(text=pattern):
    match = pattern.search(item)
    year, profit = match.group(1), match.group(2).replace(" ", "").replace(",", ".")
    data.append((year, profit))

# Print the extracted data
for year, profit in data:
    print(f"Year: {year}, Profit: {profit}")


additional_detail=[]
people_detail=[]
fillings_detail=[]
contacts_detail=[]
previous_names_detail=[]
addresses_detail=[]

mean_of_exsist_value=''
concessions_data=''
foreign_data=''
bracket_value=''
main_name=''
add_text=''
email_text=''
trade_block_text=''
name_block_text=''
employee_block_text=''
capital_block_text=''
administrator_block_text=''
owner_block_text=''
other_block_text=''
origin_of_capital_value=''
legal_matter_value=''
parent_description_value=''
company_description_value=''
ownership_type_value=''


def extract_info(soup, search_text):
    info_text = None
    texts = soup.find_all(text=lambda text: search_text in text)
    if texts:
        for text in texts:
            card = text.find_parent(class_="card")
            if card:
                card_block = card.find('div', class_='card-block')
                info_text = card_block.text.strip()
                break  # Exit the loop after finding the first match
    return info_text




# title_divs = soup.find_all('div', class_='title-divider')

# own_link="https://opencorporates.al"
# # Iterate through the div elements and check for the desired text
# for title_div in title_divs:
#     text = title_div.text.strip()  # Remove leading and trailing spaces
#     if "Zotëruese/Shoqëri Mëmë për" in text:
#         a_tag = title_div.find_next('a')
#         if a_tag:
#             title = a_tag.string  # Use .string to access the text
#             url = a_tag['href']
#             additional_detail.append({
#                 'title':title,
#                 'profile_link':f"{own_link}{url}"
#             })



for partner_div in soup.find_all('div', class_='title-divider', id='partners'):

    if "Zotërues të Shoqërisë!" in partner_div.get_text():
        type_text = 'owner'
    elif "ish Zotërues të shoqërisë" in partner_div.get_text():
        type_text = 'former_owner'


    else:
        continue

    ul_element = partner_div.find_next('ul', class_='list-group')
    if ul_element:
        items = ul_element.find_all('li', class_='list-group-item')
    else:
        items = []

    extracted_data_for_div = []

    for item in items:
        link = item.find('a')
        title = ' '.join(link.get_text(strip=True).strip().split())
        url = link['href']

        description = item.find_next('div', class_='card-block')
        description_text = description.get_text(strip=True) if description else None

        if not any(data["title"] == title for data in extracted_data_for_div):
            extracted_data_for_div.append({
                "title": title.replace("\n", ""),
                "url": url,
                "description": description_text,
            })

    for data in extracted_data_for_div:
        people_detail.append({
            'designation': type_text,
            'name': data["title"],
            'profile_link': data["url"],
            'description': data["description"],
        })

# Print the final people_detail list

span_element = soup.find_all("p")
for span in span_element:
    if "Seli/Zyra Qendrore:" in span.get_text():
        head_span=span.text.replace("Seli/Zyra Qendrore:"," ").replace("\n","")

addresses_detail.append({
    "type": "headquarters",
    "address": head_span


})

addresses_elements = soup.find_all('p')
for addresses_element in addresses_elements:
    if "Adresa:" in addresses_element.get_text():
        br_elements = addresses_element.find_all('br')        
        address_parts = []

        for br in br_elements:
            next_element = br.find_next('br')
            if next_element:
                text = br.find_next('br').previous_sibling.strip()
                address_parts.append(text)

        add_text = " ".join(address_parts)

addresses_detail.append({
      'type': 'general_address',
      'address': add_text

})

email_list_div = soup.find('div', id='emailList')
if email_list_div:
    email_child_div = email_list_div.find('div', class_='card-block')
    if email_child_div:
        email_text = email_child_div.text.strip()

contacts_detail.append({
      'type': 'email',
      'value': email_text

})


tel_list_div = soup.find('div', id='telList')
if tel_list_div:
    tele_following_sibling_divs = tel_list_div.find_next('div')
    tele_text=tele_following_sibling_divs.text


contacts_detail.append({
      'type': 'telephone',
      'value': tele_text

})

h2_elements = soup.find_all('h2', class_='title-divider')
if h2_elements:
    for h2_element in h2_elements:
        span_element = h2_element.find('span')
        main_name=span_element.text


previous_h2_elements = soup.find_all('h2', class_='title-divider')
for h2_element in previous_h2_elements:
    span_element = h2_element.find('span')
    if span_element:
        span_text = span_element.get_text()
        bracket_data = re.search(r'\(([^)]+)\)', span_text)
        if bracket_data:
            bracket_value= bracket_data.group(1)

previous_names_detail.append({
    'name':bracket_value

})


concessions  = soup.find('th', text='Konçesione dhe PPP:')
if concessions:
    concessions_td_element = concessions.find_next_sibling('td')
    if concessions_td_element:
        concessions_data = concessions_td_element.get_text()
foreign_company = soup.find('th', text='Shoqëri e huaj për këtë subjekt:')
if foreign_company:
    foreign_td_element = foreign_company.find_next_sibling('td')
    if foreign_td_element:
        foreign_data = foreign_td_element.get_text(strip=True)  # Use strip to remove leading/trailing whitespace

nipt = soup.find('th', text='NIPT:').find_next('td')
if nipt:
    nipt_value=nipt.text


object_value = soup.find('th', text='Objekti i Veprimtarisë:').find_next('td')
if object_value:
    object_value_text=object_value.text

aliases = soup.find('th', text='Emërtime të tjera Tregtare:').find_next('td')
if aliases:
    aliases_value=aliases.text

type = soup.find('th', text='Forma ligjore:').find_next('td')
if type:
    type_value=type.text


establishment_date = soup.find('th', text='Viti i Themelimit:').find_next('td')
if establishment_date:
    establishment_date_value=establishment_date.text


jurisdiction = soup.find('th', text='Rrethi:').find_next('td')
if jurisdiction:
    jurisdiction_value=jurisdiction.text


country = soup.find('th', text='Shteti ku vepron:').find_next('td')
if country:
    country_value=country.text


administrator_th_element = soup.find('th', text='Administrator: ')
if administrator_th_element:
    administrator_td_element = administrator_th_element.find_next('td')
    administrator_content = administrator_td_element.get_text().strip()

num_administrators = soup.find('th', text='Nr. i administratorëve:').find_next('td')
if num_administrators:
    num_administrators_value=num_administrators.text

gender = soup.find('th', text='Femër/Mashkull:').find_next('td')
if gender:
    gender_value=gender.text


people_detail.append({
    'designation': 'administrator',
    'name':administrator_content,
    'administrators':num_administrators_value,
    'administrator_gender':gender_value
})


parent_description = soup.find('th', text='Shoqëri Mëmë / Zotërues për këtë Subjekt:')

if parent_description:
    td_element = parent_description.find_next('td')
    if td_element:
        parent_description_value = td_element.text


# company_description = soup.find('th', text='Shoqëri e Kontrolluar nga ky Subjekt:')
# if company_description:
#     td_element = company_description.find_next('td')
#     if td_element:
#         company_description_value = td_element.text

ownership_type = soup.find('th', text='Lloji i pronësisë:')
if ownership_type:
    td_element = ownership_type.find_next('td')
    if td_element:
        ownership_type_value = td_element.text


additional_detail.append({
    'type':'ownership_details',
    'data':[
        {
            'description':parent_description_value,
            'ownership_type':ownership_type_value,

        }
    ]

})


# Extract information
capital_block_text = extract_info(soup, "Kapitali Themeltar(Lekë)")
administrator_block_text = extract_info(soup, "Administrator")
trade_block_text = extract_info(soup, "Emri Tregtar")
name_block_text = extract_info(soup, "Emri i Subjektit")
owner_block_text = extract_info(soup, "Zotërues")
employee_block_text = extract_info(soup, "Antar Bordi")
other_block_text = extract_info(soup, "Ndryshime të Tjera")

# Create the additional_detail dictionary
additional_detail = []
if (capital_block_text or administrator_block_text or trade_block_text or
        name_block_text or owner_block_text or employee_block_text or other_block_text):
    additional_detail.append({
        'type': 'amendments',
        'data': [
            {
                'capital_info': capital_block_text,
                'administrator_info': administrator_block_text,
                'previous_names_info': trade_block_text,
                'name_details': name_block_text,
                'owner_info': owner_block_text,
                'employee_details': employee_block_text,
                'misc_changes': other_block_text,
            }
        ]
    })


origin_of_capital = soup.find('th', text='Origjina e Kapitalit:')
if origin_of_capital:
    td_element = origin_of_capital.find_next('td')
    if td_element:
        origin_of_capital_value = td_element.text


share_capital = soup.find('th', text='Kapitali Themeltar(Lekë):').find_next('td')
if share_capital:
    share_capital_value=share_capital.text


shares = soup.find('th', text='Numri i pjesëve:').find_next('td')
if shares:
    shares_value=shares.text


additional_detail.append({
    'type': 'capital_details',
    'data': [
        {
        'origin_of_capital': origin_of_capital_value,
        'share_capital': share_capital_value,
        'shares': shares_value
    }

    ]
})


legal_matter = soup.find('th', text='Çështje Ligjore:')

if legal_matter:
    td_element = legal_matter.find_next('td')
    if td_element:
        legal_matter_value = td_element.text


board_member = soup.find('th', text='Anëtarë Bordi:')
board_member_value = None

if board_member:
    td_element = board_member.find_next('td')
    if td_element:
        board_member_value = td_element.text

if board_member_value:
    people_detail.append({
        "designation": "board_member",
        'name': board_member_value
    })




status = soup.find('th', text='Statusi:').find_next('td')
if status:
    status_value=status.text




license = soup.find('th', text='Leje/Licensa:').find_next('td')
if license:
    license_value=license.text


mean_of_exsist = soup.find('th', text='Mjete të ushtrimit të aktivitetit:')
if mean_of_exsist:
    td_element = mean_of_exsist.find_next('td')
    if td_element:
        mean_of_exsist_value = td_element.text



filling_th_element = soup.find('th', string='Akte. Tjetërsim Kapitali:')
base_url="https://opencorporates.al"
if filling_th_element:
    filling_td_element = filling_th_element.find_next('td')
    if filling_td_element:
        anchor_elements = filling_td_element.find_all('a')
        for anchor in anchor_elements:
            title = anchor.get_text().strip()
            link = f"{base_url}{anchor['href']}"

            # Extract the date using a regular expression
            date_match = re.search(r'\d{2}\.\d{2}.\d{4}', anchor.parent.get_text())
            date = date_match.group() if date_match else ""

            fillings_detail.append({
                'title':title,
                'file_url':link,
                'date':date
            })


    OBJ={
        'name':main_name,
        'previous_names_detail':previous_names_detail,
        'registration_number':nipt_value,
        'value':object_value_text,
        'status':status_value,
        'description':concessions_data,
        'foreign_company':foreign_data,
        'means_of_exercising_business_activity':mean_of_exsist_value,
        'licenses':license_value,
        'legal_matters':legal_matter_value,
        'aliases':aliases_value,
        'type':type_value,
        'establishment_date':establishment_date_value,
        'circle':jurisdiction_value,
        'country':country_value,
        'additional_detail':additional_detail,
        'fillings_detail':fillings_detail,
        'contacts_detail':contacts_detail,
        'addresses_detail':addresses_detail,
        'people_detail':people_detail

    }
    OBJ =  Albania.prepare_data_object(OBJ)
    ENTITY_ID = Albania.generate_entity_id(company_name=OBJ['name'],reg_number=OBJ['registration_number'])
    NAME = OBJ['name'].replace("%","%%")
    BIRTH_INCORPORATION_DATE = ""
    ROW = Albania.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
    Albania.insert_record(ROW)
