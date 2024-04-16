import json

import pandas as pd
import requests
from bs4 import BeautifulSoup


def extract_data_from_website(url):
    try:
        url = 'https://www.' + url
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all the text from the HTML and strip unnecessary spaces
            all_text = '\n'.join(line.strip() for line in soup.get_text(separator='\n').splitlines() if line.strip())

            return all_text
        else:
            return None
    except Exception as e:
        print("An error occurred while extracting data from", url)
        print(e)
        return None

def create_json_with_website_data(company_names, output_file):
    data = {}
    for company_name in company_names[:10]:
        extracted_data = extract_data_from_website(company_name)
        if extracted_data:
            data[company_name] = extracted_data

    try:
        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print("JSON file with website data created:", output_file)
    except Exception as e:
        print("An error occurred while writing JSON file:", e)

def contextexcel_to_text(xlsx_file):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_excel(xlsx_file)

    players = df['Player']
    can_buy = df['Can they buy the solution?']
    influence_decision = df['Can they influence the buying decision?']
    notes = df['Notes']

    context_prompt = ""
    # Loop through the rows and access data
    for index, row in df.iterrows():
        player = row['Player']
        can_buy_solution = row['Can they buy the solution?']
        influence_buying_decision = row['Can they influence the buying decision?']
        player_notes = row['Notes']

        # Perform further processing or analysis here
        context_prompt += f"Player: {player}, Can Buy: {can_buy_solution}, Influence Decision: {influence_buying_decision}, Notes: {player_notes}\n"

    return context_prompt

def inputexcel_to_text(xlsx_file):
    df = pd.read_excel(xlsx_file)

    # Iterate over each row in the DataFrame and extract the desired columns
    result = []
    for index, row in df.iterrows():
        contact_job_title = row['Contact Job Title']
        company = row['Company / Account']

        # Append the extracted information as a dictionary to the result list
        result.append({
            'Contact Job Title': contact_job_title,
            'Company / Account': company
        })

    # Print the result list (or do whatever you want with it)
    return result

