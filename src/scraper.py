from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import pandas as pd
import functions as f
from bs4 import BeautifulSoup
from src.functions import company_name_cleaning
from src.functions import domain_cleaning
from src.functions import remove_after_underscore

# MAKE SURE ALL DEBUG COMMENTS ARE DEACTIVATED ONCE RUNNING FINAL VERSION


def scrape_es(company_url, extracted_values, company_name):
    url = 'https://www.' + company_url + '.es'  # Replace example.com with your base URL
    extracted = f.summarize_text(url, 'spanish')
    translation = f.translate_text(extracted, 'en')
    if extracted is None:
        extracted_values[company_name] = 'NULL'
        return 1
    else:
        extracted_values[company_name] = extracted
    return 0


def scrape_com(company_url, extracted_values, company_name):
    url = 'https://www.' + company_url + '.com'  # Replace example.com with your base URL
    extracted = f.summarize_text(url, 'english')
    translation = f.translate_text(extracted, 'en')
    if extracted is None:
        extracted_values[company_name] = 'NULL'
        return 1
    else:
        extracted_values[company_name] = extracted
    return 0


def scrape_it(company_url, extracted_values, company_name):
    url = 'https://www.' + company_url + '.it'  # Replace example.com with your base URL
    extracted = f.summarize_text(url, 'italian')
    translation = f.translate_text(extracted, 'en')
    if extracted is None:
        extracted_values[company_name] = 'NULL'
        return 1
    else:
        extracted_values[company_name] = extracted
    return 0


# Function to scrape the web page and extract the text content from the HTML
# todo - deal with sites not reachable from the simple companyName.com
# input: InputData file
def web_scraper(file):
    # Read the Excel file
    df = pd.read_excel(file, header=None, usecols=[1, 3], skiprows=[0], names=['Contact E-mail', 'Company / Account'])
    scraped_entries = 0

    # hashMap to store all extracted values from a website in order to avoid multiple searches
    extracted_values = dict()

    for email, company_name in zip(df['Contact E-mail'], df['Company / Account']):

        # debug
        scraped_entries += 1

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

            # scraping various ways - todo make it cleaner this is disgusting
            if scrape_es(company_url, extracted_values, company_name) == 1:
                if scrape_com(company_url, extracted_values, company_name) == 1:
                    if scrape_it(company_url, extracted_values, company_name) == 1:
                        continue

    return extracted_values # company -> testo/NULL


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
    print(company_name)


# TEST FUNCTION
def test_scrape(url):
    summary = f.summarize_text(url, 'english')
    translation = f.translate_text(summary, 'en')
    print(translation)

