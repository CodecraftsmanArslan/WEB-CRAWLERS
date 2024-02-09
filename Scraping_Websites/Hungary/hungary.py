import requests
from bs4 import BeautifulSoup
import pandas as pd

all_data = pd.DataFrame()

for i in range(1, 137):
    url = f"https://ouny.magyarugyvedikamara.hu/licoms/common/service/requestparser?name=pubsearcher&action=search&type=kamarai_jogtanacsos&status=aktiv&p={i}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    def get_data(soup):
        individuals = soup.find_all('div', class_='media-body')
        data = []
        for person in individuals:
            person_data = {}
            form_groups = person.find_all('div', class_='form-group')
            for form_group in form_groups:
                label = form_group.find('label', class_='col-sm-4 control-label').text.strip()
                value = form_group.find('p', class_='form-control-static').text.strip()
                person_data[label] = value

            data.append(person_data)
        return data


    result_df = get_data(soup)
    print("Data Extracted")

    
    df = pd.DataFrame(result_df)
    
    all_data = all_data.append(df, ignore_index=True)

all_data.to_excel("hungary.xlsx")
print("ALL DATA IS EXTRACTED")
















