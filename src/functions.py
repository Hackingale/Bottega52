from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import json
import random
import unicodedata
from time import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import spacy
from sumy.parsers.plaintext import PlaintextParser
from textblob import TextBlob

from deep_translator import GoogleTranslator
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")


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
    # Remove special characters except letters, numbers and spaces
    cleaned_name = re.sub(r'[^a-zA-Z0-9]', '', text)
    # Convert to lowercase
    cleaned_name = cleaned_name.lower()
    return cleaned_name


def domain_cleaning(email):
    # Split the email address at '@' to get the domain part
    domain_part = email.split('@')[-1]
    # Split the domain part at '.' and take the first part
    cleaned_domain = domain_part.split('.')[0]
    # convert characters that might be representing a space to spaces
    cleaned_domain = cleaned_domain.replace('-', ' ')
    cleaned_domain = cleaned_domain.replace('_', ' ')
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


# most recurrent player in column Sub-type of the dataframe of the input excel file different from NOT_VALID
def most_recurrent_player(input_file):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(input_file)

    # Filter out rows where 'Sub-Type' is 'NOT_VALID'
    df = df[df['Sub-Type'] != 'NOT_VALID']

    # Group the data by 'Sub-Type' and get the size of each group
    result_df = df.groupby('Sub-Type').size().reset_index(name='Count')

    # Find the most recurrent player
    most_recurrent_player = result_df.loc[result_df['Count'].idxmax()]['Sub-Type']

    return most_recurrent_player


def context_excel_to_text(xlsx_file):
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


def count_employees(input_file):
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
    result_df = df.groupby('Company / Account').size().reset_index(name='# contacts')

    # Save the result to an Excel file
    result_df.to_excel('../xlsx files/employee_counts.xlsx', index=False)

    #print("Excel file generated successfully.")

    return result_df


# Function to translate text to a target language
def translate_text(text, target_language):
    if text is None:
        return None
    return GoogleTranslator(source='auto', target=target_language).translate(text) if text is not None else None


def count_sentences(text):
    # Split text by sentence delimiters and filter out any empty strings
    sentences = re.split(r'[.!?]+', text)
    # Remove empty strings that can occur after splitting
    sentences = [sentence for sentence in sentences if sentence.strip()]
    return len(sentences)


def summarize_text(url, lan, num_sentences):
    text = ''
    try:
        # summarize an html text with sumy
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        for data in soup(['style', 'script']):
            # Remove tags
            data.decompose()

            # return data by retrieving the tag content
        soup = ' '.join(soup.stripped_strings)

        parser = PlaintextParser.from_string(soup, Tokenizer(lan))
        stemmer = Stemmer(lan)
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(lan)
        for sentence in summarizer(parser.document, num_sentences):
            text += str(sentence) + '. '

    except Exception as e:
        # Optionally print or log the error
        # print("Error:", e)
        return None  # Return None or any other value indicating failure

    if text == '':
        return None

    return text


def contains_common_sense_phrases(text):

    # if text only contains numbers, return False
    if text.replace(" ", "").isdigit():
        return False

    # Analyze the text with spaCy
    doc = nlp(text)

    # Check for negations or contradictory phrases
    for token in doc:
        if token.dep_ == 'neg':
            return False

    # Perform sentiment analysis with TextBlob
    blob = TextBlob(text)
    sentiment = blob.sentiment

    # Assume that text with neutral or positive sentiment is more likely to contain common sense phrases
    if sentiment.polarity >= 0:
        return True
    else:
        return False


def random_choice(links, percentage):

    factor = percentage / 100
    # Define the range
    start_range = 0
    end_range = len(links) - 1

    # Choose n random numbers within the range
    n = end_range * factor
    n = round(n)
    random_numbers = random.sample(range(start_range, end_range + 1), n)

    # Print the randomly chosen numbers
    # print("Random numbers within the range:", random_numbers)
    chosen_links = []

    for i in random_numbers:
        chosen_links.append(links[i])
    return chosen_links


def specific_random_choice(links, number):

    # Define the range
    start_range = 0
    end_range = len(links) - 1
    n = number
    # Choose n random numbers within the range
    if number > end_range:
        n = end_range
    random_numbers = random.sample(range(start_range, end_range + 1), n)

    # Print the randomly chosen numbers
    # print("Random numbers within the range:", random_numbers)
    chosen_links = []

    for i in random_numbers:
        chosen_links.append(links[i])
    return chosen_links


def input_excel_to_text(xlsx_file):
    df = count_employees(xlsx_file)
    # Iterate over each row in the DataFrame and extract the desired columns
    result = []
    for index, row in df.iterrows():
        company_name = row['Company / Account']

        # Append the extracted information as a dictionary to the result list
        result.append({
            'Company Name': company_name
        })

    # Print the result list (or do whatever you want with it)
    return result


def context_test(context):
    prompt = ("I will provide you a list of Players in the context of the real estate market. Each player is "
              "characterized by these following attributes: Player (the role of the figure in the market), "
              "Can they buy the solution? (are they able to buy the house/estate), Can they influence the buying "
              "decision?, Notes(additional  info regarding the player's role)\n")
    prompt += context_excel_to_text(context) + "\n"


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


def parse_players_from_excel(file_path):
    try:
        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(file_path)

        # Check if 'Players' column exists
        if 'Player' in df.columns:
            # Get the values from the 'Players' column and convert them to a set
            players_set = set(df['Player'].dropna())
            return players_set
    except Exception as e:
        print(f"Error: {e}")
        return set()


def file_initializer(buyers, targets, influencers, df):

    # Create a new DataFrame with the required columns
    df['Sub-Type'] = ''
    df['Buyer (optional)'] = 'NO'
    df['Influencer (optional)'] = 'NO'
    df['Target'] = 'FALSE'
    df['Website ok (optional)'] = 'FALSE'
    return df

def print_elapsed_time(start):
    end = time()
    elapsed_time = end - start

    if elapsed_time < 60:
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
    else:
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"Elapsed time: {minutes}:{seconds:02d} mins")


summarize_text('https://www.lagardere.com', 'english', 3)