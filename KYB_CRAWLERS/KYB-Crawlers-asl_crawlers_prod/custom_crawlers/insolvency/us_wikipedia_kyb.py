"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
import datetime
import json
import os
import traceback
import requests
import re
from bs4 import BeautifulSoup
import shortuuid
import psycopg2
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import datefinder
import threading
from helpers.crawlers_helper_func import CrawlersFunctions

# Load the environment variables
load_dotenv()
'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(host=os.getenv('WIKI_DB_HOST'), port=os.getenv('WIKI_DB_PORT'),
                        user=os.getenv('WIKI_DB_USERNAME'), password=os.getenv('WIKI_DB_PASSWORD'), dbname=os.getenv('WIKI_DB_NAME'))
cursor = conn.cursor()

get_records = """SELECT category_url, category, entity_type, description FROM category_description_kyb;"""

cursor.execute(get_records)
records = cursor.fetchall()

# Define a regular expression pattern for matching dates in a string
date_pattern = r'\d{4}-\d{2}-\d{2}'

# Create a requests session for making HTTP requests to Wikipedia
session = requests.Session()

# Initialize lists to keep track of visited links and subcategories
visited_links = list()
visited_subcategories = list()


def find_years(str):
    matches = re.findall(r'(\d{4})', str)
    years = set(i[-4:] for i in matches)
    return list(years)


def scrape_pagination_pages(url):
    '''
    This function scrapes all the pages in the pagination section of a given URL and returns a list of all the pages as BeautifulSoup objects. If there are multiple pages, the function recursively calls itself with the URL of the next page and appends the new pages to the list. If an exception occurs during the scraping process, the traceback is printed to the console.
    '''
    pages = list()
    try:
        page_response = session.get(url)
        page_soup = BeautifulSoup(
            page_response.content, 'html.parser')
        pages += page_soup.find_all(
            'div', {'class': 'mw-category-generated'})[0].find_all('li')

        next_page_link = page_soup.find(
            'div', class_='mw-category-generated')
        if next_page_link is not None:
            next_page_link = next_page_link.find('a', string='next page')

            if next_page_link is not None:
                next_page_url = "https://en.wikipedia.org" + \
                    next_page_link['href']
            else:
                next_page_url = None
        else:
            next_page_url = None

        if next_page_url is not None:
            pages += scrape_pagination_pages(next_page_url)
            print('paginated_pages', len(pages))

        return pages
    except Exception as e:
        tb_str = traceback.format_exc()
        print(tb_str, 'Traceback (most recent call last):')


def scrape_main_category(url):
    '''
    This function scrapes all the pages in the main category and its subcategories of a given URL and returns a list of all the pages as BeautifulSoup objects. If there are subcategories, the function recursively calls itself with the URL of each subcategory and appends the new pages to the list. If there are multiple pages in any of the subcategories, the function calls another helper function, scrape_pagination_pages(), to scrape all the pages in the pagination section and append them to the list. If an exception occurs during the scraping process, the traceback is printed to the console. The global variable visited_subcategories is used to keep track of the subcategories already visited to avoid revisiting them.
    '''

    print('get url', url)
    global visited_subcategories

    pages = list()
    if url in visited_subcategories:
        return []
    try:
        visited_subcategories.append(url)
        subcategory_response = session.get(url)
        subcategory_soup = BeautifulSoup(
            subcategory_response.content, 'html.parser')
        categories = subcategory_soup.find_all(
            'div', {'class': 'CategoryTreeItem'})
        pages += subcategory_soup.find_all(
            'div', {'class': 'mw-category-generated'})[0].find_all('li')

        next_page_link = subcategory_soup.find(
            'div', class_='mw-category-generated')
        if next_page_link is not None:
            next_page_link = next_page_link.find('a', string='next page')

            if next_page_link is not None:
                next_page_url = "https://en.wikipedia.org" + \
                    next_page_link['href']

            else:
                next_page_url = None
        else:
            next_page_url = None

        if next_page_url is not None:
            pages += scrape_pagination_pages(next_page_url)

            print('final paginated_pages', len(pages))

        if categories is not None:
            for subcategory in categories:
                if 'https://en.wikipedia.org' + subcategory.find('a').get('href') not in visited_subcategories:
                    pages += scrape_main_category('https://en.wikipedia.org' +
                                                  subcategory.find('a').get('href'))
        return pages
    except Exception as e:
        tb_str = traceback.format_exc()
        print(tb_str, 'Traceback (most recent call last):')


