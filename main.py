import logging
import os
from flask import Flask, request, jsonify
import pandas as pd
from database_setup import Base, engine, Session, EmailPattern
from io import StringIO

# Initialize Flask application
app = Flask(__name__)

# Ensure database is set up
Base.metadata.create_all(engine)
session = Session()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/addEmailPattern', methods=['POST'])
def add_email_pattern():
    csv_data = request.data.decode('utf-8')

    try:
        data = pd.read_csv(StringIO(csv_data))
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CSV data: {e}")
        print(csv_data)
        return jsonify({"error": "Malformed CSV data"}), 400
    
    for _, row in data.iterrows():
        company_name = row['Firma']
        domain = row['Domain']
        vorname = row['Vorname']
        zuname = row['Zuname']
        email = row['Email']

        pattern = detect_email_pattern(vorname, zuname, email, domain)
        save_pattern(company_name, domain, pattern)
    
    return 'Email patterns processed and saved.'

def detect_email_pattern(vorname, zuname, email, domain):
    email = str(email)
    patterns = {
        f"{vorname}.{zuname}@{domain}": "{vorname}.{zuname}@{domain}",
        f"{vorname}@{domain}": "{vorname}@{domain}",
        f"{zuname}@{domain}": "{zuname}@{domain}",
        f"{vorname[0]}.{zuname}@{domain}": "{vorname[0]}.{zuname}@{domain}",
        f"{vorname[0]}{zuname}@{domain}": "{vorname[0]}{zuname}@{domain}"
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
    else:
        existing_pattern.pattern = pattern
        session.commit()

@app.route('/getEmail', methods=['POST'])
def get_email():
    csv_data = request.data.decode('utf-8')
    data = pd.read_csv(StringIO(csv_data))
    
    response = []
    for _, row in data.iterrows():
        company_name = row['Firma']
        domain = row['Domain']
        vorname = row['Vorname']
        zuname = row['Zuname']

        email_pattern = session.query(EmailPattern).filter_by(company_name=company_name, domain=domain).first()
        if email_pattern:
            generalized_pattern = email_pattern.pattern
            email = generalized_pattern.format(vorname=vorname, zuname=zuname, domain=domain, vorname_0=vorname[0])
            response.append({
                'Firma': company_name,
                'Domain': domain,
                'Vorname': vorname,
                'Zuname': zuname,
                'Email': email
            })
        else:
            response.append({
                'Firma': company_name,
                'Domain': domain,
                'Vorname': vorname,
                'Zuname': zuname,
                'Email': 'Pattern not found'
            })

    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)