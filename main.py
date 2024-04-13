import google.generativeai as ai
import functions as f
import config

def response(input, context, model):
    prompt = f.prompt_creation(input, context)
    #TODO for every contact add some web scraping on the company website to get more information
    #TODO once the information is gathered, add it to the prompt and send it to the model asking to generate a text well formatted
    #TODO the output should report Company, #Contacts, Type of Company, Sub-type, Buyer (yes/no), Influencer (yes/no), Target Market (true/false), Website rachable(true/false)

    completion = ai.generate_text(model=model, prompt=prompt, temperature=0, max_output_tokens=800)
    print(completion.result)

ai.configure(api_key=config.API_key)
models = [m for m in ai.list_models() if "generateText" in m.supported_generation_methods]
model = models[0].name

result = response("I am a software engineer", model)
print(result)