def scrape_page(page_link):
    '''
    This function scrapes the infobox table from a given Wikipedia page link using BeautifulSoup and returns it as a BeautifulSoup object. The infobox table contains a summary of important information related to the subject of the page, such as a person, a place, an event, etc.
    '''
    try:
        page_response = session.get(page_link)
        page_soup = BeautifulSoup(page_response.content, 'html.parser')
        return page_soup.find('table', {'class': 'infobox'})
    except Exception as e:
        tb_str = traceback.format_exc()
        print(tb_str, 'Traceback (most recent call last):')
        scrape_page(page_link)
        pass


def extract_data(table, page_link, record):
    '''
    This function extracts data from a Wikipedia page by scraping the infobox table and other relevant information from the page.
    It takes a table, a page link, and a record as input parameters.
    If the table is not None, it loops through each row in the table and extracts the key-value pairs, checking for special cases like dates and links to other pages.
    If the key is 'Children', 'Spouses', 'Partner(s)', or 'Siblings', it extracts the information about the partner from the linked page by calling the scrape_page() function and then recursively calling the extract_data() function to extract the data from that page as well.
    If the table contains an image, it extracts the URL of the image as well.
    If there is no table on the page, it extracts the name, description, and page URL from the page.
    '''
    try:
        page_response = session.get(page_link)
        page_soup = BeautifulSoup(page_response.content, 'html.parser')
        name = page_soup.find('h1').text
        if name is None:
            name = page_link.split('/')[-1].replace('_', ' ')
        data = {'name': name}
        if table is not None:
            for row in table.find_all('tr'):
                cells = row.find_all(['th', 'td'])
                if len(cells) == 2:
                    text = cells[0].get_text().strip().lower()
                    replace = text.replace(" ", "_")
                    key = replace.replace(" ", "_")

                    value = cells[1].get_text().strip()

                    # if key == 'died' or key == 'born' or key == 'died:' or key == 'born:' or key == 'date':
                    if key in ['died', 'born', 'died:', 'born:', 'date', 'founded']:

                        matches = datefinder.find_dates(value)
                        para = list(set(date for date in matches))
                        output = ''

                        if not para:
                            para = find_years(value)
                            output = ' - '.join(para)
                        else:
                            output = ' - '.join(dt.strftime('%Y-%m-%d %H:%M:%S')
                                                for dt in para)
                        value = output

                    data[key] = value

                    try:
                        # Check if the key is 'Children', 'Spouses', 'Partner(s)', or 'Siblings'
                        if key in ['children', 'spouses', 'father', 'mother', 'siblings', 'partner(s)', 'spouse', 'wife', 'sons', 'Sons',  'husband', 'Husband', 'daughters', 'grandsons', 'Grandsons', 'granddaughters', 'Granddaughters', 'sisters', 'stepsons', 'Stepsons', 'other_relatives', 'Other relatives', 'First cousins', 'first_cousins', 'Nephews', 'nephews', 'Half-brother', 'half-brothers', 'Grandfathers', 'grandfathers', 'Grandmothers', 'grandmothers']:
                            visited_links.append(page_link)
                            link = cells[1].find('a')
                            if link and "#" not in link['href']:
                                next_link = 'https://en.wikipedia.org' + \
                                    link['href']
                                if next_link not in visited_links:
                                    partner_table = scrape_page(next_link)
                                    partner_data = extract_data(
                                        partner_table, next_link, record)
                                    if partner_data:
                                        insert_data(record, partner_data)
                                        data.update(
                                            {key: [{"label": partner_data['name'], "entity_id": "wiki-" + shortuuid.uuid(next_link)}]})
                    except Exception as e:
                        tb_str = traceback.format_exc()
                        print(tb_str, 'Traceback (most recent call last):')

            if table.find('img'):
                image_url = table.find('img')['src']
                data['image_url'] = 'https:' + image_url

            data['page_url'] = page_link

        else:
            if "Category:" in page_link:
                return None
            page_response = session.get(page_link)
            page_soup = BeautifulSoup(page_response.content, 'html.parser')
            name = page_soup.find('h1').text

            # Find all 'p' tags on the page
            p_tags = page_soup.find_all('p')

            # Check if the first 'p' tag is empty
            if len(p_tags) > 0:
                Description = p_tags[0].text.strip()
            else:
                Description = ''

            data['description'] = Description

            # Add the information to the data dictionary
            data['name'] = name
            data['description'] = Description
            data['page_url'] = page_link
        return data

    except AttributeError:
        print(f"No table found on page {page_link}")
        extract_data(table, page_link, record)
        pass
        return None


