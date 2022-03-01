#This script will run daily to create cards automatically
from time import sleep
import json
import requests
import datetime
import os
import sys
from dotenv import load_dotenv

#Use python-dotenv to enable the use of a .env file in place of standard OS environment vars
load_dotenv()

#Trello API authentication secrets
API_KEY = os.environ.get("TRELLO_KEY", default="No Key Found")
API_TOKEN = os.environ.get("TRELLO_TOKEN", default="No Token Found")
BOARD_ID = os.environ.get("TRELLO_BOARD", default="No Board ID Found")

if type(BOARD_ID) == str:
    if BOARD_ID.__len__() == 24:
        print("Board ID fetched successfully")
    else:
        print(f"Board ID contained an incorrect string: {BOARD_ID}")
        breakpoint()
else:
    print(f"Something has gone horribly wrong. BOARD_ID is {type(BOARD_ID)} (Should be <class 'str'>)")
    breakpoint()

#API token authorization payload for global use
payloadAuthToken = {'key': API_KEY, 'token': API_TOKEN}

#Trello API Endpoint
endpoint = "https://api.trello.com/1/"

#lists for global use
listListIds = []
listCards = []
listCardIds = []
listLabelIds = []
listCustomFields = []
listCustomFieldIds = []
listEpicOptions = []

#Get the Board's List IDs
def getListIds():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")

    #Formulate and send an HTTP request. Store the response and parse it as json.
    requestBody = payloadAuthToken
    requestUrl = f"{endpoint}boards/{BOARD_ID}/lists"
    response = requests.get(requestUrl, params=requestBody)
    response.raise_for_status()
    jsonResponse = response.json()
    
    #Extract {"id": "<class 'str'>", "name": "<class 'str'>"} from each object in jsonResponse and populate listListIds[]
    for i in range(len(jsonResponse)):
        tempDict = {'id': jsonResponse[i].get('id'), 'name': jsonResponse[i].get('name')}
        listListIds.append(tempDict)
        i += 1
    print(f"Found {len(listListIds)} Lists and extracted their Names and IDs.")

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return listListIds

#Get the Board's Cards
def getCards():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")
    
    #Formulate and send an HTTP request. Store the response and parse it as json.
    requestBody = payloadAuthToken
    requestUrl = f"{endpoint}boards/{BOARD_ID}/cards"
    response = requests.get(requestUrl, params=requestBody)
    response.raise_for_status()
    jsonResponse = response.json()

    #Populate listCards[] with the card info from jsonResponse
    listCards.clear()
    listCards.extend(jsonResponse)

    print(f"Found {len(listCards)} Cards.")


    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return listCards

#Get Card IDs from listCards[]
def getCardIds():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")

    #Iterate through listCards[] and populate listCardIds[] with the 'id' values
    listCardIds.clear()
    for i in range(len(listCards)):
        listCardIds.append(listCards[i].get('id'))
        i += 1

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return listCardIds

#Get the Board's Label IDs
def getLabelIds():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")
    
    #Formulate and send an HTTP request. Store the response and parse it as json.
    requestBody = payloadAuthToken
    requestUrl = f"{endpoint}boards/{BOARD_ID}/labels"
    response = requests.get(requestUrl, params=requestBody)
    response.raise_for_status()
    jsonResponse = response.json()

    #Extract {"id": "<class 'str'>", "name": "<class 'str'>"} from each object in jsonResponse and populate listLabelIds[]
    for i in range(len(jsonResponse)):
        tempDict = {'id': jsonResponse[i].get('id'), 'name': jsonResponse[i].get('name')}
        listLabelIds.append(tempDict)
        i += 1
    print(f"Found {len(listLabelIds)} Labels and extracted their Names and IDs.")

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return listLabelIds

#Get the Board's Custom Fields
def getCustomFields():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")
    
    #Formulate and send an HTTP request. Store the response and parse it as json.
    requestBody = payloadAuthToken
    requestUrl = f"{endpoint}boards/{BOARD_ID}/customFields"
    response = requests.get(requestUrl, params=requestBody)
    response.raise_for_status()
    jsonResponse = response.json()

    #Populate listCustomFields[] with the card info from jsonResponse
    listCustomFields.clear()
    listCustomFields.extend(jsonResponse)

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return listCustomFields

