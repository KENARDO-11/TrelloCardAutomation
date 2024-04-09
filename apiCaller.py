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
payload_auth_token = {'key': API_KEY, 'token': API_TOKEN}

#Trello API Endpoint
endpoint = "https://api.trello.com/1/"

#lists for global use
list_listIds = []
list_cards = []
list_cardIds = []
list_labellIds = []
list_custom_fields = []
list_custom_field_ids = []

#Get the Board's List IDs
def get_list_ids():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")

    #Formulate and send an HTTP request. Store the response and parse it as json.
    request_body = payload_auth_token
    request_url = f"{endpoint}boards/{BOARD_ID}/lists"
    response = requests.get(request_url, params=request_body)
    response.raise_for_status()
    json_response = response.json()
    
    #Extract {"id": "<class 'str'>", "name": "<class 'str'>"} from each object in json_response and populate list_listIds[]
    for i in range(len(json_response)):
        temp_dict = {'id': json_response[i].get('id'), 'name': json_response[i].get('name')}
        list_listIds.append(temp_dict)
        i += 1
    print(f"Found {len(list_listIds)} Lists and extracted their Names and IDs.")

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return list_listIds

#Get the Board's Cards
def get_cards():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")
    
    #Formulate and send an HTTP request. Store the response and parse it as json.
    request_body = payload_auth_token
    request_url = f"{endpoint}boards/{BOARD_ID}/cards"
    response = requests.get(request_url, params=request_body)
    response.raise_for_status()
    json_response = response.json()

    #Populate list_cards[] with the card info from json_response
    list_cards.clear()
    list_cards.extend(json_response)

    print(f"Found {len(list_cards)} Cards.")


    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return list_cards

#Get Card IDs from list_cards[]
def get_card_ids():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")

    #Iterate through list_cards[] and populate list_cardIds[] with the 'id' values
    list_cardIds.clear()
    for i in range(len(list_cards)):
        list_cardIds.append(list_cards[i].get('id'))
        i += 1

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return list_cardIds

#Get the Cards in a List
def get_cards_in_list(id_list: str):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")
    
    #Formulate and send an HTTP request. Store the response and parse it as json.
    request_body = payload_auth_token
    request_url = f"{endpoint}lists/{id_list}/cards"
    response = requests.get(request_url, params=request_body)
    response.raise_for_status()
    json_response = response.json()

    #Populate list_cards_in_list[] with the card info from json_response
    list_cards_in_list = json_response

    print(f"Found {len(list_cards_in_list)} Cards.")


    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return list_cards_in_list

#Get the Board's Label IDs
def get_label_ids():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")
    
    #Formulate and send an HTTP request. Store the response and parse it as json.
    request_body = payload_auth_token
    request_url = f"{endpoint}boards/{BOARD_ID}/labels"
    response = requests.get(request_url, params=request_body)
    response.raise_for_status()
    json_response = response.json()

    #Extract {"id": "<class 'str'>", "name": "<class 'str'>"} from each object in json_response and populate list_labellIds[]
    for i in range(len(json_response)):
        temp_dict = {'id': json_response[i].get('id'), 'name': json_response[i].get('name')}
        list_labellIds.append(temp_dict)
        i += 1
    print(f"Found {len(list_labellIds)} Labels and extracted their Names and IDs.")

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return list_labellIds

#Get the Board's Custom Fields
def get_custom_fields():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")
    
    #Formulate and send an HTTP request. Store the response and parse it as json.
    request_body = payload_auth_token
    request_url = f"{endpoint}boards/{BOARD_ID}/customFields"
    response = requests.get(request_url, params=request_body)
    response.raise_for_status()
    json_response = response.json()

    #Populate list_custom_fields[] with the card info from json_response
    list_custom_fields.clear()
    list_custom_fields.extend(json_response)

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return list_custom_fields

