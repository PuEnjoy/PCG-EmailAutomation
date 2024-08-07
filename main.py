#   ______                 _ _                 _                        _   _             
#  |  ____|               (_) |     /\        | |                      | | (_)            
#  | |__   _ __ ___   __ _ _| |    /  \  _   _| |_ ___  _ __ ___   __ _| |_ _  ___  _ __  
#  |  __| | '_ ` _ \ / _` | | |   / /\ \| | | | __/ _ \| '_ ` _ \ / _` | __| |/ _ \| '_ \ 
#  | |____| | | | | | (_| | | |  / ____ \ |_| | || (_) | | | | | | (_| | |_| | (_) | | | |
#  |______|_| |_| |_|\__,_|_|_| /_/    \_\__,_|\__\___/|_| |_| |_|\__,_|\__|_|\___/|_| |_|
                                                                                        

# Author: Tobias Kregelin
# Visit the official github page: https://github.com/PuEnjoy/PCG-EmailAutomation

#========================Start of main.py code============================================
import logging
import os
from flask import Flask, request, jsonify
import pandas as pd
from database_setup import Base, engine, Session, EmailPattern
from io import StringIO


#This requires the environment varible API_KEYS to be set
API_KEY = os.environ.get('API_KEY')

#Character replacement:
#TODO more special characters like é 
char_map = {
    'ä': 'ae',
    'ö': 'oe',
    'ü': 'ue',
    'ß': 'ss',
    'Ä': 'ae',
    'Ö': 'oe',
    'Ü': 'ue'
}

# Initialize Flask application
app = Flask(__name__)

# Function to check api key
def check_api_key(api_key):
    return str(api_key) == str(API_KEY)

# Ensure database is set up
Base.metadata.create_all(engine)
session = Session()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to replace special characters like ä with ae
def replace_characters(string: str) -> str:
    for char, replacement in char_map.items():
        string = string.replace(char, replacement)
    return string

@app.route('/addEmailPattern', methods=['POST'])
def add_email_pattern():
    # api_key = request.headers.get('X-API-KEY')
    # if not check_api_key(api_key):
    #     return jsonify({"error": "Unauthorized"}), 401
    
    csv_data = request.data.decode('utf-8')

    try:
        data = pd.read_csv(StringIO(csv_data))
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CSV data: {e}")
        return jsonify({"error": "Malformed CSV data"}), 400
    
    #TODO check if domain can be removed from required_columns
    required_columns = ['Company', 'Domain', 'Firstname', 'Lastname', 'Email']

    valid_rows_counter = 0
    valid_patterns_counter = 0
    for _, row in data.iterrows():
        if any(pd.isna(row[col]) for col in required_columns):
            continue
        valid_rows_counter += 1
        company_name = row['Company']
        domain = row['Domain']
        firstname = row['Firstname']
        lastname = row['Lastname']
        email = str(row['Email'])
        #Replace all special characters before processing
        firstname = replace_characters(firstname)
        lastname = replace_characters(lastname)

        smart_domain = email.split('@')[1]

        pattern = detect_email_pattern(firstname, lastname, email, domain, smart_domain)
        if pattern != "unknown":
            valid_patterns_counter += 1
            save_pattern(company_name, domain, smart_domain, pattern)
    
    return f'Total of {valid_rows_counter} valid rows scanned and {valid_patterns_counter} patterns detected.'



