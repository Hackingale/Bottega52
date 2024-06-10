import os
import base64
from flask import Flask, request, render_template, jsonify, send_from_directory

app = Flask(__name__)
project_root = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = '../HTML/uploaded'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the default LLM model path
DEFAULT_LLM_MODEL_PATH = '../HTML/uploaded/'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

latest_model_path = None
files_uploaded = False
companies_evaluated = 0
companies_scraped = False
output_provided = False
test_set_uploaded = False
output_downloaded = False
num_companies_scraped = 0
precision = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success', methods=['POST'])
def success():
    global latest_model_path, files_uploaded, test_set_uploaded
    if request.method == 'POST':
        # Retrieve each file using their corresponding names
        input_file = request.files['input_file']
        context_file = request.files['context_file']
        test_set_file = request.files['test_set_file']
        llm_file = request.files['llm_file']  # Retrieve the uploaded LLM file

        # Save each file with a unique name
        input_file.save(os.path.join(app.config['UPLOAD_FOLDER'], "InputData.xlsx"))
        context_file.save(os.path.join(app.config['UPLOAD_FOLDER'], "ContextData.xlsx"))

        # Handle the uploaded LLM file
        if llm_file.filename != '':
            llm_filename = 'USERLLM.gguf'  # Set the default filename for the uploaded LLM file
            llm_file.save(os.path.join(app.config['UPLOAD_FOLDER'], llm_filename))
            llm_filename = ''  # Reset the filename to an empty string
            latest_model_path = os.path.join(app.config['UPLOAD_FOLDER'], llm_filename)
        else:
            latest_model_path = DEFAULT_LLM_MODEL_PATH

        if test_set_file.filename != '':
            test_set_file.save(os.path.join(app.config['UPLOAD_FOLDER'], "TestSetData.xlsx"))
            test_set_uploaded = True
        else:
            test_set_uploaded = False
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

@app.route('/get_test_set_uploaded', methods=['GET'])
def get_test_set_uploaded():
    global test_set_uploaded
    return jsonify({"test_set_uploaded": test_set_uploaded})

@app.route('/provide_output', methods=['POST'])
def provide_output():
    global output_provided
    data = request.get_json()
    if 'file_name' not in data or 'file_data' not in data:
        return jsonify({"error": "Invalid payload"}), 400

    file_name = data['file_name']
    file_data = data['file_data']

    # Decode the file data
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    with open(file_path, 'wb') as f:
        f.write(base64.b64decode(file_data))

    output_provided = True
    return jsonify({"output_provided": output_provided})

@app.route('/check_output_provided', methods=['GET'])
def check_output_provided():
    global output_provided, precision, test_set_uploaded
    response = {"output_provided": output_provided}
    if test_set_uploaded and precision is not None:
        response["precision"] = precision
    return jsonify(response)

@app.route('/download_output', methods=['GET'])
def download_output():
    global output_downloaded
    output_downloaded = True
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'output.xlsx', as_attachment=True)

@app.route('/check_output_downloaded', methods=['GET'])
def check_output_downloaded():
    global output_downloaded
    return jsonify({"output_downloaded": output_downloaded})

@app.route('/provide_precision', methods=['POST'])
def provide_precision():
    global precision
    data = request.get_json()
    if 'precision' not in data:
        return jsonify({"error": "Invalid payload"}), 400

    precision = data['precision']
    return jsonify({"precision": precision})

if __name__ == "__main__":
    app.run(debug=True)