def prompt_creation(input, context):
    prompt = "I will provide you a list of Players in the context of the real estate market. Each player is characterized by these following attributes: Player (the role of the figure in the market), Can they buy the solution? (are they able to buy the house/estate), Can they influence the buying decision?, Notes(additional  info regarding the player's role)\n"
    prompt += contextexcel_to_text(context) + "\n"
    prompt += "Now I will provide a list of people, every pair of curly brackets represents a person. The first element of the pair is the Job Title of the contact, and the second element is the Company or Account for which the person works for. For example, {'Contact Job Title': 'Chief of operations', 'Company / Account': 'Urban Campus'} means that the person is the Chief of operations and his company is Urban Campus. The list of people is as follows:\n"
    prompt += str(inputexcel_to_text(input)) + "\n"
    prompt += "Now I will provide you a text extracted from the website of the first company in the list of people. The text is as follows: \n"
    prompt += "Constructora pionera en innovaci\u00f3n, tecnolog\u00eda y sostenibilidad - ACR\nSaltar al contenido\nSomos\nLideramos\nAbrir el men\u00fa\nColaboraci\u00f3n radical\nInnovaci\u00f3n\nSostenibilidad\nIndustrializaci\u00f3n\nLean Construction\nRehabilitaci\u00f3n ecoeficiente\nConstruimos\nAbrir el men\u00fa\nProyectos\nCrecemos\nAbrir el men\u00fa\nPersonas\nOfertas de empleo\nComunicamos\nAbrir el men\u00fa\nActualidad\nContacto\nProveedores\nClientes\nCandidaturas\nCanal \u00c9tico\nCastellano\nEnglish\nCONSTRUIMOS\nPENSANDO\nEN TODO.\nEN TODOS\nEdificio de flex living en Valdebebas\nConstrucci\u00f3n del edificio industrializado h\u00edbrido m\u00e1s grande de Espa\u00f1a con el sistema CREE Buildings, que contar\u00e1 con 500 apartamentos.\n1\n2\n3\n4\n\u203a\nCreemos que el futuro necesita un sector cada vez m\u00e1s\nresponsable,\ninnovador\ny\nsostenible.\nSABER M\u00c1S DE ACR\nInnovamos para adaptarnos a las nuevas necesidades y responder a los retos del momento.\nVer m\u00e1s\nTrabajamos para liderar la transformaci\u00f3n de la construcci\u00f3n hacia una industria cada vez m\u00e1s responsable, innovadora y sostenible.\nVer m\u00e1s\nBuscamos la satisfacci\u00f3n de nuestros clientes gracias al modelo Lean Construction y a un sentido de la colaboraci\u00f3n radical que vertebra nuestra estrategia, engloba a todos nuestros colaboradores y se refleja en todos nuestros proyectos.\nVer m\u00e1s\nResidencial\n121 viviendas industrializadas Stay by Kronos\nProyecto industrializado con Steel framing, de 121 viviendas para build to rent en Torrej\u00f3n de Ardoz.\nVER M\u00c1S\nM\u00c1S PROYECTOS\n1\n2\n3\n\u2026\n5\n\u203a\nPor qu\u00e9\nlideramos\nLean Construction\nConstrucci\u00f3n industrializada\nRehabilitaci\u00f3n ecoeficiente\nDesarrolla tu carrera en\nBuscamos personas con iniciativa, eficientes y productivas, que tengan predisposici\u00f3n para el trabajo en equipo, capacidad de adaptaci\u00f3n al cambio y orientaci\u00f3n al cliente. Si crees en entornos de colaboraci\u00f3n, din\u00e1micos e innovadores, no sigas buscando. \u00a1ACR es tu sitio!\nPOR QU\u00c9 TRABAJAR EN ACR\nVER OPORTUNIDADES\nActualidad ACR\nACR construir\u00e1 para DAZIA CAPITAL y AERMONT CAPITAL el edificio industrializado h\u00edbrido m\u00e1s grande de Espa\u00f1a\nEl proyecto, ubicado en el barrio madrile\u00f1o de Valdebebas, contar\u00e1 con 500 apartamentos.\nSer\u00e1 uno de los edificios m\u00e1s grandes del mundo construido con el sistema h\u00edbrido de madera y hormig\u00f3n de CREE Buildings, y el segundo mayor de Europa.\nCon planta baja m\u00e1s 7 alturas, estar\u00e1 entre los edificios industrializados m\u00e1s altos de nuestro pa\u00eds.\nTerminamos en solo 14 d\u00edas la estructura del primer edificio industrializado h\u00edbrido de Espa\u00f1a\nDise\u00f1o de TdB Arquitectura, el hotel B&B de Tres Cantos, que estamos construyendo junto a Casais avanza a un ritmo vertiginoso. Y es que en solo 14 d\u00edas, adem\u00e1s de la estructura h\u00edbrida de madera y hormig\u00f3n del sistema de CREE Buildings, tambi\u00e9n ha quedado montada la fachada, con acabado exterior incluido con marcos y vidrios, y ya est\u00e1n distribuidos por las plantas los ba\u00f1os industrializados y los kits de tuber\u00edas para las instalaciones.\nVER\nM\u00c1S\nSuscr\u00edbete a nuestra newsletter\nY recibe todas las novedades. En ACR estamos continuamente transform\u00e1ndonos y super\u00e1ndonos con cada proyecto, as\u00ed que siempre tenemos algo nuevo para compartir.\nEmail\nConsent\nAcepto\nla pol\u00edtica de privacidad\nENVIA\nCopyright\n\u00a9 ACR - Grupo ACR 2021\nMen\u00fa pie\nAviso legal\nPol\u00edtica de privacidad\nPol\u00edtica de cookies\nRRSS\nUtilizamos cookies propias y de terceros para fines anal\u00edticos. Clica\nAQU\u00cd\npara m\u00e1s informaci\u00f3n.\nPuedes aceptar todas las cookies pulsando el bot\u00f3n \"Aceptar\" o configurarlas o rechazar su uso clicando\naqu\u00ed\n.\nAceptar\nManage consent\nCerrar\nPrivacy Overview\nThis website uses cookies to improve your experience while you navigate through the website. Out of these, the cookies that are categorized as necessary are stored on your browser as they are essential for the working of basic functionalities of the website. We also use third-party cookies that help us analyze and understand how you use this website. These cookies will be stored in your browser only with your consent. You also have the option to opt-out of these cookies. But opting out of some of these cookies may affect your browsing experience.\nNecessary\nNecessary\nSiempre activado\nNecessary cookies are absolutely essential for the website to function properly. These cookies ensure basic functionalities and security features of the website, anonymously.\nCookie\nDuraci\u00f3n\nDescripci\u00f3n\ncookielawinfo-checkbox-analytics\n11 months\nThis cookie is set by GDPR Cookie Consent plugin. The cookie is used to store the user consent for the cookies in the category \"Analytics\".\ncookielawinfo-checkbox-functional\n11 months\nThe cookie is set by GDPR cookie consent to record the user consent for the cookies in the category \"Functional\".\ncookielawinfo-checkbox-necessary\n11 months\nThis cookie is set by GDPR Cookie Consent plugin. The cookies is used to store the user consent for the cookies in the category \"Necessary\".\ncookielawinfo-checkbox-others\n11 months\nThis cookie is set by GDPR Cookie Consent plugin. The cookie is used to store the user consent for the cookies in the category \"Other.\ncookielawinfo-checkbox-performance\n11 months\nThis cookie is set by GDPR Cookie Consent plugin. The cookie is used to store the user consent for the cookies in the category \"Performance\".\nviewed_cookie_policy\n11 months\nThe cookie is set by the GDPR Cookie Consent plugin and is used to store whether or not user has consented to the use of cookies. It does not store any personal data.\nFunctional\nFunctional\nFunctional cookies help to perform certain functionalities like sharing the content of the website on social media platforms, collect feedbacks, and other third-party features.\nPerformance\nPerformance\nPerformance cookies are used to understand and analyze the key performance indexes of the website which helps in delivering a better user experience for the visitors.\nAnalytics\nAnalytics\nAnalytical cookies are used to understand how visitors interact with the website. These cookies help provide information on metrics the number of visitors, bounce rate, traffic source, etc.\nAdvertisement\nAdvertisement\nAdvertisement cookies are used to provide visitors with relevant ads and marketing campaigns. These cookies track visitors across websites and collect information to provide customized ads.\nOthers\nOthers\nOther uncategorized cookies are those that are being analyzed and have not been classified into a category as yet.\nGUARDAR Y ACEPTAR"
    prompt += "Based on the information provided using the list of players and the company, please generate a text that reports the following information: Company, #Contacts, Type of Company, Sub-type, Buyer (yes/no), Influencer (yes/no), Target Market (true/false), Website reachable (true/false)\n"
    return prompt

# Call the function and store the return value
return_string = prompt_creation("InputData.xlsx", "Categories.xlsx")

# Specify the file path
file_path = "output.txt"

# Write the return string to a text file
with open(file_path, "w") as file:
    file.write(return_string)

print("Return string has been written to", file_path)
