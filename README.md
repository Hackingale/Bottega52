# Automated Market Analysis with Large Language Model (LLM)

## Authors
- Alessandro Marina
- Marco Laurenzi

## Overview
This project leverages a Large Language Model (LLM) to automate the identification of company roles within a market. Traditional market analysis methods are effective but time-consuming and labor-intensive. Our solution streamlines this process by quickly processing large volumes of text, ensuring high accuracy and efficiency. 

## Features
- **Automated Data Analysis**: Quickly processes large volumes of text.
- **High Accuracy**: Ensures accurate classification of company roles.
- **Efficiency**: Reduces manual labor, allowing businesses to focus on strategic decision-making.

## Pipeline Stages
1. **Web Scraping**: Collects data from various sources.
2. **Classification**: Uses the LLM to classify companies based on their roles.
3. **Output Validation**: Validates the output against a test set (optional).

## Requirements
- Python 3.x
- Flask
- Other dependencies listed in `requirements.txt`

## Getting Started

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/automated-market-analysis.git
   cd automated-market-analysis
2. install the required dependencies:
   ```sh
   pip install -r requirements.txt

## Running the application 
1. Start the application by running the main script: pyhton main.py
2. Open your web browser and connect to the default address:
   ```sh
	http://127.0.0.1:5000

## Using the Application:
To use the application, upload the following files

	•	List of Companies: A CSV file containing the list of companies to be classified.
	•	LLM (Optional): The large language model file.
	•	Test Set File (Optional): A file to compare the results and validate the model’s performance.
	•	Context File: A file describing the roles of the agents in the market.

## What the Application Does

The application automates the process of market analysis by:

	1.	Scraping data from various sources.
	2.	Using the LLM to classify the roles of companies within a market.
	3.	Validating the output to ensure high accuracy.

By automating these tasks, the application helps businesses gain valuable insights with minimal manual intervention, thereby enhancing strategic decision-making and competitiveness.

## License

This project is licensed under the MIT License.

## Acknowledgments

Special thanks to all contributors and supporters of this project.








