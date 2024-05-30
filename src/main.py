import time
import base64
import json
import pandas as pd
import os
import requests
from LLM1 import ConversationHandler
import src.functions as f
import scraper as scr
from HTML import fileupload
from multiprocessing import Process
import src.outputValidation as ov

TEMP = 0.1

def send_output_file(file_path):
    url = 'http://127.0.0.1:5000/provide_output'
    with open(file_path, 'rb') as f:
        encoded_file = base64.b64encode(f.read()).decode('utf-8')
    data = {
        'file_name': os.path.basename(file_path),
        'file_data': encoded_file
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("Output file sent successfully.")
    else:
        print("Failed to send output file.")

def start_flask_app():
    fileupload.app.run(debug=True, use_reloader=False)


if __name__ == '__main__':

    # Start the Flask app in a separate thread
    server = Process(target=start_flask_app)
    server.start()

    time.sleep(2)

    files_uploaded = False
    model_path = None

    while not files_uploaded:
        response = requests.get('http://127.0.0.1:5000/get_model_path')
        if response.status_code == 200:
            data = response.json()
            model_path = data.get('model_path')
            files_uploaded = data.get('files_uploaded')
        if not files_uploaded:
            print("Waiting for file upload...")
            time.sleep(2)


    # model_path = '/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0.gguf'
    #  model_path = '/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf'
    # model_path = '/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/wizardlm-13b-v1.2.Q4_0.gguf'
    # print(model_path)
    # Continue with your logic
    players = f.parse_players_from_excel('../HTML/uploaded/ContextData.xlsx')

    # todo this must be done after the category has been assigned
    buyers = f.create_buyers('../HTML/uploaded/ContextData.xlsx')
    targets = f.create_targets('../HTML/uploaded/ContextData.xlsx')
    influencers = f.create_influencers('../HTML/uploaded/ContextData.xlsx')

    df = f.count_employees('../HTML/uploaded/InputData.xlsx')  # Company name and number of employees

    df = f.file_initializer(buyers, targets, influencers,
                            df)  # Company name, number of employees, Buyer, Influencer, Target
    start = time.time()
    scr.web_scraper('../HTML/uploaded/InputData.xlsx', 10)  # create a dictionary < company, text / 'null' >
    companies = scr.extracted_values
    company_keys = list(companies.keys())
    f.print_elapsed_time(start)
    handler = ConversationHandler(model_path, players)
    handler.put_messages_in_queue(company_keys, companies)
    handler._start_conversation(companies, df, buyers, targets, influencers,
                                TEMP)  # Use the start function to start the thread instead of this
    send_output_file('../HTML/uploaded/output.xlsx')
    print(ov.validate_output(pd.read_excel('../HTML/uploaded/output.xlsx'), pd.read_excel('../HTML/uploaded/TestSetData.xlsx'), 'Company', ['Website ok (optional)']))

    server.terminate()
    server.join()