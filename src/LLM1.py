import queue
import threading
import time
import re
from gpt4all import GPT4All
import functions as func
import scraper as scr

# Define ConversationHandler class
class ConversationHandler:
    def __init__(self, model_path):
        self.thread = None
        self.model = GPT4All(model_path, n_ctx=8192, allow_download=True)
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
        self.condition = threading.Condition(lock=self.lock)
        self.number = 0
        self.thread2 = None
        self.stop = False

    def generate_response(self, prompt):
        with self.model.chat_session():
            output = self.model.generate(prompt, max_tokens=4096)
            return output
    def start(self, index, company_keys, companies, df, buyers, targets, influencers):
        self.thread = threading.Thread(target=self._start_conversation, args=(index, company_keys, companies, df, buyers, targets, influencers,))
        self.thread.start()
    def parse_category(self, text):
        pattern = r'\*\*(.*?)\*\*'
        matches = re.findall(pattern, text)
        cleaned_string = matches[0].strip("[]'")
        return cleaned_string

    def _start_conversation(self, index, company_keys, dict, df, buyers, targets, influencers):
        print('Starting the conversation\n')
        with self.condition:
            with self.model.chat_session():
                prompt = "I'll give you a list of Players. Please remember them because they're crucial; Each player has two attributes: Player (the role of the company in the market) and Notes (additional information about the player's role). I will provide you a company and its description. You have to tell me which kind of player the company is. You must not to come up with new players just use the ones I will provide"
                print(self.model.generate(prompt, max_tokens=4096))
                prompt = func.contextexcel_to_text("../HTML/uploaded/ContextData.xlsx") + "\nI will now provide you the company and its description. You have to tell me which kind of player the company is. Remember if you explicitly find the Player's category in the description it is probably the right player to choose and the right answer to give"
                print(self.model.generate(prompt, max_tokens=4096))
                self.number += 1
                self.condition.notify()

                while True:
                    while self.number == 1:
                        if self.stop:
                            break
                        self.condition.wait()
                    message = self.message_queue.get()
                    asterisk_index = message.find('*')
                    company = message[:asterisk_index]
                    message = message[asterisk_index+1:]
                    company = company.replace('*', '')
                    dict[company] = self.parse_category(self.model.generate(message, max_tokens=4096))
                    if self.stop:
                        break
                    self.number += 1
                    self.condition.notify()

        for index, row in df.iterrows():
            company = row['Company / Account']
            category = dict.get(company)
            if category != 'NULL':
                df.at[index, 'Sub-Type'] = category
                df.at[index, 'Website ok'] = 'TRUE'
            else:
                df.at[index, 'Sub- Type'] = 'NOT_VALID'
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
        df.to_excel('../xlsx files/output.xlsx', index=False)

    def send_input(self, user_input):
        self.message_queue.put(user_input)

    def start_messages(self, index, company_keys, companies, df):
        self.thread2 = threading.Thread(target=self.messages_in_queue, args=(index, company_keys, companies, df,))
        self.thread2.start()

    def messages_in_queue(self, index, company_keys, companies, df):
        print('Starting the conversation\n')
        with self.condition:
            while True:
                while self.number == 0:
                    self.condition.wait()
                description = ''
                company = ''
                company = company_keys[index]
                description = companies.get(company)
                index += 1
                if (description == 'NULL'):
                    self.stop = True
                    continue
                prompt = company + '*Answer with only one word by telling me just the player category of this Company: ' + company + ', using this description: ' + description + 'and as a rule mind that if you find the player in the description it is probably the right player to choose and the right answer to give'
                if (prompt == "exit"):
                    break
                self.send_input(prompt)
                self.number -= 1
                self.condition.notify()
                if (index >= len(company_keys)):
                    self.stop = True
                    self.condition.notify_all()
                    break