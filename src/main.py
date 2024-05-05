
from LLM1 import ConversationHandler
import src.functions as f
import scraper as scr
'''if __name__ == '__main__':
    fileupload.app.run(debug=True)
f.file_initializer(f.create_buyers('/Users/marco/Developer/GitHub/Botteg52/xlsx files/ContextData.xlsx'), f.create_targets('/Users/marco/Developer/GitHub/Botteg52/xlsx files/ContextData.xlsx'), f.create_influencers('/Users/marco/Developer/GitHub/Botteg52/xlsx files/ContextData.xlsx'), df)

'''

#TODO Choosing model path and change path of the model
#model_path = "/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
#model_path = '/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/orca-2-13b.Q4_0.gguf'

# Alessandro
model_path = '/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0.gguf'

# Marco
#model_path = '/Users/marco/Library/Application Support/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0.gguf'

# todo this must be done after the category has been assigned
buyers = f.create_buyers('../HTML/uploaded/ContextData.xlsx')
targets = f.create_targets('../HTML/uploaded/ContextData.xlsx')
influencers = f.create_influencers('../HTML/uploaded/ContextData.xlsx')

df = f.countemployees('../HTML/uploaded/InputData.xlsx')    #Company name and number of employees

df = f.file_initializer(buyers, targets, influencers, df) #Company name, number of employees, Buyer, Influencer, Target

companies = scr.web_scraper('../HTML/uploaded/InputData.xlsx') # create a dictionary < company, text / 'null' >

company_keys = list(companies.keys())
index = 0

handler = ConversationHandler(model_path)     #just make sure to parse the context file before doing this operation otherwise it will have no file
thread1 = handler.start(index, company_keys, companies, df, buyers, targets, influencers)
thread2 = handler.start_messages(index, company_keys, companies, df)

