import psycopg2
import requests
from bs4 import BeautifulSoup



def extract_data(soup1):
    table_info = soup1.find('table', id='tblAttorney').find('tbody')
    links = table_info.find_all('tr')
    base_url = 'https://apps.calbar.ca.gov/'
    
    for link in links:
        url = f"{base_url}{link.find('a')['href']}"
        response2 = requests.get(url)
        soup = BeautifulSoup(response2.content, "html.parser")
        data = {}

        # Find the div element
        div_element = soup.find('div', style='margin-top:1em;')

        # Extract name and number
        try:
            h3_element = div_element.find('h3')
            name_with_number = h3_element.find('b').get_text(strip=True)
            name, _ = name_with_number.split('#', 1)
            data['Name'] = name.strip()
        except:
            pass

        try:
            website = soup.find('a', id='websiteLink').get_text(strip=True)
            data['website'] = website
        except:
            data['website'] = 'None'

        try:
            email = soup.find('span', id='e0')['href'].replace('mailto:','')
            data['email'] = email
        except:
            data['email'] = ''

        try:
            license = div_element.find('p').find('b').find('span').text
            data['license'] = license
        except:
            try:
                license = div_element.find('p').find('b').get_text(strip=True).replace('License Status:', '').strip()
                data['license'] = license
            except:
                data['license'] = 'None'


        # Extract phone and fax
        phone_paragraph = soup.find('p', string=lambda text: text and 'Phone' in text)
        try:
            phone = phone_paragraph.get_text(strip=True).split(':')[1].split('|')[0].strip()
            data['Phone'] = phone
        except:
                data['Phone'] = "Phone number not found."

        try:
            fax = phone_paragraph.get_text(strip=True).split(':')[2].strip()
            data['Fax'] = fax
        except:
            data['Fax'] = "Fax number not found."          

        data_insertion(data)


def data_insertion(data):
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="airflow",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # Check if the name already exists in the database
        cursor.execute("SELECT name FROM info WHERE name = %s", (data['Name'],))
        existing_name = cursor.fetchone()

        if existing_name:
            print("Data already exists for:", existing_name[0])
        else:
            # Insert the data into the database
            cursor.execute("""
                INSERT INTO info(name, license, email, website, phone, fax)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data['Name'], data['license'], data['email'], data['website'], data['Phone'], data['Fax']))
            print("Data inserted successfully")
            conn.commit()
    except Exception as e:
        print("Error inserting data:", str(e))
        conn.rollback()
    finally:
        cursor.close()
        conn.close()




def main():
    for i in range(ord('y'), ord('z') + 1):
        letter = chr(i)
        url=f"https://apps.calbar.ca.gov/attorney/LicenseeSearch/QuickSearch?FreeText={letter}&SoundsLike=false"
        print(f"data extracted letter {letter}")
        response = requests.get(url)
        soup1 = BeautifulSoup(response.content, "html.parser")
        extract_data(soup1)


if __name__ == "__main__":
    main()