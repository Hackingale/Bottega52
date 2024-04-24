import requests
import pandas as pd
from bs4 import BeautifulSoup

# Function to scrape the web page and extract the text content from the HTML
# todo - deal with sites not reachable from the simple comapnyName.com 
def web_scraper(file):
    # Read the Excel file
    df = pd.read_excel(file, header=None, usecols=[3], skiprows=[0], names=['Company'])

    company_column = df['Company']

    for company_name in company_column:
        if pd.notnull(company_name):  # Check if company name is not null
            url = 'https://www.' + company_name + '.com'  # Replace example.com with your base URL
            response = requests.get(url)

            if response.status_code == 200:
                # Parse the HTML content of the web page
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract only the text from the parsed HTML
                text = ' '.join(line.strip() for line in soup.get_text().splitlines() if line.strip())

                # Print the extracted text
                print(text)
            else:
                print("Failed to fetch:", url, "Status Code:", response.status_code)
        else:
            print("Company name is null or empty.")

web_scraper("InputData.xlsx")