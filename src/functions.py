from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import json
import unicodedata
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

from deep_translator import GoogleTranslator
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


# Function to remove text after the last underscore in the company name
def remove_after_underscore(company_name):
    # Find the last underscore in the company name
    last_underscore_index = company_name.rfind('_')

    # Check if an underscore was found
    if last_underscore_index != -1:
        # Remove the text after the last underscore
        cleaned_name = company_name[:last_underscore_index]
    else:
        # No underscore found, return the original name
        cleaned_name = company_name

    return cleaned_name


# company name cleaning
def company_name_cleaning(company_name):
    # Remove accents
    text = unicodedata.normalize('NFKD', company_name).encode('ASCII', 'ignore').decode('utf-8')
    # Remove special characters except letters and numbers
    cleaned_name = re.sub(r'[^a-zA-Z0-9]', '', text)
    # Convert to lowercase
    cleaned_name = cleaned_name.lower()
    return cleaned_name


def domain_cleaning(email):
    # Split the email address at '@' to get the domain part
    domain_part = email.split('@')[-1]
    # Split the domain part at '.' and take the first part
    cleaned_domain = domain_part.split('.')[0]
    return cleaned_domain

def extract_data_from_website(url):
    try:
        url = 'https://www.' + url
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all the text from the HTML and strip unnecessary spaces
            all_text = '\n'.join(line.strip() for line in soup.get_text(separator='\n').splitlines() if line.strip())

            return all_text
        else:
            return None
    except Exception as e:
        print("An error occurred while extracting data from", url)
        print(e)
        return None

def create_json_with_website_data(company_names, output_file):
    data = {}
    for company_name in company_names[:10]:
        extracted_data = extract_data_from_website(company_name)
        if extracted_data:
            data[company_name] = extracted_data

    try:
        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print("JSON file with website data created:", output_file)
    except Exception as e:
        print("An error occurred while writing JSON file:", e)

def contextexcel_to_text(xlsx_file):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_excel(xlsx_file)
    context_prompt = ''
    players = df['Player']
    notes = df['Notes']

    # Loop through the rows and access data
    for index, row in df.iterrows():
        player = row['Player']
        player_notes = row['Notes']

        # Perform further processing or analysis here
        context_prompt += f"Player: {player}, Notes: {player_notes}\n"

    return context_prompt

def extract_name_or_email(row):
    if row['Company / Account'].startswith('_'):
        return domain_cleaning(str(row['Contact E-mail']))
    else:
        return row['Company / Account']

def countemployees(input_file):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(input_file)

    df['Company / Account'] = df.apply(extract_name_or_email, axis=1)

    # Extract the company name from the 'Company name' column
    df['Company / Account'] = df['Company / Account'].str.split('_').str[0]

    # Convert company names to lowercase
    df['Company / Account'] = df['Company / Account'].str.lower()

    # Remove trailing spaces after the company name
    df['Company / Account'] = df['Company / Account'].str.strip()

    # Group the data by company name and get the size of each group (count of employees)
    result_df = df.groupby('Company / Account').size().reset_index(name='Number of Employees')

    # Save the result to an Excel file
    result_df.to_excel('../xlsx files/employee_counts.xlsx', index=False)

    #print("Excel file generated successfully.")

    return result_df


# Function to translate text to a target language
def translate_text(text, target_language):
    translation = GoogleTranslator(source='auto', target=target_language).translate(text)
    return translation


def summarize_text(url, lan):
    parser = HtmlParser.from_url(url, Tokenizer(lan))
    stemmer = Stemmer(lan)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(lan)
    text = ""
    for sentence in summarizer(parser.document, 10):
        text += str(sentence) + " \n"
        text += str(sentence)
    if text == '':
        return 1
    return text

def inputexcel_to_text(xlsx_file):
    df = countemployees(xlsx_file)
    # Iterate over each row in the DataFrame and extract the desired columns
    result = []
    for index, row in df.iterrows():
        companyname = row['Company / Account']

        # Append the extracted information as a dictionary to the result list
        result.append({
            'Company Name': companyname
        })

    # Print the result list (or do whatever you want with it)
    return result


def contextp_test(context):
    prompt = "I will provide you a list of Players in the context of the real estate market. Each player is characterized by these following attributes: Player (the role of the figure in the market), Can they buy the solution? (are they able to buy the house/estate), Can they influence the buying decision?, Notes(additional  info regarding the player's role)\n"
    prompt += contextexcel_to_text(context) + "\n"


def create_influencers(file):
    influencers = set()
    df = pd.read_excel(file)
    for index, row in df.iterrows():
        if row['Can they influence the buying decision?'] == 'YES':
            influencers.add(row['Player'])

    return influencers


def create_targets(file):
    targets = set()
    df = pd.read_excel(file)
    for index, row in df.iterrows():
        if row['Is Target'] == 'YES':
            targets.add(row['Player'])

    return targets


def create_buyers(file):
    buyers = set()
    df = pd.read_excel(file)
    for index, row in df.iterrows():
        if row['Can they buy the solution?'] == 'YES':
            buyers.add(str(row['Player']))

    return buyers


# todo make it modular
def file_initializer(buyers, targets, influencers, df):

    # Create a new DataFrame with the required columns
    df['Sub-Type'] = ''
    df['Buyer'] = 'NO'
    df['Influencer'] = 'NO'
    df['Target'] = 'NO'
    df['Website ok'] = 'NO'

    # iterate over the "Categories" column and check if the company is a buyer, target, or influencer
    for index, row in df.iterrows():
        company = row['Sub-Type']
        if company in buyers:
            df.at[index, 'Buyer'] = 'YES'
        else:
            df.at[index, 'Buyer'] = 'NO'
        if company in targets:
            df.at[index, 'Target'] = 'YES'
        else:
            df.at[index, 'Target'] = 'NO'
        if company in influencers:
            df.at[index, 'Influencer'] = 'YES'
        else:
            df.at[index, 'Influencer'] = 'NO'

        df.to_excel('../xlsx files/output.xlsx', index=False)

