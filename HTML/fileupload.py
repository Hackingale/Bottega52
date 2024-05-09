import os
from urllib import request
from flask import Flask, render_template

app = Flask(__name__)

# Define the directory to save the uploaded LLM files
UPLOAD_FOLDER = 'HTML/uploaded'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the default LLM model path
DEFAULT_LLM_MODEL_PATH = '/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0.gguf'

@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        # Retrieve each file using their corresponding names
        input_file = request.files['input_file']
        context_file = request.files['context_file']
        test_set_file = request.files['test_set_file']
        llm_file = request.files['llm_file']  # Retrieve the uploaded LLM file

        # Save each file with a unique name
        input_file.save(os.path.join(app.config['UPLOAD_FOLDER'], "InputData.xlsx"))
        context_file.save(os.path.join(app.config['UPLOAD_FOLDER'], "ContextData.xlsx"))
        test_set_file.save(os.path.join(app.config['UPLOAD_FOLDER'], "TestSetData.xlsx"))

        # Handle the uploaded LLM file
        if llm_file.filename != '':
            llm_filename = 'USERLLM'  # Set the default filename for the uploaded LLM file
            llm_file.save(os.path.join(app.config['UPLOAD_FOLDER'], llm_filename))
            model_path = os.path.join(app.config['UPLOAD_FOLDER'], llm_filename)
        else:
            model_path = DEFAULT_LLM_MODEL_PATH

        return render_template("Acknowledgement.html",
                               input_file_name="InputData.xlsx",
                               context_file_name="ContextData.xlsx",
                               test_set_file_name="TestSetData.xlsx",
                               model_path=model_path)  # Pass the model_path to the template

if __name__ == "__main__":
    app.run(debug=True)
