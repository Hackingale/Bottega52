from LLM1 import ConversationHandler, get_external_input
import time
'''if __name__ == '__main__':
    fileupload.app.run(debug=True)
'''
'''
import src.functions as f

df = f.countemployees('/Users/marco/Developer/GitHub/Botteg52/xlsx files/InputData.xlsx')

f.file_sguccer(f.create_buyers('/Users/marco/Developer/GitHub/Botteg52/xlsx files/Categories.xlsx'), f.create_targets('/Users/marco/Developer/GitHub/Botteg52/xlsx files/Categories.xlsx'), f.create_influencers('/Users/marco/Developer/GitHub/Botteg52/xlsx files/Categories.xlsx'), df)

'''
#model_path = "/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"

model_path = '/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0.gguf'

#model_path = '/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/orca-2-13b.Q4_0.gguf'

handler = ConversationHandler(model_path)
handler.start()

time.sleep(2)
while True:
    time.sleep(0.5)
    handler.lock.acquire()
    prompt = input("Enter a prompt: ")
    user_input = get_external_input(prompt)
    if(user_input == "exit"):
        handler.stop()
        break
    handler.send_input(user_input)
    handler.lock.release()

#Answer with only one word by telling me just the player category of this Company: ACR, using this description: We innovate to adapt to new needs and respond to the challenges of the moment. We work to lead the transformation of construction towards an increasingly responsible, innovative and sustainable industry. We seek the satisfaction of our clients thanks to the Lean Construction model and a sense of radical collaboration that underpins our strategy, encompasses all our collaborators and is reflected in all our projects. We are looking for people with initiative, efficient and productive, who have a predisposition for teamwork, the ability to adapt to change and customer orientation. If you believe in collaborative, dynamic and innovative environments, look no further. ACR is your place! Designed by TdB Arquitectura, the B&B hotel in Tres Cantos, which we are building together with Casais, is advancing at a dizzying pace. And in just 14 days, in addition to the hybrid wood and concrete structure of the CREE Buildings system, the façade has also been assembled, with an exterior finish included with frames and glass, and the industrialized bathrooms and bathrooms are already distributed throughout the floors. piping kits for installations.


