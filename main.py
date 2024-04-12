#Alessandro Aldo Marina & Marco Laurenzi
#Bottega52 Project on LLMs

import sagemaker
import boto3
from sagemaker.huggingface import HuggingFace

try:
    role = sagemaker.get_execution_role()
except ValueError:
    iam = boto3.client('iam')
    role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

hyperparameters = {
    'model_name_or_path': 'deepset/roberta-base-squad2',
    'output_dir': '/opt/ml/model'
    # add your remaining hyperparameters
    # more info here https://github.com/huggingface/transformers/tree/v4.37.0/examples/pytorch/question-answering
}

# git configuration to download our fine-tuning script
git_config = {'repo': 'https://github.com/huggingface/transformers.git', 'branch': 'v4.37.0'}

# creates Hugging Face estimator
huggingface_estimator = HuggingFace(
    entry_point='run_qa.py',
    source_dir='./examples/pytorch/question-answering',
    instance_type='ml.p3.2xlarge',
    instance_count=1,
    role=role,
    git_config=git_config,
    transformers_version='4.37.0',
    pytorch_version='2.1.0',
    py_version='py310',
    hyperparameters=hyperparameters
)
# starting the train job
huggingface_estimator.fit()

from transformers import AutoModelForCausalLM, AutoTokenizer, AutoTokenizer, AutoModelForQuestionAnswering, pipeline

# Load the LLM model
#TODO implement the choice of the LLM
model_name = "deepset/roberta-base-squad2"
pipe = pipeline("question-answering", model=model_name) #idk what is this and if it ok for all the models or just deepset/roberta-base-squad2
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, is_decoder=True)

'''
# Save the model and tokenizer
local_model_directory="." # mention the localtion where you want to save the model
model.save_pretrained("local_model_directory")
tokenizer.save_pretrained("local_model_directory")

model = AutoModel.from_pretrained("local_model_directory")
tokenizer = AutoTokenizer.from_pretrained("local_model_directory")
'''
# Generate a response
inputs = tokenizer.encode("rephrase like a data analyst. what is MTD sales in Singapore", return_tensors="pt").to("cuda")
outputs = model.generate(inputs)
print(tokenizer.decode(outputs[0]))