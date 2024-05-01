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
model_path = "/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"

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
