from gpt4all import GPT4All
import functions as func
model = GPT4All("/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf", n_ctx = 10000, n_threads = 8, allow_download = True)

def contextest():
    with model.chat_session():
        prompt = func.contextexcel_to_text("Categories.xlsx")
        output = model.generate(prompt, max_tokens = 4096)
        print(output)
        while True:
            prompt = input("User: ")
            output = model.generate(prompt, max_tokens=4096)
            print(output)



