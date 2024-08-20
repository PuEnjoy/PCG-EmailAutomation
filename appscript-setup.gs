/*
  ______                 _ _                 _                        _   _             
 |  ____|               (_) |     /\        | |                      | | (_)            
 | |__   _ __ ___   __ _ _| |    /  \  _   _| |_ ___  _ __ ___   __ _| |_ _  ___  _ __  
 |  __| | '_ ` _ \ / _` | | |   / /\ \| | | | __/ _ \| '_ ` _ \ / _` | __| |/ _ \| '_ \ 
 | |____| | | | | | (_| | | |  / ____ \ |_| | || (_) | | | | | | (_| | |_| | (_) | | | |
 |______|_| |_| |_|\__,_|_|_| /_/    \_\__,_|\__\___/|_| |_| |_|\__,_|\__|_|\___/|_| |_|
                                                                                        

Author: Tobias Kregelin
Visit the official github page: https://github.com/PuEnjoy/PCG-EmailAutomation

*/

function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Emails')
    .addItem('📤 POST Emails', 'sendDataToAPI')
    .addItem('📥 GET Emails', 'populateEmails')
    .addToUi();
}

//This function is only required when using the addEmailPattern api
//function getApiKey() {
//    //The API key has to be set in the scriptProperties settings unter Project-Settings
//  var scriptProperties = PropertiesService.getScriptProperties();
//  return scriptProperties.getProperty('API_KEY');
//}

//This function will take all your entries from the sheet, format them and send them to the api endpoint which will detect the email pattern and add it to the database
function sendDataToAPI() {
//  var apiKey = getApiKey();
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  var csvRows = [];
  var columnsToExtract = ["Company", "Domain", "Firstname", "Lastname", "Email"];
  var columnIndexes = columnsToExtract.map(col => headers.indexOf(col));
  
  // Add headers to CSV
  csvRows.push(columnsToExtract.join(","));
  
  for (var i = 1; i < data.length; i++) {
    var row = data[i];

    // Check if all required columns have values
    var includeRow = columnIndexes.every(index => row[index] && row[index].toString().trim() !== "");
    if (!includeRow) continue;

    // Strip commas from data and join columns into CSV format
    var csvRow = columnIndexes.map(index => row[index].toString().replace(/,/g, '')).join(",");
    csvRows.push(csvRow);
  }
  
  var csvContent = csvRows.join("\n");

  var apiUrl = 'https://api.cloudspam.net/addEmailPattern'; // Replace with actual API endpoint
  var options = {
    method: 'post',
    contentType: 'application/csv',
    payload: csvContent,
    headers: {
//      'X-API-KEY': apiKey
    }
  };
  Logger.log(options.payload);
  var response = UrlFetchApp.fetch(apiUrl, options);
  Logger.log(response.getContentText());
}

//This Function will send and api request to the getEmail Endpoint and tries to populate all empty fields in the Email column
function populateEmails() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var dataRange = sheet.getDataRange();
  var data = dataRange.getValues();
  var headers = data[0];
  var CompanyIndex = headers.indexOf("Company");
  var domainIndex = headers.indexOf("Domain");
  var FirstnameIndex = headers.indexOf("Firstname");
  var LastnameIndex = headers.indexOf("Lastname");
  var emailIndex = headers.indexOf("Email");

  var csvRows = [];
  csvRows.push("Company,Domain,Firstname,Lastname");

  for (var i = 1; i < data.length; i++) {
    var row = data[i];

    // Check if Company, Firstname, Lastname have values and Email does not
    if (row[CompanyIndex] && row[FirstnameIndex] && row[LastnameIndex] && !row[emailIndex]) {
      var csvRow = [
        row[CompanyIndex].toString().replace(/,/g, ''),
        row[domainIndex].toString().replace(/,/g, ''),
        row[FirstnameIndex].toString().replace(/,/g, ''),
        row[LastnameIndex].toString().replace(/,/g, '')
      ].join(",");
      csvRows.push(csvRow);
    }
  }

  var csvContent = csvRows.join("\n");

  var apiUrl = 'https://api.cloudspam.net/getEmail'; // Replace with actual API endpoint
  var options = {
    method: 'post',
    contentType: 'application/csv',
    payload: csvContent
  };

  var response = UrlFetchApp.fetch(apiUrl, options);
  var emails = JSON.parse(response.getContentText());

  // Update the sheet with the received emails
  for (var i = 1; i < data.length; i++) {
    for (var j = 0; j < emails.length; j++) {
      if (data[i][CompanyIndex] == emails[j].Company &&
          data[i][domainIndex] == emails[j].Domain &&
          data[i][FirstnameIndex] == emails[j].Firstname &&
          data[i][LastnameIndex] == emails[j].Lastname) {
        sheet.getRange(i + 1, emailIndex + 1).setValue(emails[j].Email);
      }
    }
  }
}

/*
  _      _                        
 | |    (_)                     _ 
 | |     _  ___ ___ _ __  ___  (_)
 | |    | |/ __/ _ \ '_ \/ __|    
 | |____| | (_|  __/ | | \__ \  _ 
 |______|_|\___\___|_| |_|___/ (_)
                                  
[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

*/