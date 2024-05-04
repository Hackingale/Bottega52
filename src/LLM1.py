import queue
import threading
import time
import re

from gpt4all import GPT4All
import functions as func

class ConversationHandler:
    def __init__(self, model_path):
        self.thread = None
        self.model = GPT4All(model_path, n_ctx=8192, allow_download=True)
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()

    def generate_response(self, prompt):
        with self.model.chat_session():
            output = self.model.generate(prompt, max_tokens=4096)
            return output

    def return_lock(self):
        return self.lock

    def start(self, companies):
        self.thread = threading.Thread(target=self._start_conversation(companies))
        self.thread.start()

    def parse_category(text):
        pattern = r'\*\*(.*?)\*\*'
        matches = re.findall(pattern, text)
        return matches


    def stop(self):
        self.thread.stop()

    def _start_conversation(self, dict):
        self.lock.acquire()
        with self.model.chat_session():
            prompt = "I'll give you a list of Players. Please remember them because they're crucial; Each player has two attributes: Player (the role of the company in the market) and Notes (additional information about the player's role). I will provide you a company and its description. You have to tell me which kind of player the company is. You must not to come up with new players just use the ones I will provide"
            output = self.model.generate(prompt, max_tokens=4096)
            print(output) #to be removed

            prompt = func.contextexcel_to_text(
                "../HTML/uploaded/ContextData.xlsx") + "\nI will now provide you the company and its description. You have to tell me which kind of player the company is. Remember if you explicitly find the Player's category in the description it is probably the right player to choose and the right answer to give"
            output = self.model.generate(prompt, max_tokens=4096)
            print(output) #to be removed

            self.lock.release()
            time.sleep(2)

            while True:
                # Acquire the lock to access the message queue
                self.lock.acquire()

                # Check if there are messages in the queue
                if not self.message_queue.empty():
                    message = self.message_queue.get()
                    # Process the message
                    asterisk_index = message.find('*')

                    # Extract the text before the asterisk
                    company = message[:asterisk_index]
                    company = company.replace('*', '')
                    dict[company] = self.parse_category(self.model.generate(message, max_tokens=4096))
                    #print(self.model.generate(message, max_tokens=4096))

                # Release the lock after processing the message
                self.lock.release()

    def send_input(self, user_input):
        self.message_queue.put(user_input)

    def handle_input(self, user_input):
        response = self.generate_response(user_input)
        print(response)
        if(self.lock.locked()):
            self.lock.release()


