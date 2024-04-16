from gpt4all import GPT4All
model = GPT4All("Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf", n_ctx = 10000, n_threads = 8, allow_download = True) # device='amd', device='intel'

with model.chat_session():
    while True:
        prompt = input("User: ")
        output = model.generate(prompt, max_tokens=4096)
        print(output)