#Get the Custom Field IDs
def getCustomFieldIds():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")

    #Make sure getCustomFields() has been run
    getCustomFields()

    #Iterate through listCustomFields[] and populate listCustomFieldIds[] with the 'id' values
    listCustomFieldIds.clear()
    for i in range(len(listCustomFields)):
        tempDict = {'id': listCustomFields[i].get('id'), 'name': listCustomFields[i].get('name')}
        listCustomFieldIds.append(tempDict)
        i += 1

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return listCustomFieldIds

#Get the {option}s for the "Epic" CustomField #MOVE THIS TO apiScheduler
def getEpicOptions():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")

    #Make sure getCustomFields() has been run at least once
    getCustomFields()

    #Iterate through listCustomFields[] to find the 'Epic' field, and set it as epicField
    for i in range(len(listCustomFields)):
        if listCustomFields[i].get('name') == 'Epic':
            print(f"Found Epic at Index {i}")
            epicField = listCustomFields[i]
            break
        else:
            epicField = None
        i += 1          

    epicOptions = epicField.get('options')
    #Iterate through epicField[] and add each 'id' and 'value' to listEpicOptions[]
    listEpicOptions.clear()
    for b in range(len(epicOptions)):
        tempDict = {'id': epicOptions[b].get('id'), 'value': epicOptions[b].get('value')}
        listEpicOptions.append(tempDict)
        b += 1

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return listEpicOptions

#Create a new Card, using the json provided in the (request)
def postNewCard(request: dict):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")
    
    #Formulate an HTTP request
    request.update(payloadAuthToken)
    requestUrl = f"{endpoint}cards"

    jsonPayload = json.loads(json.dumps(request, indent=4, separators=(', ', ': ')))
    postHeaders = {
        'Accept-Encoding': 'gzip, deflate, br', 
        'Accept': '*/*', 
        'Content-Type': 'application/json',
        'Host': 'api.trello.com'
        }

    #Send the HTTP request and set responseMsg with the status
    response = requests.post(requestUrl, json=jsonPayload, headers=postHeaders)
    response.raise_for_status()
    responseMsg = f"{response.status_code}: {response.reason}"
    
    #This function expects the following:
    #body:
        #name - string
        #desc - string
        #pos - "top" OR "bottom" OR positive float
        #due - string (date)
        #dueComplete - boolean
        #idList - string, target List ID, REQUIRED
        #idMembers - [string]
        #idLabels - [idLabel]
        #urlSoruce - string (starting in http:// or https://)
        #fileSource - string (binary)
        #mimeType - string
        #idCardSource - string (id of a Card to copy from)
        #keepFromSource - string (properties to keep from source if copying)
        #address - string
        #locationName - string
        #coordinates - string
        #key: API Key
        #token: API Token
        
    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return [responseMsg, response.json()]

#Update an existing Card (idCard), using the json provided in the (request)
def putUpdateCard(request: dict, idCard: str):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")
    
    #Formulate an HTTP request
    request.update(payloadAuthToken)
    requestUrl = f"{endpoint}cards/{idCard}"

    #Account for Custom Field updates
    if request.get('idCustomField') is None:
        pass
    else:
        requestUrl += f"/customField/{request.get('idCustomField')}/item"
        del request['idCustomField']

    jsonPayload = json.loads(json.dumps(request, indent=4, separators=(', ', ': ')))
    postHeaders = {
        'Accept-Encoding': 'gzip, deflate, br', 
        'Accept': '*/*', 
        'Content-Type': 'application/json',
        'Host': 'api.trello.com'
        }
   
    #Send the HTTP request and set responseMsg with the status
    response = requests.put(requestUrl, json=jsonPayload, headers=postHeaders)
    response.raise_for_status()
    responseMsg = f"{response.status_code}: {response.reason}"

    #This function expects the following:
    #request:
        #id - ID of the Card to update
    #body:
        #name - string
        #desc - string
        #closed - boolean (archive = closed:true)
        #pos - "top" OR "bottom" OR positive float
        #due - string (date)
        #dueComplete - boolean
        #idList - string, target List ID, REQUIRED
        #idMembers - [string]
        #idLabels - [idLabel]
        #urlSoruce - string (starting in http:// or https://)
        #fileSource - string (binary)
        #mimeType - string
        #idCardSource - string (id of a Card to copy from)
        #keepFromSource - string (properties to keep from source if copying)
        #address - string
        #locationName - string
        #coordinates - string
        #cover - object{{"color": canonical color name}, {"brightness": "dark" OR "light"}, etc}
        #key: API Key
        #token: API Token

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return [responseMsg, response.json()]