#Get the Custom Field IDs
def get_custom_field_ids():
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")

    #Make sure get_custom_fields() has been run
    get_custom_fields()

    #Iterate through list_custom_fields[] and populate list_custom_field_ids[] with the 'id' values
    list_custom_field_ids.clear()
    for i in range(len(list_custom_fields)):
        temp_dict = {'id': list_custom_fields[i].get('id'), 'name': list_custom_fields[i].get('name')}
        list_custom_field_ids.append(temp_dict)
        i += 1

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return list_custom_field_ids

#Get the actions[] for the provided id_card and return them #TO DO
def get_card_actions(id_card: str, filter: list):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")

    #Formulate and send an HTTP request. Store the reesponse and parse it as json.
    payload_action_request = {'filter': filter}
    payload_action_request.update(payload_auth_token)    
    url_card_request = f"{endpoint}cards/{id_card}/actions"
    response = requests.get(url_card_request, params=payload_action_request)
    response.raise_for_status()
    json_actions = response.json()

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return json_actions

#Get the {pluginData} for the provided id_card
def get_plugin_data(id_card: str):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")

    #Force the plugin to update by changing the front of the card, then sleep for 2 seconds to make sure the pluginData has time to update
    force_update_json = {'cover': {'color': 'green'}}
    force_update_json.update(payload_auth_token)
    put_update_card(force_update_json, id_card)
    force_update_json.update(cover='')
    put_update_card(force_update_json, id_card)
    sleep(2)

    #Generate and transmit a GET pluginData request
    request_body = payload_auth_token
    request_url = f"{endpoint}cards/{id_card}/pluginData"
    response = requests.get(request_url, params=request_body)
    response.raise_for_status()
    json_response = response.json()

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return json_response

#Create a new Card, using the json provided in the (request)
def post_new_card(request: dict):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")
    
    #Formulate an HTTP request
    request.update(payload_auth_token)
    request_url = f"{endpoint}cards"

    json_payload = json.loads(json.dumps(request, indent=4, separators=(', ', ': ')))
    post_headers = {
        'Accept-Encoding': 'gzip, deflate, br', 
        'Accept': '*/*', 
        'Content-Type': 'application/json',
        'Host': 'api.trello.com'
        }

    #Send the HTTP request and set response_msg with the status
    response = requests.post(request_url, json=json_payload, headers=post_headers)
    response.raise_for_status()
    response_msg = f"{response.status_code}: {response.reason}"
    
    #This function expects the following:
    #body:
        #name - string
        #desc - string
        #pos - "top" OR "bottom" OR positive float
        #due - string (date)
        #dueComplete - boolean
        #id_list - string, target List ID, REQUIRED
        #idMembers - [string]
        #idLabels - [idLabel]
        #urlSoruce - string (starting in http:// or https://)
        #fileSource - string (binary)
        #mimeType - string
        #id_cardSource - string (id of a Card to copy from)
        #keepFromSource - string (properties to keep from source if copying)
        #address - string
        #locationName - string
        #coordinates - string
        #key: API Key
        #token: API Token
        
    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return [response_msg, response.json()]

#Update an existing Card (id_card), using the json provided in the (request)
def put_update_card(request: dict, id_card: str):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")
    
    #Formulate an HTTP request
    request.update(payload_auth_token)
    request_url = f"{endpoint}cards/{id_card}"

    #Account for Custom Field updates
    if request.get('idCustomField') is None:
        pass
    else:
        request_url += f"/customField/{request.get('idCustomField')}/item"
        del request['idCustomField']

    json_payload = json.loads(json.dumps(request, indent=4, separators=(', ', ': ')))
    post_headers = {
        'Accept-Encoding': 'gzip, deflate, br', 
        'Accept': '*/*', 
        'Content-Type': 'application/json',
        'Host': 'api.trello.com'
        }
   
    #Send the HTTP request and set response_msg with the status
    response = requests.put(request_url, json=json_payload, headers=post_headers)
    response.raise_for_status()
    response_msg = f"{response.status_code}: {response.reason}"

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
        #id_list - string, target List ID, REQUIRED
        #idMembers - [string]
        #idLabels - [idLabel]
        #urlSoruce - string (starting in http:// or https://)
        #fileSource - string (binary)
        #mimeType - string
        #id_cardSource - string (id of a Card to copy from)
        #keepFromSource - string (properties to keep from source if copying)
        #address - string
        #locationName - string
        #coordinates - string
        #cover - object{{"color": canonical color name}, {"brightness": "dark" OR "light"}, etc}
        #key: API Key
        #token: API Token

    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return [response_msg, response.json()]

