import json

import pandas as pd
import requests
from bs4 import BeautifulSoup


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

    players = df['Player']
    can_buy = df['Can they buy the solution?']
    influence_decision = df['Can they influence the buying decision?']
    notes = df['Notes']

    context_prompt = ""
    # Loop through the rows and access data
    for index, row in df.iterrows():
        player = row['Player']
        can_buy_solution = row['Can they buy the solution?']
        influence_buying_decision = row['Can they influence the buying decision?']
        player_notes = row['Notes']

        # Perform further processing or analysis here
        context_prompt += f"Player: {player}, Can Buy: {can_buy_solution}, Influence Decision: {influence_buying_decision}, Notes: {player_notes}\n"

    return context_prompt

def inputexcel_to_text(xlsx_file):
    df = pd.read_excel(xlsx_file)

    # Iterate over each row in the DataFrame and extract the desired columns
    result = []
    for index, row in df.iterrows():
        contact_job_title = row['Contact Job Title']
        company = row['Company / Account']

        # Append the extracted information as a dictionary to the result list
        result.append({
            'Contact Job Title': contact_job_title,
            'Company / Account': company
        })

    # Print the result list (or do whatever you want with it)
    return result

def prompt_creation(input, context):
    prompt = "I will provide you a list of Players in the context of the real estate market. Each player is characterized by these following attributes: Player (the role of the figure in the market), Can they buy the solution? (are they able to buy the house/estate), Can they influence the buying decision?, Notes(additional  info regarding the player's role)\n"
    prompt += contextexcel_to_text(context) + "\n"
    prompt += "Now I will provide a list of people, every pair of curly brackets represents a person. The first element of the pair is the Job Title of the contact, and the second element is the Company or Account for which the person works for. For example, {'Contact Job Title': 'Chief of operations', 'Company / Account': 'Urban Campus'} means that the person is the Chief of operations and his company is Urban Campus. The list of people is as follows:\n"
    prompt += inputexcel_to_text(input) + "\n"
    return prompt