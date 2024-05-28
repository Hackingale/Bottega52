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
from src.functions import remove_after_underscore

# Global variables
extracted_values = dict()  # Dictionary to store the extracted text from the web pages
scraped_entries = 0  # Counter to keep track of the number of scraped entries

# MAKE SURE ALL DEBUG COMMENTS ARE DEACTIVATED ONCE RUNNING FINAL VERSION

'''
This functon takes a URL and returns a list of all the links on the first level of the website
'''


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
Function to scrape the web page and extract the text content from the HTML
taking advantage of Clearbit to get possible domains of the company

:parameter extracted_values: dictionary to store the extracted text from the web pages
:parameter company_name: name of the company to scrape

:return 0 if the scraping was successful, 1 otherwise
'''


def clear_scrape(company_name):
    url = 'https://autocomplete.clearbit.com/v1/companies/suggest?query={' + company_name + '}'
    try:
        response = requests.get(url)
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
        for domain in domains:
            # here the function should iter over the domains and for each domain scrape the text
            # and scrape the text of the links in the first level of the website
            url = 'https://www.' + domain  # Replace example.com with your base URL

            # Extract the text content from the HTML
            extracted = ''
            ret = ''

            extracted = f.summarize_text(url, 'english', 3)
            translation = f.translate_text(extracted, 'en')
            ret = translation
            links = None
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


def unclear_scrape(company_url, company_name):
    # try spain first
    url = 'https://www.' + company_url + '.es'  # Replace example.com with your base URL
    extracted = f.summarize_text(url, 'spanish', 3)
    if extracted is None:
        # try italian
        url = 'https://www.' + company_url + '.it'
        extracted = f.summarize_text(url, 'italian', 3)
        if extracted is None:
            # try english
            url = 'https://www.' + company_url + '.com'
            extracted = f.summarize_text(url, 'english', 3)
            if extracted is None:
                extracted_values[company_name] = 'NULL'
                return 1
            else:
                translation = f.translate_text(extracted, 'en')
                extracted_values[company_name] = translation
                return 0
        else:
            translation = f.translate_text(extracted, 'en')
            extracted_values[company_name] = translation
            return 0
    else:
        translation = f.translate_text(extracted, 'en')
        extracted_values[company_name] = translation
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

        company_name = company_name.split('_')[0]  # Split the string and take the first part
        company_name = company_name.lower().strip()  # Convert to lowercase and remove whitespace

        # company already found
        if company_name in extracted_values:
            continue

        if pd.notnull(company_name):  # Check if company name is not null

            # remove everything after the last underscore as sometimes there may be the name of the contact
            company_url = remove_after_underscore(company_name)
            company_url = company_name_cleaning(company_url)

            # DOMAIN CLEANING
            if pd.notnull(email):  # Check if email is not null
                cleaned_domain = domain_cleaning(email)

                # if after that deletion the company is void, use the main domain
                if company_url == "":
                    company_url = cleaned_domain

            if clear_scrape(company_name) == 1:
                unclear_scrape(company_url, company_name)

            # updates extracted_values: company -> testo/NULL



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

'''
web_scraper('../HTML/uploaded/InputData.xlsx', 10)
print(extracted_values)
print(len(extracted_values.keys()))


'''