#Create a new Checklist, using the json provided in the (request)
def post_new_checklist(request: dict):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")    
    
    #Formulate an HTTP request
    request.update(payload_auth_token)
    request_url = f"{endpoint}checklists"

    json_payload = json.loads(json.dumps(request, indent=4, separators=(', ', ': ')))
    post_headers = {
        'Accept-Encoding': 'gzip, deflate, br', 
        'Accept': '*/*', 
        'Content-Type': 'application/json',
        'Host': 'api.trello.com'
        }
   
    #Send the HTTP request and set response_msg with the status
    response = requests.post(request_url, json=json_payload, headers=post_headers)
    response.raise_for_status()
    response_msg = f"{response.status_code}: {response.reason}"

    #This function expects the following:
    #body:
        #id_card - ID of the Card the Checklist should be added to (REQUIRED)
        #name - string
        #pos - "top" OR "bottom" OR positive float
        #idChecklistSource - ID of a checklist to copy from
        
    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return [response_msg, response.json()]

#Create a Checkitem on an existing Checklist (idChecklist), using the json provided in the (request)
def post_new_checkitem(request: dict, idChecklist: str):
    print(f"Starting {sys._getframe().f_code.co_name} at {datetime.datetime.now(datetime.UTC)}")    
    
    #Formulate an HTTP request
    request.update(payload_auth_token)
    request_url = f"{endpoint}checklists/{idChecklist}/checkItems"

    json_payload = json.loads(json.dumps(request, indent=4, separators=(', ', ': ')))
    post_headers = {
        'Accept-Encoding': 'gzip, deflate, br', 
        'Accept': '*/*', 
        'Content-Type': 'application/json',
        'Host': 'api.trello.com'
        }
   
    #Send the HTTP request and set response_msg with the status
    response = requests.post(request_url, json=json_payload, headers=post_headers)
    response.raise_for_status()
    response_msg = f"{response.status_code}: {response.reason}"

    #This function expects the following:
    #request:
        #id - ID of the checklist to add items to
    #body:
        #name - string (REQUIRED)
        #pos - "top" OR "bottom" OR positive float
        #checked - boolean
        
    print(f"{sys._getframe().f_code.co_name} completed successfully at {datetime.datetime.now(datetime.UTC)}\n")
    return [response_msg, response.json()]

# TEST FUNCTIONS up to 3 times, sleeping for 2 seconds if it fails and backing off each time
def main():
    print("I'm doing things!")
    sleepTime = 3
    for b in range(0, 3):
        try:
            get_list_ids()
            get_cards()
            get_card_ids()
            get_label_ids()
            get_custom_fields()
            get_custom_field_ids()

            print("List of List IDs:")
            for i in range(len(list_listIds)):
                print(f"{i+1}. {list_listIds[i]}")
                i += 1
            print()

            print("List of Card IDs:")
            for i in range(len(list_cardIds)):
                print(f"{i+1}. {list_cardIds[i]}")
                i += 1
            print()

            print("List of Label IDs:")
            for i in range(len(list_labellIds)):
                print(f"{i+1}. {list_labellIds[i]}")
                i += 1
            print()

            print("List of Custom Field IDs:")
            for i in range(len(list_custom_field_ids)):
                print(f"{i+1}. {list_custom_field_ids[i]}")
                i += 1
            print()     
                  
            errored = None

        except Exception as errored:
            except_msg = str(errored).replace(API_KEY, "API Key Hidden-")
            except_msg = except_msg.replace(API_TOKEN, "API Token Hidden-")
            pass

        try: 
            errored
            break
        except NameError:
            print(f"{except_msg}\n Sleeping for {sleepTime} seconds before trying again...")
            sleep(sleepTime)
            sleepTime *= 2
        b += 1

if __name__ == '__main__':
    main()