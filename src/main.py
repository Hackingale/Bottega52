from LLM1 import ConversationHandler
import time
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
#model_path = '/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0.gguf'

# Marco
model_path = '/Users/marco/Library/Application Support/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0.gguf'

buyers = f.create_buyers('../HTML/uploaded/ContextData.xlsx')
targets = f.create_targets('../HTML/uploaded/ContextData.xlsx')
influencers = f.create_influencers('../HTML/uploaded/ContextData.xlsx')

df = f.countemployees('../HTML/uploaded/InputData.xlsx')    #Company name and number of employees

df = f.file_initializer(buyers, targets, influencers, df) #Company name, number of employees, Buyer, Influencer, Target

companies = scr.web_scraper('../HTML/uploaded/InputData.xlsx') # create a dictionary < company, text / 'null' >

handler = ConversationHandler(model_path)     #just make sure to parse the context file before doing this operation otherwise it will have no file
handler.start(companies)

company_keys = list(companies.keys())
index = 0
time.sleep(2) #TODO prova a rimuovere questo
while True:
    time.sleep(0.5)
    handler.lock.acquire()
    description = ''
    company = ''
    company = company_keys[index]
    description = companies.get(company)
    index += 1
    if(description == 'NULL'):
        continue
    #prompt = input("Enter a prompt: ")   #Answer with only one word by telling me just the player category of this Company: {dict.company}, using this description: {dict.text}
    prompt = company + '*Answer with only one word by telling me just the player category of this Company: ' + company + ', using this description: ' + description
    if(index >= len(company_keys)):
        handler.lock.release()
        handler.stop()
        break;
    if(prompt == "exit"):
        handler.lock.release()
        handler.stop()
        break
    handler.send_input(prompt)
    handler.lock.release()

for index, row in df.iterrows():
    company = row['Company / Account']
    category = companies.get(company)
    if category != 'NULL':
        df.at[index, 'Sub-Type'] = category
        df.at[index, 'Website ok'] = 'YES'
    else:
        df.at[index, 'Sub- Type'] = 'NOT_VALID'
        df.at[index, 'Website ok'] = 'NO'

df.to_excel('/src/OutputData.xlsx', index=False)