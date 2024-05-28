import os
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)
project_root = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = '../HTML/uploaded'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the default LLM model path
DEFAULT_LLM_MODEL_PATH = '/Users/alessandrom/Library/Application Support/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0.gguf'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

latest_model_path = None
files_uploaded = False
companies_evaluated = 0
companies_scraped = False
num_companies_scraped = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success', methods=['POST'])
def success():
    global latest_model_path, files_uploaded
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
            llm_filename = 'USERLLM.gguf'  # Set the default filename for the uploaded LLM file
            llm_file.save(os.path.join(app.config['UPLOAD_FOLDER'], llm_filename))
            llm_filename = ''  # Reset the filename to an empty string
            latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], llm_filename)
        else:
            latest_model_path = DEFAULT_LLM_MODEL_PATH
        files_uploaded = True

        return render_template("Acknowledgement.html",
                               input_file_name="InputData.xlsx",
                               context_file_name="ContextData.xlsx",
                               test_set_file_name="TestSetData.xlsx",
                               model_path=latest_model_path)  # Pass the model_path to the template

@app.route('/get_model_path', methods=['GET'])
def get_model_path():
    global latest_model_path, files_uploaded
    return jsonify({"model_path": latest_model_path, "files_uploaded": files_uploaded})

@app.route('/increment_counter', methods=['POST'])
def increment_counter():
    global companies_evaluated
    companies_evaluated += 1
    return jsonify({"companies_evaluated": companies_evaluated})

@app.route('/companies_scraped', methods=['POST'])
def set_companies_scraped():
    global companies_scraped, num_companies_scraped
    data = request.get_json()
    num_companies_scraped = data.get('num_companies_scraped', 0)
    companies_scraped = True
    return jsonify({"companies_scraped": companies_scraped})

@app.route('/check_companies_scraped', methods=['GET'])
def check_companies_scraped():
    global companies_scraped
    return jsonify({"companies_scraped": companies_scraped})

@app.route('/get_evaluated_count', methods=['GET'])
def get_evaluated_count():
    global companies_evaluated, num_companies_scraped
    return jsonify({"companies_evaluated": companies_evaluated, "num_companies_scraped": num_companies_scraped})

if __name__ == "__main__":
    app.run(debug=True)
