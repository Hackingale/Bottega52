from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import threading
from urllib.parse import urljoin

import pandas as pd
import requests

import functions as f
from bs4 import BeautifulSoup
from src.functions import company_name_cleaning
from src.functions import domain_cleaning

import re

# Global variables
extracted_values = dict()  # Dictionary to store the extracted text from the web pages
# MAKE SURE ALL DEBUG COMMENTS ARE DEACTIVATED ONCE RUNNING FINAL VERSION


def counter(val):
    val = val+1
    return val


'''
This functon takes a URL and returns a list of all the links on the first level of the website


def get_links_level1(url):
    # Send a GET request to the URL
    try:
        response = requests.get(url)
    except Exception as e:
        print("Error: Failed to retrieve links from the website")
        return None
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all anchor tags (links) in the HTML
        links = soup.find_all('a')

        # Extract the href attribute from each anchor tag
        all_links = []
        for link in links:
            href = link.get('href')
            if href:
                # Join relative URLs with the base URL
                full_url = urljoin(url, href)
                all_links.append(full_url)
        return all_links if len(all_links) > 0 else None
    else:
        print("Failed to fetch page:", response.status_code)
        return None
'''


'''
Function to scrape the web page and extract the text content from the HTML
taking advantage of Clearbit to get possible domains of the company

:parameter extracted_values: dictionary to store the extracted text from the web pages
:parameter company_name: name of the company to scrape

:return 0 if the scraping was successful, 1 otherwise
'''


def clear_scrape(company_name):

    url = 'https://autocomplete.clearbit.com/v1/companies/suggest?query={' + company_name + '}'
    try:
        # Send a GET request to the ClearBit API with a timeout of 5 seconds
        response = requests.get(url, timeout=5)
    except Exception as e:
        print("Error: Failed to connect to the ClearBit API")
        return 1

    if response.status_code == 200:
        data = response.json()
        domains = [entry['domain'] for entry in data if 'domain' in entry]
    else:
        print("Error: Failed to retrieve data from the API")
        domains = []

    if len(domains) == 0:
        return 1
    else:
        if len(domains) > 5:
            # take the first five domains
            domains = domains[:5]
        for domain in domains:
            # here the function should iter over the domains and for each domain scrape the text
            # and scrape the text of the links in the first level of the website
            url = 'https://www.' + domain  # Replace example.com with your base URL

            # Extract the text content from the HTML
            extracted = ''
            ret = ''

            extracted = f.summarize_text(url, 'english', 12)
            if extracted is not None and len(extracted) > 5000:
                extracted = extracted[:4999]

            try:
                translation = f.translate_text(extracted, 'en')
            except Exception as e:
                translation = extracted
                try:
                    translation = f.translate_text(translation, 'en')
                except Exception as e:
                    translation = extracted

            ret = translation
            links = None
            '''
            if extracted is not None:
                links = get_links_level1(url)
            if links is not None:
                if len(links) > 40:
                    links = f.specific_random_choice(links, 4)
                else:
                    links = f.random_choice(links, 5)
                for link in links:
                    extracted = f.summarize_text(link, 'english', 3)
                    if extracted is not None and len(extracted) > 5000:
                        extracted = extracted[:4999]
                    translation = f.translate_text(extracted, 'en')
                    if translation is not None:
                        ret += translation
            '''
            if ret is not None:
                extracted_values[company_name] = ret
                # print(ret)
                return 0
        return 1


"""
Function to scrape the web page and extract the text content from the HTML

:parameter company_url: URL of the company to scrape
:parameter extracted_values: dictionary to store the extracted text from the web pages
:parameter company_name: name of the company to scrape

:return 0 if the scraping was successful, 1 otherwise
"""


