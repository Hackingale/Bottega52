from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

model_name = "deepset/roberta-base-squad2"

# a) Get predictions
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
QA_input = {
    'question': 'Who is Cecilia?',
    'context': 'Cecilia is the smallest patata in the world'
}
res = nlp(QA_input)
print(res)