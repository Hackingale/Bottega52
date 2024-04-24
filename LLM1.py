from gpt4all import GPT4All
import functions as func
import getpass

#get current user function
def get_current_user():
    return getpass.getuser()
def contextest():
    with model.chat_session():
        '''prompt = "I will provide you a list of Players in the context of the real estate market. Each player is characterized by these following attributes: Player (the role of the figure in the market), Can they buy the solution? (are they able to buy the house/estate), Can they influence the buying decision?, Notes(additional  info regarding the player's role)\n"
        prompt += func.contextexcel_to_text("Categories.xlsx")
        output = model.generate(prompt, max_tokens = 4096) #remove output print
        print(output)'''
        prompt = "Now I will provide a list of people, every pair of curly brackets represents a person. The first element of the pair is the Job Title of the contact, and the second element is the Company or Account for which the person works for. For example, {'Contact Job Title': 'Chief of operations', 'Company / Account': 'Urban Campus'} means that the person is the Chief of operations and his company is Urban Campus. The list of people is as follows:\n"
        prompt += str(func.inputexcel_to_text("InputData.xlsx")) + "\n"
        output = model.generate(prompt, max_tokens = 4096)
        print(output)
        while True:
            prompt = input("User: ")
            output = model.generate(prompt, max_tokens=4096)
            print(output)

path_to_gpt = "/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf" # works on my machine, let's see if it works on yours
model = GPT4All(path_to_gpt, n_ctx = 10000, allow_download = True)
contextest()
