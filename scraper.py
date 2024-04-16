import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
url = 'https://www.'
# Read the Excel file
df = pd.read_excel('Manual Classification.xlsx')

company = df['Company']

for index in range(1):
    first_value = company.iloc[index]
    response = requests.get(url + first_value)
    if response.status_code == 200:
        # Parse the HTML content of the web page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract only the text from the parsed HTML
        text = ' '.join(line.strip() for line in soup.get_text().splitlines() if line.strip())

        # Print the extracted text
        print(text)
    else:
        print(response.status_code)

