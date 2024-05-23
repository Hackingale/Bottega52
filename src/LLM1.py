import queue
import threading
import re
import time
import functions as f
import functions as func
import requests
from gpt4all import GPT4All
from fuzzywuzzy import process

# Define ConversationHandler class
class ConversationHandler:
    def __init__(self, model_path, players):
        self.thread = None
        self.model = GPT4All(model_path, n_ctx=8192, allow_download=False)
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
        self.stop = False
        self.players = players
        self.progress = 0
        self.totalNumber = 0

    #Passing the arguments to the start conversation and starts the thread
    def start(self, companies, df, buyers, targets, influencers, TEMP):
        self.thread = threading.Thread(target=self._start_conversation, args=(companies, df, buyers, targets, influencers, TEMP,))
        self.thread.start()
        return self.thread

    # Function to parse the category from the generated text
    def parse_category(self, text):
        if not isinstance(text, str):
            return 'NULL'
        # Attempt to find matches using regex pattern
        pattern = r'\*\*(.*?)\*\*'
        matches = re.findall(pattern, text)

        # If matches are found, return the first match
        for match in matches:
            cleaned_string = match.strip("[]'")
            if cleaned_string.lower() != 'answer':
                cleaned_string = self.find_most_similar_category(cleaned_string)
                return cleaned_string

        # If no matches are found, search for names from the given set
        for name in self.players:
            if name.lower() in text.lower():
                return name

        # If neither matches nor names from the set are found, return 'NULL'
        return 'NULL'

    def find_most_similar_category(self, input_word):
        # Use fuzzy matching to find the closest match from the categories set
        closest_match, score = process.extractOne(input_word.strip(), self.players)

        # If the similarity score is above a certain threshold, consider it a match
        if score >= 90:  # Adjust threshold as needed
            return closest_match
        else:
            return None  # If no close match found, return None

    def _start_conversation(self, dict, df, buyers, targets, influencers, TEMP):
        self.totalNumber = self.message_queue.qsize()
        requests.post('http://127.0.0.1:5000/companies_scraped', json={'num_companies_scraped': self.totalNumber})
        print('Starting the conversation\n')
        start = time.time()
        context = func.context_excel_to_text("../HTML/uploaded/ContextData.xlsx")
        number_of_companies = self.message_queue.qsize()
        while self.message_queue.qsize() > 0:
            with self.model.chat_session() as session:
                for i in range(0, 12):
                            if(i == 0):
                                print('restart window\n')
                                prompt = ("I'll give you a list of Players. Please remember them because they're crucial; "
                                  "Each player has two attributes: Player (the role of the company in the market) "
                                  "and Notes (additional information about the player's role). I will provide you a "
                                  "company and its description. You have to tell me which kind of player the company is. "
                                  "You must not come up with new players just use the ones I will provide")
                                (self.model.generate(prompt, max_tokens=4096, temp=TEMP)) #we can make it nicer by using generate response
                                prompt = context + ("\nI will now provide you the company and its description. You have to tell "
                                                    "me which kind of player the company is. Remember if you explicitly find the Player's "
                                                    "category in the description it is probably the right player to choose and the right answer to give.")
                                (self.model.generate(prompt, max_tokens=4096, temp=TEMP))
                            if self.stop:
                                break
                            message = self.message_queue.get()
                            asterisk_index = message.find('*')
                            company = message[:asterisk_index]
                            message = message[asterisk_index+1:]
                            company = company.replace('*', '')
                            answer = self.model.generate(message, max_tokens=4096, temp=TEMP)
                            print('answer: ' + answer)
                            answer = self.parse_category(answer)
                            if(answer != 'NULL'):
                                dict[company] = answer #self.parse_category(answer)
                            else:
                                dict[company] = 'NA'
                            print('Company ' + company + ' evaluated\n')
                            self.progress += 1
                            requests.post('http://127.0.0.1:5000/increment_counter')
                            print('Progress: ' + str(self.progress) + ' of ' + str(number_of_companies) + '\n')
                            if self.stop or (self.message_queue.qsize() == 0):
                                break
        f.print_elapsed_time(start)
        time.sleep(2)
        for index, row in df.iterrows():
            company = row['Company / Account']
            category = dict.get(company)
            if category != 'NULL':
                df.at[index, 'Sub-Type'] = category
                df.at[index, 'Website ok'] = 'TRUE'
            else:
                df.at[index, 'Sub-Type'] = 'NOT_VALID'
                df.at[index, 'Website ok'] = 'FALSE'

        for index, row in df.iterrows():
            company = row['Sub-Type']
            if company in buyers:
                df.at[index, 'Buyer'] = 'YES'
            else:
                df.at[index, 'Buyer'] = 'NO'
            if company in targets:
                df.at[index, 'Target'] = 'TRUE'
            else:
                df.at[index, 'Target'] = 'FALSE'
            if company in influencers:
                df.at[index, 'Influencer'] = 'YES'
            else:
                df.at[index, 'Influencer'] = 'NO'
        df.to_excel('../HTML/uploaded/output.xlsx', index=False)

    def generate_response(self, prompt, TEMP):
        with self.model.chat_session():
            output = self.model.generate(prompt, max_tokens=4096, temp=TEMP)
            return output

    def send_input(self, user_input):
        self.message_queue.put(user_input)

    def put_messages_in_queue(self, company_keys, companies):
        print('Starting the conversation\n')
        for i in range(0, len(company_keys)):
            print('index is: ' + str(i) + '\n')
            company = company_keys[i]
            description = companies.get(company)
            if (description == 'NULL' or description == 'null' or description == 'None' or description == 'none' or description == '' or len(description) <=10):
                continue
            prompt = company + '*Perfect! Answer with only one word by telling me just the category of this Company based on the context file I gave you. It is mandatory to put the answer you find between ** and ** (e.g. **Player**). Now answer company name: ' + company + ', using this description: ' + description + 'and as a rule mind that if you find the player in the description it is probably the right player to choose and the right answer to give'
            if (prompt == "exit"):
                break
            self.send_input(prompt)