import queue
import threading
import re
from gpt4all import GPT4All
import functions as func
from fuzzywuzzy import process

# Define ConversationHandler class
class ConversationHandler:
    def __init__(self, model_path, players):
        self.thread = None
        self.model = GPT4All(model_path, n_ctx=8192, allow_download=True)
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
        self.condition = threading.Condition(lock=self.lock)
        self.number = 0
        self.thread2 = None
        self.stop = False
        self.players = players


    def generate_response(self, prompt):
        with self.model.chat_session():
            output = self.model.generate(prompt, max_tokens=4096)
            return output
    def start(self, index, company_keys, companies, df, buyers, targets, influencers):
        self.thread = threading.Thread(target=self._start_conversation, args=(index, company_keys, companies, df, buyers, targets, influencers,))
        self.thread.start()

    def parse_category(self, text):
        # Attempt to find matches using regex pattern
        pattern = r'\*\*(.*?)\*\*'
        matches = re.findall(pattern, text)

        # If matches are found, return the first match
        if matches:
            cleaned_string = matches[0].strip("[]'")
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

    def _start_conversation(self, index, company_keys, dict, df, buyers, targets, influencers):
        with self.condition:
            print('Starting the conversation\n')
            context = func.contextexcel_to_text("../HTML/uploaded/ContextData.xlsx")
            while True:
                if self.stop:
                    break
                with self.model.chat_session():
                    for i in range(0, 15):
                                if(i == 0):
                                    print('restart window\n')
                                    prompt = "I'll give you a list of Players. Please remember them because they're crucial; Each player has two attributes: Player (the role of the company in the market) and Notes (additional information about the player's role). I will provide you a company and its description. You have to tell me which kind of player the company is. You must not to come up with new players just use the ones I will provide"
                                    (self.model.generate(prompt, max_tokens=4096))
                                    prompt = context + "\nI will now provide you the company and its description. You have to tell me which kind of player the company is. Remember if you explicitly find the Player's category in the description it is probably the right player to choose and the right answer to give"
                                    (self.model.generate(prompt, max_tokens=4096))
                                    self.number += 1
                                    self.condition.notify()
                                while self.number == 1:
                                    if self.stop:
                                        break
                                    self.condition.wait()
                                message = self.message_queue.get()
                                asterisk_index = message.find('*')
                                company = message[:asterisk_index]
                                message = message[asterisk_index+1:]
                                company = company.replace('*', '')
                                answer = self.model.generate(message, max_tokens=4096)
                                answer = self.parse_category(answer)
                                answer = self.find_most_similar_category(answer)
                                dict[company] = self.parse_category(answer)
                                print('Company ' + company + ' evaluated\n')
                                if self.stop:
                                    break
                                if(i < 14):
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
                # todo solve a possible index out of range
                description = companies.get(company)
                index += 1
                if (description == 'NULL'):
                    continue
                prompt = company + '*Perfect! Answer with only one word by telling me just the category of this Company based on the context file I gave you. It is mandatory to put the answer you find between ** and ** like this: **Answer**: ' + company + ', using this description: ' + description + 'and as a rule mind that if you find the player in the description it is probably the right player to choose and the right answer to give'
                if (prompt == "exit"):
                    break
                self.send_input(prompt)
                self.number -= 1
                self.condition.notify()
                if index >= len(company_keys):
                    self.stop = True
                    self.number = 0
                    self.condition.notify_all()
                    break