def unclear_scrape( company_name):

    # try spain first
    url = 'https://www.' + company_name + '.es'  # Replace example.com with your base URL
    extracted = f.summarize_text(url, 'spanish', 15)

    if extracted is None:
        # try italian
        url = 'https://www.' + company_name + '.it'
        extracted = f.summarize_text(url, 'italian', 15)
        if extracted is None:
            # try english
            url = 'https://www.' + company_name + '.com'
            extracted = f.summarize_text(url, 'english', 15)
            if extracted is None:
                extracted_values[company_name] = None
                return 1
            else:
                if len(extracted) > 5000:
                    extracted = extracted[:4999]
                try:
                    translation = f.translate_text(extracted, 'en')
                except Exception as e:
                    translation = extracted
                    try:
                        translation = f.translate_text(translation, 'en')
                    except Exception as e:
                        translation = extracted
                extracted_values[company_name.lower()] = translation
                return 0
        else:
            if len(extracted) > 5000:
                extracted = extracted[:4999]
            try:
                translation = f.translate_text(extracted, 'en')
            except Exception as e:
                translation = extracted
                try:
                    translation = f.translate_text(translation, 'en')
                except Exception as e:
                    translation = extracted
            extracted_values[company_name.lower()] = translation
            return 0
    else:
        if len(extracted) > 5000:
            extracted = extracted[:4999]
        try:
            translation = f.translate_text(extracted, 'en')
        except Exception as e:
            translation = extracted
            try:
                translation = f.translate_text(translation, 'en')
            except Exception as e:
                translation = extracted
        extracted_values[company_name.lower()] = translation
        return 0


"""
Function to start a thread for each section of the DataFrame

:parameter file: Excel file containing the data to scrape
:parameter num: number of sections/threads to create

:return None
"""