def scrape_url(record):
    '''
    This function scrapes the given category URL and extracts information from its main pages and subcategories. It calls
    scrape_main_category to extract links to main pages and scrape_page and extract_data to extract
    information from those pages. The extracted data is inserted into the database using insert_data. If an
    error occurs, it is caught and the traceback is printed.
    '''
    try:
        main_pages = scrape_main_category(record[0])

        print('Total main pages found --------------------------------',
              len(main_pages))

        for page in main_pages:
            page_link = 'https://en.wikipedia.org' + page.find('a').get('href')
            table = scrape_page(page_link)

            data = extract_data(table, page_link, record)

            if data:
                insert_data(record, data)

    except Exception as e:
        tb_str = traceback.format_exc()
        print(tb_str, 'Traceback (most recent call last):')
        scrape_url(record)
        pass
 

def get_listed_object(data):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
   
    @param record
    @return dict
    '''
    # print(data)
    # input()

    # preparing meta_detail dictionary object

    meta_detail = dict()
    try:
      meta_detail['products'] = data['products'].replace("'","''")
    except:
        meta_detail['products'] = ""
    try:
      meta_detail['revenue'] = data['revenue'].replace("'","''")
    except:
        meta_detail['revenue'] = ""
    try:
        meta_detail['description'] = data['description'].replace("'","''")
    except:
        meta_detail['description'] = ""
    try:
      meta_detail['subsidiaries'] = data['Subsidiaries'].replace("'","''")
    except:
        meta_detail['subsidiaries'] = ""
    try:
        meta_detail['industry_type'] = data['Industry'].replace("'","''")
    except:
        meta_detail['industry_type'] = ""
    try:
        meta_detail['operating_income'] = data['operating_income'].replace("'","''")
    except:
        meta_detail['operating_income'] = ""
    try:
        meta_detail['net_income'] = data['net_income'].replace("'","''")
    except:
        meta_detail['net_income'] = ""
    try:
        meta_detail['assets'] = data['total_assets'].replace("'","''")
    except:
        meta_detail['assets'] = "" 
    try:
        meta_detail['number_of_employees'] = data['number_of_employees'].replace("'","''")
    except:
        meta_detail['number_of_employees'] = "" 
    try:    
        meta_detail['services'] = data['services'].replace("'","''")
    except:
        meta_detail['services'] = ""
    try:
        meta_detail['Branches'] = data['number_of_locations'].replace("'","''")
    except:
        meta_detail['Branches'] = ""
    try:
        meta_detail['language'] = data['language'].replace("'","''")
    except:
        meta_detail['language'] = ""
    
    try:
        meta_detail['successor'] = data['successor'].replace("'","''")
    except:
        meta_detail['successor'] = ""
    try:
        meta_detail['parent_company'] = data['parent_company'].replace("'","''")
    except:
        meta_detail['parent_company'] = ""
    address = dict()
    address['type'] = "address_details"
    address['description'] = ""
    address['address'] = data['address'].replace("'","''") if 'address' in data else ""
    ad_meta_detail = {
                "country":data['country'].replace("'","''") if 'country' in data else "",
                "area_served":data['area_served'].replace("'","''") if 'area_served' in data else "",
                 "number_of_locations":data['number_of_locations'].replace("'","''") if 'number_of_locations' in data else "",
                 "area_served":data['area_served'].replace("'","''") if 'area_served' in data else "",
                 "location":data['location'].replace("'","''") if 'location' in data else "",  
                 "coordinates":data['coordinates'].replace("'","''") if 'coordinates' in data else "", 
                    }
    address['meta_detail'] = ad_meta_detail

    incorporation_place_and_date  = dict()
    incorporation_place_and_date['type'] = "incorporation_place_and_date_details"
    incorporation_place_and_date['description'] = ""
    incorporation_place_and_date['founded'] = data['founded'].replace("'","''") if 'founded' in data else ""
    incorporation_meta_detail = {
                "commenced_operations":data['commenced_operations'].replace("'","''") if 'commenced_operations' in data else "",
                "opened":data['opened'].replace("'","''") if 'opened' in data else "",
                    }
    incorporation_place_and_date['meta_detail'] = incorporation_meta_detail


    dissolution_date  = dict()
    dissolution_date['type'] = "dissolution_date_details"
    dissolution_date['description'] = ""
    dissolution_date['defunct'] = data['defunct'].replace("'","''") if 'defunct' in data else ""
    dd_meta_detail = {
                "ceased_operations":data['ceased_operations'].replace("'","''") if 'ceased_operations' in data else "",
                "ceased":data['ceased'].replace("'","''") if 'ceased' in data else "",
                "closed":data['closed'].replace("'","''") if 'closed' in data else "",
                    }
    dissolution_date['meta_detail'] = dd_meta_detail


    directors_officers  = dict()
    directors_officers['type'] = "directors_officers_details"
    directors_officers['description'] = ""
    directors_officers['founder'] = data['founder'].replace("'","''") if 'founder' in data else ""
    do_meta_detail = {
                "key_people":data['key_people'].replace("'","''") if 'key_people' in data else "",
                "owner":data['owner'].replace("'","''") if 'owner' in data else "",
                "owner(s)":data['owner(s)'].replace("'","''") if 'owner(s)' in data else "",
                    }
    dissolution_date['meta_detail'] = do_meta_detail

    aliases  = dict()
    aliases['type'] = "aliases"
    aliases['description'] = ""
    aliases['traded_as'] = data['traded_as'].replace("'","''") if 'traded_as' in data else ""
    alias_meta_detail = {
                "former_names":data['former_names'].replace("'","''") if 'former_names' in data else "",
               
                    }
    dissolution_date['meta_detail'] = alias_meta_detail




    website= dict()
    website['type'] = "Website"
    website['description'] = ""
    website['website'] = data['website'].replace("'","''") if 'website' in data else ""
    website_meta_detail = {
                "official_website":data['official_website'].replace("'","''") if 'official_website' in data else "",
                "url":data['url'].replace("'","''") if 'url' in data else "",
                
                    }
    website['meta_detail'] = website_meta_detail
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": data['name'].replace("'","''"),
        "status": data['fate'].replace("'","''") if 'fate' in data else "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": data['type'].replace("'","''") if 'type' in data else "",
        "crawler_name": "crawlers.custom_crawlers.insolvency.us_wikipedia_kyb",
        "country_name": "United States",
        "company_fetched_data_status": "",
        "address_details":[address],
        "dissolution_date_details":[dissolution_date],
        "dissolution_date":[dissolution_date],
        "website_url":[website],
        "incorporation_place_and_date_detalis":[incorporation_place_and_date],
        "aliases":[aliases],
        "directors_officers":[directors_officers],
        "meta_detail": meta_detail
    }
    
    return data_obj

def insert_data(record, data):
    '''
    This function inserts data into a PostgreSQL database table called "wiki_pages_data".
    The function takes in two arguments: a record and data to be inserted into the database.
    The function uses a formatted SQL query to insert the data into the table, with the 'ON CONFLICT' clause to update the row if the 'wikidata_id' already exists in the table.
    '''

    try:
        country = "United States"
        entity_type = "Company/ Organisation/ Person" 
        category = "Wikipedia Bankruptcy"
        name_ = "Wikipedia"
        description = "This data contains information about bankrupt companies/ persons and It provides a comprehensive list of companies that have gone bankrupt, with links to their individual articles that contain detailed information about each case. "
        source_type = name_+"-"+"HTML"
        url = record[0]
        data  = get_listed_object(data)
        
        source_details = {"name":name_,"source_url":url,"description":description}
        updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data, source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}', source = '{9}',updated_at='{10}'""".format(data['name'],data['name'].replace("'","''"),json.dumps([]),json.dumps([category.title()]),json.dumps([country.title()]),entity_type.title(),json.dumps([]),json.dumps(data),json.dumps(source_details), source_type,updated_at,updated_at,'en','true')
        
        crawlers_functions.db_connection(query)    
        # cursor.execute(query)
        # conn.commit()
        print("done")
    except Exception as e:
        tb = traceback.format_exc()
        print("Error: ", e, tb)


if __name__ == '__main__':
    '''
    This code block is the main entry point of the program.
    It creates a ThreadPoolExecutor with a number of worker threads equal to the number of records in the 'records' list.
    The 'scrape_url' function is then mapped to the executor to be executed concurrently for each record in the list.
    '''

    with ThreadPoolExecutor(max_workers=len(records)) as executor:
        executor.map(scrape_url, records)
