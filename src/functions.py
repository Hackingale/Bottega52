import json
import unicodedata
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


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

    players = df['Player']
    can_buy = df['Can they buy the solution?']
    influence_decision = df['Can they influence the buying decision?']
    target = df['Is Target']
    notes = df['Notes']

    context_prompt = ""
    # Loop through the rows and access data
    for index, row in df.iterrows():
        player = row['Player']
        can_buy_solution = row['Can they buy the solution?']
        influence_buying_decision = row['Can they influence the buying decision?']
        istarget = row['Is Target']
        player_notes = row['Notes']

        # Perform further processing or analysis here
        context_prompt += f"Player: {player}, Can Buy: {can_buy_solution}, Influence Decision: {influence_buying_decision}, Is Target: {istarget}, Notes: {player_notes}\n"

    return context_prompt

def extract_name_or_email(row):
    if row['Company / Account'].startswith('_'):
        return domain_cleaning(str(row['Contact E-mail']))
    else:
        return row['Company / Account']

def countemployees(input):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(input)

    df['Company / Account'] = df.apply(extract_name_or_email, axis=1)

    # Extract the company name from the 'Company name' column
    df['Company / Account'] = df['Company / Account'].str.split('_').str[0]

    # Convert company names to lowercase
    df['Company / Account'] = df['Company / Account'].str.lower()

    # Remove trailing spaces after the company name
    df['Company / Account'] = df['Company / Account'].str.strip()

    first_element = df.iloc[0, 0]
    print(first_element)

    # Group the data by company name and get the size of each group (count of employees)
    result_df = df.groupby('Company / Account').size().reset_index(name='Number of Employees')

    # Save the result to an Excel file
    result_df.to_excel('employee_counts.xlsx', index=False)

    #print("Excel file generated successfully.")

    return result_df


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

def prompt_creation(input, context):
    prompt = "I will provide you a list of Players in the context of the real estate market. Each player is characterized by these following attributes: Player (the role of the figure in the market), Can they buy the solution? (are they able to buy the house/estate), Can they influence the buying decision?, Notes(additional  info regarding the player's role)\n"
    prompt += contextexcel_to_text(context) + "\n"
    prompt += "Now I will provide a list of people, every pair of curly brackets represents a person. The first element of the pair is the Job Title of the contact, and the second element is the Company or Account for which the person works for. For example, {'Contact Job Title': 'Chief of operations', 'Company / Account': 'Urban Campus'} means that the person is the Chief of operations and his company is Urban Campus. The list of people is as follows:\n"
    prompt += str(inputexcel_to_text(input)) + "\n"
    prompt += "Now I will provide you a text extracted from the website of the first company in the list of people. The text is as follows: \n"
    prompt += "Based on the information provided using the list of players and the company, please generate a text that reports the following information: Company, #Contacts, Type of Company, Sub-type, Buyer (yes/no), Influencer (yes/no), Target Market (true/false), Website reachable (true/false)\n"
    return prompt

    # Call the function and store the return value
    return_string = prompt_creation("InputData.xlsx", "Categories.xlsx")

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


def file_sguccer(buyers, targets, influencers, df):

    # Create a new DataFrame with the required columns
    df['Sub-Type'] = 'Constructor'
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

        df.to_excel('output.xlsx', index=False)

