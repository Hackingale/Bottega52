import time
import base64
import pandas as pd
import os
import requests
from LLM1 import ConversationHandler
import src.functions as f
import scraper as scr
from HTML import fileupload
from multiprocessing import Process
import src.outputValidation as oV

TEMP = 0.1


def send_output_file(file_path):
    url = 'http://127.0.0.1:5000/provide_output'
    with open(file_path, 'rb') as file:
        encoded_file = base64.b64encode(file.read()).decode('utf-8')
    datapath = {
        'file_name': os.path.basename(file_path),
        'file_data': encoded_file
    }
    answer = requests.post(url, json=datapath)
    if answer.status_code == 200:
        print("Output file sent successfully.")
    else:
        print("Failed to send output file.")


def start_flask_app():
    fileupload.app.run(debug=False, use_reloader=False)


if __name__ == '__main__':
    server = Process(target=start_flask_app)
    model_path = None
    deb = input("Do you want to skip the file upload process? (y/n): ")
    if deb == 'n':

        # Start the Flask app in a separate thread
        server.start()
        time.sleep(2)
        files_uploaded = False


        while not files_uploaded:
            response = requests.get('http://127.0.0.1:5000/get_model_path')
            if response.status_code == 200:
                data = response.json()
                model_path = data.get('model_path')
                files_uploaded = data.get('files_uploaded')
            if not files_uploaded:
                print("Waiting for file upload...")
                time.sleep(2)


    if deb == 'y':
        model_path = '../HTML/uploaded/'

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
    print(oV.validate_output(pd.read_excel('../HTML/uploaded/output.xlsx'),
                             pd.read_excel('../HTML/uploaded/TestSetData.xlsx'),
                             'Company',
                             ['Website ok (optional)']))
    if deb == 'n':
        server.terminate()
        server.join()
