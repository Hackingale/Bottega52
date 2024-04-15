import requests
import pandas as pd
from urllib.parse import urlparse
url = 'https://www.linkedin.com/company/'
# Read the Excel file
df = pd.read_excel('Manual Classification.xlsx')

company = df['Company'].apply(lambda x: x.split('.')[0])

for index in range(len(company)):
    first_value = company.iloc[index]
    response = requests.get(url + first_value)
    if response.status_code == 200:
        print(f"{first_value} is reachable")
    else:
        print(response.status_code)

