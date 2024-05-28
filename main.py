import logging
import os
from flask import Flask, request, jsonify
import pandas as pd
from database_setup import Base, engine, Session, EmailPattern
from io import StringIO


#This requires the environment varible API_KEYS to be set
API_KEY = os.environ.get('API_KEY')

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

@app.route('/addEmailPattern', methods=['POST'])
def add_email_pattern():
    api_key = request.headers.get('X-API-KEY')
    if not check_api_key(api_key):
        return jsonify({"error": "Unauthorized"}), 401
    
    csv_data = request.data.decode('utf-8')

    try:
        data = pd.read_csv(StringIO(csv_data))
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CSV data: {e}")
        return jsonify({"error": "Malformed CSV data"}), 400
    
    for _, row in data.iterrows():
        company_name = row['Company']
        domain = row['Domain']
        firstname = row['Firstname']
        lastname = row['Lastname']
        email = row['Email']

        pattern = detect_email_pattern(firstname, lastname, email, domain)
        if pattern != "unknown":
            save_pattern(company_name, domain, pattern)
    
    return 'Email patterns processed and saved.'

def detect_email_pattern(firstname, lastname, email, domain):
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
    }

    for pattern, generalized in patterns.items():
        if email.lower() == pattern.lower():
            return generalized
    
    return "unknown"

def save_pattern(company_name, domain, pattern):
    existing_pattern = session.query(EmailPattern).filter_by(company_name=company_name, domain=domain).first()
    if not existing_pattern:
        new_pattern = EmailPattern(company_name=company_name, domain=domain, pattern=pattern)
        session.add(new_pattern)
        session.commit()
    elif existing_pattern.status != "verified":
        existing_pattern.pattern = pattern
        session.commit()

@app.route('/getEmail', methods=['POST'])
def get_email():
    csv_data = request.data.decode('utf-8')
    data = pd.read_csv(StringIO(csv_data))
    
    response = []
    for _, row in data.iterrows():
        company_name = row['Company']
        domain = row['Domain']
        firstname = row['Firstname']
        lastname = row['Lastname']

        email_pattern = session.query(EmailPattern).filter_by(company_name=company_name, domain=domain).first()
        if email_pattern:
            generalized_pattern = email_pattern.pattern
            email = generalized_pattern.format(firstname=firstname, lastname=lastname, domain=domain, firstname_0=firstname[0])
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
                'Email': 'Pattern not found'
            })

    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)