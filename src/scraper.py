from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import threading

import pandas as pd
import functions as f
from bs4 import BeautifulSoup
from src.functions import company_name_cleaning
from src.functions import domain_cleaning
from src.functions import remove_after_underscore

extracted_values = dict()  # Dictionary to store the extracted text from the web pages

# MAKE SURE ALL DEBUG COMMENTS ARE DEACTIVATED ONCE RUNNING FINAL VERSION

def scrape_es(company_url, extracted_values, company_name):
    url = 'https://www.' + company_url + '.es'  # Replace example.com with your base URL
    extracted = f.summarize_text(url, 'spanish')
    if extracted is None:
        extracted_values[company_name] = 'NULL'
        return 1
    else:
        translation = f.translate_text(extracted, 'en')
        extracted_values[company_name] = translation
    return 0


def scrape_com(company_url, extracted_values, company_name):
    url = 'https://www.' + company_url + '.com'  # Replace example.com with your base URL
    extracted = f.summarize_text(url, 'english')
    if extracted is None:
        extracted_values[company_name] = 'NULL'
        return 1
    else:
        translation = f.translate_text(extracted, 'en')
        extracted_values[company_name] = translation
    return 0


def scrape_it(company_url, extracted_values, company_name):
    url = 'https://www.' + company_url + '.it'  # Replace example.com with your base URL
    extracted = f.summarize_text(url, 'italian')
    if extracted is None:
        extracted_values[company_name] = 'NULL'
        return 1
    else:
        translation = f.translate_text(extracted, 'en')
        extracted_values[company_name] = translation
    return 0


# Function to scrape the web page and extract the text content from the HTML
# todo - deal with sites not reachable from the simple companyName.com
# input: InputData file
def web_scraper(file):
    # Read the Excel file
    df = pd.read_excel(file, header=None, usecols=[1, 3], skiprows=[0], names=['Contact E-mail', 'Company / Account'])

    # Determine the number of rows in the file and calculate the number of rows each section should contain
    total_rows = len(df)
    rows_per_section = total_rows // 10  # Integer division to evenly distribute rows

    # Split the DataFrame into 10 sections
    sections = []
    for i in range(10):
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

            # scraping various ways - todo make it cleaner this is disgusting
            if scrape_es(company_url, extracted_values, company_name) == 1:
                if scrape_com(company_url, extracted_values, company_name) == 1:
                    if scrape_it(company_url, extracted_values, company_name) == 1:
                        continue

    # return extracted_values # company -> testo/NULL



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


def test_multithreaded_scrape():
    # Test the multithreaded web scraping function
    web_scraper('../xlsx files/InputData.xlsx')
    print(extracted_values)


#test_multithreaded_scrape()