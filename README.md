<h1 align="center">
  <a href="https://cloudspam.net"><img src="https://media.discordapp.net/attachments/1122682710842937415/1245066359570956409/EmailToolsLogo.png?ex=66c57b28&is=66c429a8&hm=b60003c4cd4c5587b471545d4d68439e8840b5867243dd586fb5207ce22d99b7&=&format=webp&quality=lossless&width=652&height=652" alt="AutomatedEmailLogo" width="250"></a>
  <br>
  Email-Automation Service
  <br>

</h1>

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/) [![Flask Version](https://img.shields.io/badge/Flask-2.0.2-blue)](https://flask.palletsprojects.com/en/3.0.x/) [![Pandas Version](https://img.shields.io/badge/pandas-1.3.4-blue)](https://pandas.pydata.org/) [![SQLAlchemy Version](https://img.shields.io/badge/SQLAlchemy-1.4.25-blue)](https://www.sqlalchemy.org/) [![python-dotenv](https://img.shields.io/badge/python--dotenv-v0.19.2-blue)](https://pypi.org/project/python-dotenv/)

A modern and efficient service for detecting and managing email patterns for companies. This project is designed to seamlessly integrate with Google Sheets to streamline email automation tasks.
Documentation too long? Skip to <a href="#tldr">TLDR</a> for quick setup
</div>


<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#tldr">TLDR</a> •
  <a href="#license">License</a> •
  <a href="#credits">Credits</a>
</p>

## Key Features

- **Email Pattern Detection:** Automatically detects common email patterns based on provided data.
- **Google Sheets Integration:** Easily send and receive data from Google Sheets.
- **Pattern Management:** Ensures patterns are only added when valid and prevents overwriting verified patterns.
- **FREE API:** Provides a simple API for managing and querying email patterns.

## How To Use

Each api request requires data in form of a csv as payload. See <a href="#csv-formatting">CSV Formatting</a> for more details on format specifications.
You can either use the API with http requests (see <a href="#using-curl">Using Curl</a> for a detailed description) or access the API using a user friendly gui by directly integrating it in your Google Sheets documents. See <a href="#using-sheets">Using Sheets</a> for a quick guide on how to use an already functioning integration or <a href="#setting-up-sheets">Setting up Sheets</a> for a guide on how to integrate the api functionality into your Google Sheets document.
### CSV Formatting
They payload must be passed in a csv format.
The following columns must exist in the csv:
 * "Company" - [Use the Company name as used by LinkedIn]
 * "Domain" - [Company web domain in github.com format]
 * "Firstname" - [must not be empty!]
 * "Lastname" - [must not be empty!]
 * "Email" - [empty for `/getEmail`; must contain valid email for `/addEmailPattern`]

### Using Curl
You can directly send requests to the RestAPI to generate Emails based on already saved Patterns by using the `https://api.cloudspam.net/getEmail` endpoint.
This is an example to get Emails using curl:
```bash
curl -X POST -H "Content-Type: application/csv" --data "[your csv formatted content]" https://api.cloudspam.net/getEmail
```
##
In an attempt to keep the quality of the data in good condition, request to add Patterns using the `https://api.cloudspam.net/addEmailPattern` endpoint require a registered api key. As of now, you can not generate your own api key. (possibly coming soon)
This is an example to add Patterns using curl:

```bash
curl -X POST -H "Content-Type: application/csv" -H "X-API-KEY: your_api_key_here" --data "[your csv formatted content] https://api.cloudspam.net/addEmailPattern
```
### Setting up Sheets
#### Script Setup:
Go to the Extensions tab and select `Apps Script`
<a><img src="https://cdn.discordapp.com/attachments/1122682710842937415/1245135032612294727/image.png?ex=66c5125d&is=66c3c0dd&hm=31ecf39d53dea6e5d300e89dc4d603b1f618c4fcf2b28cb7ab960edb3ac7d1cb&" alt="Select AppScript" width="250"></a>

Simply copy the gs code from <a href="https://github.com/PuEnjoy/PCG-EmailAutomation/blob/main/appscript-setup.gs">appscript-setup.gs</a> into the empty code file. Save the project and refresh the Google Sheets page.
#### Sheet Template:
The following columns must exist in the sheet:
 * "Company"
 * "Domain"
 * "Firstname"
 * "Lastname"
 * "Email"

##### Add Email Template
The following is an example template ready for adding email patterns to the DB:
<a><img src="https://media.discordapp.net/attachments/1122682710842937415/1245142245074796544/image.png?ex=66c51914&is=66c3c794&hm=8c3dfed1544d0b0b3938c42ceb163096e22ca991c0b985c9582074a7b00a6db6&=&format=webp&quality=lossless&width=1410&height=229" alt="AddEmails Example Image" width="1200"></a>
Note that all rows containing a red cell will be skipped due to missing values.
The needed columns are retrieved by their name. The Location of those columns is irrelevant and other columns like `RandomColumn` from the example will be ignored. 

##### Get Email Template
The following is an example template ready to getting emails from the api:
<a><img src="https://cdn.discordapp.com/attachments/1122682710842937415/1245144064303566858/image.png?ex=66c51ac6&is=66c3c946&hm=5bf3abe370dbb27c94a23100ad61b684080931a446eeddd75d722e0bc422ffb6&" alt="GetEmails Example Image" width="1200"></a>
Note that that all rows containing a red cell will be skipped due to missing values.
Row 6 with the orang cell will also be ignored since an entry in the email column already exists for this row.
The needed columns are retrieved by their name. The Location of those columns is irrelevant and other columns like `RandomColumn` from the example will be ignored. 

### Using Sheets
If the Google Sheets integration was setup correctly you will see a new "Emails" tab:
<a><img src="https://media.discordapp.net/attachments/1122682710842937415/1245136992014958746/image.png?ex=6657a7b0&is=66565630&hm=666078fffdba7dc2e7f79ef8608b41baded836a2ab2697b0563ac4d0f981fa6d&=&format=webp&quality=lossless&width=634&height=302" alt="Select Emails Tab" width="250"></a>

`Add Emails to DB` will try to upload your current emails to the database to be processed
`Populate Emails Column` will try to find matching email patterns and generate the missing emails for you (if a pattern is known).

## TLDR
Long story short: If you are only interested in getting email adresses you can copy this template:
<a href="https://docs.google.com/spreadsheets/d/1i062wTn-4YQWMYSg_qPwagylFiOnTsJ-ylSNPy8gzSA/edit?usp=sharing">Google Sheets Email Automation Template</a> and have a quick glanz at <a href="#using-sheets">Using Sheets.</a>
Note that using this template you can only populate your sheet data with emails for Companies with already known patterns. This will most likely not result in many matches. To add your own Company patterns you will need to read the documentation and either host your own copy of this automation service or aquire an API-Key (coming soon).
### Prerequisites

- Python 3.11
- Flask 2.0.2
- Pandas 1.3.4
- SQLAlchemy 1.4.25

## License

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

### Credits

Tobias Kregelin
[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)](https://linkedin.com/in/tobias-kregelin-26a638271) [![Github](https://img.shields.io/badge/Github-121013?logo=github&logoColor=white)](https://github.com/PuEnjoy)