#Create a new Checklist, using the json provided in the (request)
def postNewChecklist(request: dict):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")    
    
    #Formulate an HTTP request
    request.update(payloadAuthToken)
    requestUrl = f"{endpoint}checklists"

    jsonPayload = json.loads(json.dumps(request, indent=4, separators=(', ', ': ')))
    postHeaders = {
        'Accept-Encoding': 'gzip, deflate, br', 
        'Accept': '*/*', 
        'Content-Type': 'application/json',
        'Host': 'api.trello.com'
        }
   
    #Send the HTTP request and set responseMsg with the status
    response = requests.post(requestUrl, json=jsonPayload, headers=postHeaders)
    response.raise_for_status()
    responseMsg = f"{response.status_code}: {response.reason}"

    #This function expects the following:
    #body:
        #idCard - ID of the Card the Checklist should be added to (REQUIRED)
        #name - string
        #pos - "top" OR "bottom" OR positive float
        #idChecklistSource - ID of a checklist to copy from
        
    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return [responseMsg, response.json()]

#Create a Checkitem on an existing Checklist (idChecklist), using the json provided in the (request)
def postNewCheckItem(request: dict, idChecklist: str):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.utcnow()}")    
    
    #Formulate an HTTP request
    request.update(payloadAuthToken)
    requestUrl = f"{endpoint}checklists/{idChecklist}/checkItems"

    jsonPayload = json.loads(json.dumps(request, indent=4, separators=(', ', ': ')))
    postHeaders = {
        'Accept-Encoding': 'gzip, deflate, br', 
        'Accept': '*/*', 
        'Content-Type': 'application/json',
        'Host': 'api.trello.com'
        }
   
    #Send the HTTP request and set responseMsg with the status
    response = requests.post(requestUrl, json=jsonPayload, headers=postHeaders)
    response.raise_for_status()
    responseMsg = f"{response.status_code}: {response.reason}"

    #This function expects the following:
    #request:
        #id - ID of the checklist to add items to
    #body:
        #name - string (REQUIRED)
        #pos - "top" OR "bottom" OR positive float
        #checked - boolean
        
    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.utcnow()}\n")
    return [responseMsg, response.json()]

#TO DO:
    #getCardActions() - see TrelloCardAge for reference on getting card actions
    #getPluginData() - see notepad.py re: package tracking

# TEST FUNCTIONS up to 3 times, sleeping for 2 seconds if it fails and backing off each time
def main():
    print("I'm doing things!")
    sleepTime = 3
    for b in range(0, 3):
        try:
            getListIds()
            getCards()
            getCardIds()
            getLabelIds()
            getCustomFields()
            getCustomFieldIds()
            getEpicOptions()

            print("List of List IDs:")
            for i in range(len(listListIds)):
                print(f"{i+1}. {listListIds[i]}")
                i += 1
            print()

            print("List of Card IDs:")
            for i in range(len(listCardIds)):
                print(f"{i+1}. {listCardIds[i]}")
                i += 1
            print()

            print("List of Label IDs:")
            for i in range(len(listLabelIds)):
                print(f"{i+1}. {listLabelIds[i]}")
                i += 1
            print()

            print("List of Custom Field IDs:")
            for i in range(len(listCustomFieldIds)):
                print(f"{i+1}. {listCustomFieldIds[i]}")
                i += 1
            print()     
            
            print("List of Epic Options:")
            for i in range(len(listEpicOptions)):
                print(f"{i+1}. {listEpicOptions[i]}")
                i += 1          
            errored = None

        except Exception as errored:
            exceptMsg = str(errored).replace(API_KEY, "API Key Hidden-")
            exceptMsg = exceptMsg.replace(API_TOKEN, "API Token Hidden-")
            pass

        try: 
            errored
            break
        except NameError:
            print(f"{exceptMsg}\n Sleeping for {sleepTime} seconds before trying again...")
            sleep(sleepTime)
            sleepTime *= 2
        b += 1

if __name__ == '__main__':
    main()