import requests
import pandas as pd
from bs4 import BeautifulSoup
from functions import company_name_cleaning
from functions import domain_cleaning
from functions import remove_after_underscore

# MAKE SURE ALL DEBUG COMMENTS ARE DEACTIVATED ONCE RUNNING FINAL VERSION


def scrape_es(company_url, extracted_values, company_name):
    url = 'https://www.' + company_url + '.es'  # Replace example.com with your base URL

    try:
        response = requests.get(url, timeout=20)
    except requests.exceptions.RequestException as e:
        print("Failed to fetch:", url, "Error:", e)
        return 1
    extracted_values[company_name] = response
    return 0


def scrape_com(company_url, extracted_values, company_name):
    url = 'https://www.' + company_url + '.com'  # Replace example.com with your base URL

    try:
        response = requests.get(url, timeout=20)
    except requests.exceptions.RequestException as e:
        print("Failed to fetch:", url, "Error:", e)
        return 1
    extracted_values[company_name] = response
    return 0


def scrape_it(company_url, extracted_values, company_name):
    url = 'https://www.' + company_url + '.it'  # Replace example.com with your base URL

    try:
        response = requests.get(url, timeout=20)
    except requests.exceptions.RequestException as e:
        print("Failed to fetch:", url, "Error:", e)
        return 1
    extracted_values[company_name] = response
    return 0


# Function to scrape the web page and extract the text content from the HTML
# todo - deal with sites not reachable from the simple comapnyName.com
def web_scraper(file):
    # Read the Excel file
    df = pd.read_excel(file, header=None, usecols=[1, 3], skiprows=[0], names=['Contact E-mail', 'Company'])
    scraped_entries = 0

    # hashMap to store all extracted values from a website in order to avoid multiple searches
    extracted_values = dict()

    for email, company_name in zip(df['Contact E-mail'], df['Company']):

        # debug
        scraped_entries += 1

        print("#" * 100)

        if company_name in extracted_values:
            print("Company already extracted: " + company_name)
            print("Scraped entries:", scraped_entries)
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
            if scrape_es(company_url,extracted_values, company_name) == 1:
                if scrape_com(company_url, extracted_values, company_name) == 1:
                    if scrape_it(company_url, extracted_values, company_name) == 1:
                        print("Failed to fetch:", company_name)
                        print("Scraped entries:", scraped_entries)
                        print("#" * 100)
                        continue

        print("Scraped entries:", scraped_entries)
        print("#" * 100)


def status_code_ok(response, extracted_values, company_name):
    # Parse the HTML content of the web page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract only the text from the parsed HTML
    text = ' '.join(line.strip() for line in soup.get_text().splitlines() if line.strip())

    # Save the extracted text
    extracted_values[company_name] = text

    # Print the extracted text - DEBUG only
    print(company_name)


# DEBUG only
web_scraper("../xlsx files/InputData.xlsx")