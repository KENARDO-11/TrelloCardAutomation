from dateutil.parser import isoparse

listEpicIdValues = []       #This isn't implemented anywhere

#dict of covers for global update use, in legend:{coverObject} format
dictCoverOptions = {
    "personal": {"cover": {"color": "green"}},
    "domestic": {"cover": {"color": "blue"}},
    "work": {"cover": {"color": "red"}},
    "school": {"cover": {"color": "black"}},
    "automotive": {"cover": {"color": "yellow"}},
    "noCover": {"cover": ""}
}

#sample json
jsonSampleCard = {
    'name': '',             #string
    'desc': '',             #string
    'closed': False,        #boolean
    'pos': '',              #"top" OR "bottom" OR positive float
    'due': '',              #string (date)
    'dueComplete': False,   #boolean
    'idList': '',           #string (target List ID) REQUIRED
    'idMembers': '',        #string []
    'idLabels': '',         #idLabel[]
    'urlSource': '',        #string (starting in http:// or https://)
    'fileSource': '',       #string (binary)
    'mimeType': '',         #string
    'idCardSource': '',     #string (id of a Card to copy from)
    'keepFromSource': '',   #string (properties to keep from source if copying)
    'address': '',          #string
    'locationName': '',     #string
    'coordinates': '',      #string
    'cover': ''             #object{{"color": canonical color name}, {"brightness": "dark" OR "light"}, etc}
}
jsonSampleCheckList = {
    'idCard': '',           #ID of the Card the Checklist should be added to (REQUIRED)
    'name': '',             #string
    'pos': '',              #"top" OR "bottom" OR positive float
    'idChecklistSource': '' #ID of a checklist to copy from
}
jsonSampleCheckItem = {
    'name': '',     #string (REQUIRED)
    'pos': '',      #"top" OR "bottom" OR positive float
    'checked': ''   #boolean
}

#Get time in Blocked list for idCard
def getTimeInBlockedList(idCard):
    print(f"this will get the time {idCard} has spent in the Blocked list since being put there")
    #request: GET /1/cards/{id}/actions
        #id - the Card ID to get Actions from
    #body: {json}
        #key: API Key
        #token: API Token
        #"filter": ['updateCard:idList','createCard', 'convertToCardFromCheckItem', 'copyCard', 'moveCardToBoard']

    #Successful requests return:
    #http.status 200 OK
    #body: {json}
        #{updateCard Actions}

    #listUpdateActions = response.json()
    #listUpdateActions[0] should contain {{"data": {"card": {"idList": "blockedListId"}}}}. If it does, get [0].{"date"} and store it as dateInBlocked
    return "(today's date - dateInBlocked)"
    #if this returns a value greater than 7 days, the function calling it will generate json and call postNewCard()
    #Actually that's probably bullshit, this function probably doesn't need to exist, I'm just a fuckup

#Get time in To Do list for idCard
def getTimeInToDoList(idCard):
    print(f"this will get the time {idCard} has spent in the To Do list since being put there")
    #request: GET /1/cards/{id}/actions
        #id - the Card ID to get Actions from
    #body: {json}
        #key: API Key
        #token: API Token
        #'filter': ['updateCard:idList','createCard', 'convertToCardFromCheckItem', 'copyCard', 'moveCardToBoard']

    #Successful requests return:
    #http.status 200 OK
    #body: {json}
        #{updateCard Actions}

    #listUpdateActions = response.json()
    #listUpdateActions[0] should contain {{"data": {"card:" {"idList": "toDoIdList"}}}}. If it does, get [0].{"date"} and store it as dateInBlocked
    return "(today's date - dateInBlocked)"
    #if this returns a value greater than 10 days, the function calling it will generate json and call putUpdateCard()

#Get the idValues for the "Epic" CustomField --- Not Implemented
def getEpicIdValues():
    print("I don't know if I'm going to need or want this")

    #Extract a list of {"id": "<class 'str'>"} dicts, replace "id" with "idValue", and stuff it into listEpicIdValues[]
    successMessage = ""
    return successMessage

###Add Cards Daily:

#Feed Scirocco
def addFeedScirocco():
    print("This will remind me to feed my kitten")

    jsonNewCard = {
        'name': 'Feed Scirocco',
        'closed': False,
        'pos': 'top',
        'idList': '',   #string (target List ID) REQUIRED
        'idLabels': '', #idLabel[] Label: {“name”: “Scirocco”, “color”: “orange”}
        'cover': {{'color': dictCoverOptions.get('domestic')}}
    }

    jsonNewChecklist = {
        'idCard': '',           #ID of the Card the Checklist should be added to (REQUIRED)
        'name': 'Feeding Times'
    }

    jsonCheckItem1 = {
        'name': 'Morning',
        'pos': 'top',
        'checked': False
    }

    jsonCheckItem2 = {
        'name': 'Afternoon',
        'pos': 'top',
        'checked': False
    }    

    return

#WGU Studies
def addWguStudies():
    print("This will remind me to study for school")
    #Position: Below "Feed Scirocco"
    #Checklist:
        # Morning
        # Mid-Day
        # Afternoon
        # Evening
    #Cover: {“color”: “black”}
    #Label: {“name”: “Course Studies”, “color”: “black”}
    #Epic: {“idCustomField”: “620eb1e04ff0807368d0a0c0”, “idValue”: “620eb1e04ff0807368d0a0ce”} 
        #idValue corresponds to “Daily Studies”#

    return

#Japanese Studies
def addJapaneseStudies():
    print("This will remind me to study Japanese")
    #Position: Below “WGU Studies”
    #Checklist:
        #Session 1
        #Session 2
    #Cover: {“color”: “green”}
    #Label: {“name”: “Japan Migration”, “color”: “lime”}
    #Epic: {“idCustomField”: “620eb1e04ff0807368d0a0c0”, “idValue”: “620eb1e04ff0807368d0a0ce”} 
        #idValue corresponds to “Daily Studies”#

    return

#Physical Therapy Exercises
def addPhysicalTherapyExercises():
    print("This will remind me to do my PT")
    # Position: Below “WGU Studies”
    # Checklist: (Subject to Change)
        # Pelvic Tilt
        # Trunk Rotations
        # Lumbar Bridges
        # Leg Raises
    # Cover: {“color”: “green”}
    # Label: {“name”: “Health”, “color”: “sky”}
    # Epic: {“idCustomField”: “620eb1e04ff0807368d0a0c0”, “idValue”: “620eb1e04ff0807368d0a0c1”} 
        #idValue corresponds to “Physical Therapy”#

    return


###Move Cards Daily:

#Move cards that have spent more than 10 days in To Do, to Backburner
def moveStaleCardsToBackburner():
    print("This will move stale cards from the To-Do list to the Backburner")
    #getTimeInToDoList(idCard) is our friend here

    return

###Archive Cards Daily:

#Archive cards in Package Tracking with a "DELIVERED" status
def archiveDeliveredPackageCards():
    print("This will archive cards if they're tracking a delivered package")
   
    #for each card in "Package Tracking" list:
        #Force the Package Tracker plugin to update by changing the front of the card
        #putUpdateCard(forceUpdateJson)
            #body: key, token, cover: {"color": "green"}
        #Change the cover back to empty
        #putUpdateCard(forceUpdateJson)
            #body: key, token, cover: ""

        #Get the pluginData for the delivery status
        #request GET /1/cards/{idCard}/pluginData
        #if response contains {"value": {"statuses": [ {"status": "DELIVERED"} ] } }
        #the package has been delivered, move this to the archive
    
    return


# if __name__ == '__main__':
    
#     stream = open("C:\\Users\\SUPERDICKS MkVII\\Documents\\Projects\\KENARDONET\\Scripts\\APIs\\Trello\\TrelloCardAutomation\\Tasks\\feedscirocco.yml", 'r')
#     dictionary = yaml.load(stream, yaml.Loader)

#     print(dictionary)

#     for key, value in dictionary.items():
#         if type(value) is dict:
#             print(f"\n{key}:")
#             for aKey, aValue in value.items():
#                 if type(aValue) is list:
#                     print(f"--{aKey}:")
#                     for i in range(len(aValue)):
#                         if type(aValue[i]) is dict:
#                             for speen, smook in aValue[i].items():
#                                 print(f"----{speen}: {smook}")
#                         else:
#                             print(f"----{aValue[i]}")
#                 else:
#                     print(f"--{aKey}: {aValue}")
#         else:
#             print(f"{key}: {value}")

a = 1
if a is None:
    print('speen')
else:
    print('smook')