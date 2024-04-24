from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        # Retrieve each file using their corresponding names
        input_file = request.files['input_file']
        context_file = request.files['context_file']
        test_set_file = request.files['test_set_file']

        # Save each file with a unique name
        input_file.save("InputData.xlsx")
        context_file.save("ContextData.xlsx")
        test_set_file.save("TestSetData.xlsx")

        return render_template("Acknowledgement.html",
                               input_file_name="InputData.xlsx",
                               context_file_name="ContextData.xlsx",
                               test_set_file_name="TestSetData.xlsx")


if __name__ == '__main__':
    app.run(debug=True)