def detect_email_pattern(firstname, lastname, email, domain, smart_domain):
    email = str(email)
    patterns = {
        # Voller name
        f"{firstname}.{lastname}@{domain}": "{firstname}.{lastname}@{domain}",
        f"{firstname}{lastname}@{domain}": "{firstname}{lastname}@{domain}",
        f"{firstname}-{lastname}@{domain}": "{firstname}-{lastname}@{domain}",
        f"{firstname}_{lastname}@{domain}": "{firstname}_{lastname}@{domain}",
        f"{firstname}@{domain}": "{firstname}@{domain}", #Nur firstname
        f"{lastname}@{domain}": "{lastname}@{domain}", #Nur Nachname
        # 1. Buchstabe firstname, voller nachname
        f"{firstname[0]}.{lastname}@{domain}": "{firstname[0]}.{lastname}@{domain}",
        f"{firstname[0]}{lastname}@{domain}": "{firstname[0]}{lastname}@{domain}",
        f"{firstname[0]}-{lastname}@{domain}": "{firstname[0]}-{lastname}@{domain}",
        f"{firstname[0]}_{lastname}@{domain}": "{firstname[0]}_{lastname}@{domain}",
        # Voller firstname, 1. Buchstabe nachname
        f"{firstname}.{lastname[0]}@{domain}": "{firstname}.{lastname[0]}@{domain}",
        f"{firstname}{lastname[0]}@{domain}": "{firstname}{lastname[0]}@{domain}",
        f"{firstname}-{lastname[0]}@{domain}": "{firstname}-{lastname[0]}@{domain}",
        f"{firstname}_{lastname[0]}@{domain}": "{firstname}_{lastname[0]}@{domain}",
        # 1. Buchstabe firstname, 1. Buchstabe nachname
        f"{firstname[0]}.{lastname[0]}@{domain}": "{firstname[0]}.{lastname[0]}@{domain}",
        f"{firstname[0]}{lastname[0]}@{domain}": "{firstname[0]}{lastname[0]}@{domain}",
        f"{firstname[0]}-{lastname[0]}@{domain}": "{firstname[0]}-{lastname[0]}@{domain}",
        f"{firstname[0]}_{lastname[0]}@{domain}": "{firstname[0]}_{lastname[0]}@{domain}",

        # Using smart domains ==============================

        f"{firstname}.{lastname}@{smart_domain}": "{firstname}.{lastname}@{smart_domain}",
        f"{firstname}{lastname}@{smart_domain}": "{firstname}{lastname}@{smart_domain}",
        f"{firstname}-{lastname}@{smart_domain}": "{firstname}-{lastname}@{smart_domain}",
        f"{firstname}_{lastname}@{smart_domain}": "{firstname}_{lastname}@{smart_domain}",
        f"{firstname}@{smart_domain}": "{firstname}@{smart_domain}", #Nur firstname
        f"{lastname}@{smart_domain}": "{lastname}@{smart_domain}", #Nur Nachname
        # 1. Buchstabe firstname, voller nachname
        f"{firstname[0]}.{lastname}@{smart_domain}": "{firstname[0]}.{lastname}@{smart_domain}",
        f"{firstname[0]}{lastname}@{smart_domain}": "{firstname[0]}{lastname}@{smart_domain}",
        f"{firstname[0]}-{lastname}@{smart_domain}": "{firstname[0]}-{lastname}@{smart_domain}",
        f"{firstname[0]}_{lastname}@{smart_domain}": "{firstname[0]}_{lastname}@{smart_domain}",
        # Voller firstname, 1. Buchstabe nachname
        f"{firstname}.{lastname[0]}@{smart_domain}": "{firstname}.{lastname[0]}@{smart_domain}",
        f"{firstname}{lastname[0]}@{smart_domain}": "{firstname}{lastname[0]}@{smart_domain}",
        f"{firstname}-{lastname[0]}@{smart_domain}": "{firstname}-{lastname[0]}@{smart_domain}",
        f"{firstname}_{lastname[0]}@{smart_domain}": "{firstname}_{lastname[0]}@{smart_domain}",
        # 1. Buchstabe firstname, 1. Buchstabe nachname
        f"{firstname[0]}.{lastname[0]}@{smart_domain}": "{firstname[0]}.{lastname[0]}@{smart_domain}",
        f"{firstname[0]}{lastname[0]}@{smart_domain}": "{firstname[0]}{lastname[0]}@{smart_domain}",
        f"{firstname[0]}-{lastname[0]}@{smart_domain}": "{firstname[0]}-{lastname[0]}@{smart_domain}",
        f"{firstname[0]}_{lastname[0]}@{smart_domain}": "{firstname[0]}_{lastname[0]}@{smart_domain}",
   
    }

    for pattern, generalized in patterns.items():
        if email.lower() == pattern.lower():
            return generalized
    
    return "unknown"

def save_pattern(company_name, domain, smart_domain, pattern):
    existing_pattern = session.query(EmailPattern).filter_by(company_name=company_name, domain=domain, smart_domain=smart_domain).first()
    if not existing_pattern:
        new_pattern = EmailPattern(company_name=company_name, domain=domain, smart_domain=smart_domain, pattern=pattern)
        session.add(new_pattern)
        session.commit()
    elif existing_pattern.status != "verified":
        existing_pattern.pattern = pattern
        session.commit()

@app.route('/getEmail', methods=['POST'])
def get_email():
    csv_data = request.data.decode('utf-8')
    data = pd.read_csv(StringIO(csv_data))
    
    required_columns = ['Company', 'Domain', 'Firstname', 'Lastname']

    response = []
    for _, row in data.iterrows():
        if any(pd.isna(row[col]) for col in required_columns):
            continue
        company_name = row['Company']
        domain = row['Domain']
        firstname = row['Firstname']
        lastname = row['Lastname']
        #Replace all special characters before processing
        firstname = replace_characters(firstname)
        lastname = replace_characters(lastname)

        email_pattern = session.query(EmailPattern).filter_by(company_name=company_name).first()
        if email_pattern:
            generalized_pattern = email_pattern.pattern
            email = generalized_pattern.format(firstname=firstname, lastname=lastname, domain=domain, smart_domain=email_pattern.smart_domain, firstname_0=firstname[0])
            response.append({
                'Company': company_name,
                'Domain': domain,
                'Firstname': firstname,
                'Lastname': lastname,
                'Email': email
            })
        else:
            response.append({
                'Company': company_name,
                'Domain': domain,
                'Firstname': firstname,
                'Lastname': lastname,
                'Email': None
            })

    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

#========================End of main.py code============================================

#   _      _                        
#  | |    (_)                     _ 
#  | |     _  ___ ___ _ __  ___  (_)
#  | |    | |/ __/ _ \ '_ \/ __|    
#  | |____| | (_|  __/ | | \__ \  _ 
#  |______|_|\___\___|_| |_|___/ (_)
                                  
# [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

# This work is licensed under a
# [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

# [![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

# [cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
# [cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
# [cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
