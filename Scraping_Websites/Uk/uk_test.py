import requests,sys
from bs4 import BeautifulSoup
import pandas as pd


def extract_name(soup2):
    header = soup2.find('h1')
    if header:
        company_name = header.text.strip()
        return company_name
    return None

def extract_address(info_elements):
    address_element = info_elements.find('dd', class_='address')
    if address_element:
        address_text = address_element.get_text(strip=True)
        cleaned_address = address_text.replace("Head office |Address", "")
        return cleaned_address
    return None

def extract_info(info_elements, label):
    info = info_elements.find('dt', text=label)
    if info:
        value = info.find_next_sibling("dd")
        if value:
            return value.get_text(strip=True)
    return None

def append_data(data, info_elements,soup2):
    company_name=extract_name(soup2)
    trading_names = extract_info(info_elements, 'Trading Names')
    type_ = extract_info(info_elements, 'Type')
    sra_id = extract_info(info_elements, 'SRA ID')
    email = extract_info(info_elements, 'Email')
    web = extract_info(info_elements, 'Web')
    telephone = extract_info(info_elements, 'Telephone')
    address = extract_address(info_elements)

    data.append({
        'name':company_name,
        'Trading Names': trading_names,
        'Type': type_,
        'SRA ID': sra_id,
        'Email': email,
        'Web': web,
        'Address': address,
        'telephone': telephone

    })

def create_dataframe(data):
    df = pd.DataFrame(data)
    return df

def get_data(soup1):
    data = []
    details = soup1.find_all('div', class_="heading")
    for detail in details:
        info_url = f"{base_url}{detail.find('a')['href']}"
        response2 = requests.get(info_url, headers=headers)
        soup2 = BeautifulSoup(response2.content, "html.parser")
        info_elements = soup2.find('div', class_="details-outer")
        
        append_data(data, info_elements,soup2)
    
    df = create_dataframe(data)
    return df

# Initialize an empty list to store data
all_data = []

url = "https://solicitors.lawsociety.org.uk/"
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}
response = requests.request("GET", url, headers=headers)

base_url = "https://solicitors.lawsociety.org.uk"

arguments = sys.argv
start_num = int(arguments[1]) if len(arguments)>1 else 0
value_arg = arguments[2] if len(arguments) > 2 else None


soup = BeautifulSoup(response.content, "html.parser")
options=soup.find_all("optgroup")
for optgroup in options:
    for option in optgroup.find_all("option"):
        for i in range(start_num, 31):
            value = value_arg if value_arg is not None else option['value']
            person_url=f"https://solicitors.lawsociety.org.uk/search/results?Pro=False&UmbrellaLegalIssue={value}&Page={i}"
            start_num=1
            print(f"DATA EXTRACTED-{value} & Page={i}")
            person_response=requests.get(person_url,headers=headers)
            soup1 = BeautifulSoup(person_response.content, "html.parser")
                # Get data for current page and append to all_data
            data_frame = get_data(soup1)
            print("DATA SAVED SUCCESSFULLY")
            all_data.append(data_frame)

            combined_df = pd.concat(all_data, ignore_index=True)

            # Save the combined DataFrame to a single CSV file
            combined_df.to_excel("DATA1.xlsx")
            print("CSV file saved successfully.")


# LIUFAM
# get the result from there