def web_scraper(file, num):
    # Read the Excel file
    df = pd.read_excel(file, header=None, usecols=[1, 3], skiprows=[0], names=['Contact E-mail', 'Company / Account'])

    # Determine the number of rows in the file and calculate the number of rows each section should contain
    total_rows = len(df)
    rows_per_section = total_rows // num  # Integer division to evenly distribute rows

    # Split the DataFrame into 10 sections
    sections = []
    for i in range(num):
        start_row = i * rows_per_section
        end_row = start_row + rows_per_section
        if i == 9:  # Last section may have remaining rows
            end_row = total_rows
        section_df = df.iloc[start_row:end_row].reset_index(drop=True)  # Reset index for each section
        sections.append(section_df)

    threads = []

    # Now, sections[0] contains the first DataFrame, sections[1] contains the second DataFrame, and so on.
    for frame in sections:
        # start a thread for each frame that executes function scrape
        thread = threading.Thread(target=scrape, args=(frame,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()


"""
Function to scrape the web page and extract the text content from the HTML

:parameter df: DataFrame containing the data to scrape

:return None"""


def scrape(df):

    for email, company_name in zip(df['Contact E-mail'], df['Company / Account']):

        name = company_name
        # remove everything after the last underscore
        name = name.split('_')
        if len(name) > 1:
            name = name[:-1]

        # take the company and make it lowercase
        for i in range(len(name)):
            name[i] = name[i].lower()

        # join the company name back together
        name = '_'.join(name)

        # remove spaces at the end of the word in case there are any
        name = name.rstrip()
        company_name = name.lower()

        flag = 0

        # IF THE CONTACT HAS A VALID NAME
        if pd.notnull(name) and name != '' and len(name) > 0:  # Check if company name is not null
            flag = 1

        # DOMAIN CLEANING
        # ELSE USE THE CONTACT'S EMAIL
        elif pd.notnull(email) and email != '' and len(email) > 0:
            flag = 2

            # takes only the domain part
            cleaned_domain = domain_cleaning(email)

        if company_name in extracted_values.keys() and flag == 1 or flag == 2 and cleaned_domain in extracted_values.keys():
            continue
        else:
            extracted_values[company_name] = None

        # if the contact has a valid company_name
        if flag == 1:
            if wikipedia_scrape(company_name) == 1:
                if clear_scrape(company_name) == 1:
                    unclear_scrape(company_name)
            print("Scraped: " + company_name)
        elif flag == 2:
            if clear_scrape(cleaned_domain) == 1:
                unclear_scrape(cleaned_domain)
            print("Scraped: " + cleaned_domain)
        else:
            print("Error: Company name and email are both null " + company_name)


def status_code_ok(response, extracted_values, company_name):
    # Parse the HTML content of the web page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the body of the parsed HTML
    body = soup.body

    # Extract only the text from the parsed HTML
    text = ' '.join(line.strip() for line in body.get_text().splitlines() if line.strip())

    # Save the extracted text
    extracted_values[company_name] = text

    # Print the extracted text - DEBUG only
    # print(company_name)


def fetch_wikipedia_page(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.content


def find_all_list_item_links(content_div):
    links = []
    list_items = content_div.find_all('li')
    for li in list_items:
        first_link = li.find('a')
        if first_link and 'href' in first_link.attrs:
            links.append('https://en.wikipedia.org' + first_link['href'])
    return links


def scrape_wikipedia_paragraphs_from_list(links, depth):
    paragraphs = []
    for link in links:
        paragraphs.append(scrape_wikipedia_paragraphs(link, depth))
    return paragraphs


def scrape_wikipedia_paragraphs(url, depth):
    if depth > 2:
        return []
    content = fetch_wikipedia_page(url)
    soup = BeautifulSoup(content, 'html.parser')

    content_div = soup.find('div', class_='mw-content-ltr mw-parser-output')

    is_disambiguation = False

    # Check for the disambiguation notice
    disambig_notice = soup.find('div', id='mw-normal-catlinks')
    if disambig_notice and 'disambiguation' in disambig_notice.text.lower():
        is_disambiguation = True
    else:
        is_disambiguation = False

    paragraphs = []

    for child in content_div.children:
        if child.name == 'p':
            paragraphs.append(child.get_text())
            if is_disambiguation:
                links = find_all_list_item_links(content_div)
                if links:
                    # take first 3 links
                    links = links[:3]
                    return scrape_wikipedia_paragraphs_from_list(links, depth + 1)
        elif child.name and child.name.startswith('h'):
            break

    return paragraphs


def take_longest_paragraph(paragraphs):
    longest = ""
    for paragraph in paragraphs:
        if len(paragraph) > len(longest):
            longest = paragraph
    return longest


def wikipedia_scrape(company_name):
    paragraphs = ''
    try:
        paragraphs = scrape_wikipedia_paragraphs('https://en.wikipedia.org/wiki/' + company_name, 1)
        paragraphs = take_longest_paragraph(paragraphs)
        paragraphs = clean_text(paragraphs)
    except Exception as e:
        paragraphs = None
        return 1
    extracted_values[company_name.lower()] = paragraphs
    return 0

def is_disambiguation_page(url):
    try:
        # Fetch the content of the page
        response = requests.get(url)
        response.raise_for_status()  # Raise an error on a bad status

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for the disambiguation notice
        disambig_notice = soup.find('div', id='mw-normal-catlinks')
        if disambig_notice and 'disambiguation' in disambig_notice.text.lower():
            return True
        else:
            return False
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return None


def clean_text(text):

    # Remove newline characters
    text = text.replace('\n', ' ')

    # Remove numbers within square brackets
    text = re.sub(r'\[\d+\]', '', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove leading and trailing spaces
    text = text.strip()

    return text



############ TEST FUNCTIONS START ############


def test_scrape(name):
    clear_scrape(name)


def test_multithreaded_scrape():
    # Test the multithreaded web scraping function
    web_scraper('../HTML/uploaded/InputData.xlsx', 10) # 2 entries
    # web_scraper('../xlsx files/InputData.xlsx') # all entries
    print(extracted_values)
    print(len(extracted_values.keys()))


############ TEST FUNCTIONS END ############
