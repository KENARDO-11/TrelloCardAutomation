# This function determines what API calls should be run on a given day, then coordinates the requests
import yaml
from time import sleep
import datetime
import os
import sys
from apiCaller import *
# from apiExtensions import *

# Some global lists and dicts
tasklistFilename = f"{sys.path[0]}{os.sep}tasklist.yml"
taskList = {}
dictTrelloLists = {}
dictTrelloLabels = {}
listTrelloLists = []
listTrelloLabels = []

# Globally, the last returned card and checklist's json dicts for reference in further tasks in a given job
lastReturnedCard = {}
lastReturnedChecklist = {}

# Globally, a list of checklists and checkitems generated by previous tasks, to be referenced in later tasks in a given job
listReturnedChecklists = []
listReturnedCheckItems = []

# Extend YAML Dumper to drop aliases
class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

# Fetch the list of scheduled Tasks and store it as a dict
def fetchTaskList(filename: str):
    print('Fetching the tasklist...')
    with open(filename) as f:
        stream = f.read()
    taskList.update(yaml.load(stream, yaml.Loader))
    print('Tasklist fetched successfully.\n')

# Analyze the taskList to determine what tasks need to be performed today, in which order #IN PROGRESS
def parseTaskList():
    print('Parsing the tasklist...')
    
    # Get today's date for use in checking whether a task should be run today
    weekdays = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday'
    ]
    todayDate = datetime.date.today()
    today = weekdays[datetime.date.weekday(todayDate)]
    print(f"Today is {today}.")
    
    taskIndex = 0
    for key, value in taskList.items():
        runDays = value.get('Run Days')
        
        if runDays.__contains__(today):
            print(f"\nTask \'{value.get('Name')}\' needs to run today.")
            taskIndex += 1 
            taskFile = f'{sys.path[0]}{os.sep}Tasks{os.sep}'
            taskFile += value.get('File')
            print(f"Starting Task {taskIndex}: {value.get('Name')}")
            readTask(taskFile)

            updateTask = {key: value}
            updateValue = value
            lastRun = {'Last Run': todayDate.isoformat()}
            updateValue.update(lastRun)
            # updateTask.update(key=updateValue)

            print('Updating Task List with last-run date...')
            taskList.update(updateTask)
            updateTasklist()
        
        else:
            print(f"\nTask \'{value.get('Name')}\' does not run on {today}.")

# Fetch the specified Task YAML file, read it, and call the appropriate functions in order #IN PROGRESS
def readTask(filename: str):
    with open(filename) as f:
        stream = f.read()
    readTasks = yaml.load(stream, yaml.Loader)
    print('\nOpened Task File successfully.')

    if readTasks is None:
        print("Nothing to do. Skipping.")
        return

    for key, value in readTasks.items():
        
        # Error Handler tries each task up to 3 times, sleeping for sleepTime seconds if it fails and backing off each time
        sleepTime = 3
        for b in range(3):
            try:
                if key.__contains__('New'):
                    if key.__contains__('Card'):
                        createCard(value)
                    elif key.__contains__('Checklist'):
                        createChecklist(value)
                    elif key.__contains__('CheckItem'):
                        createCheckItem(value)
                    else:
                        print(f"Something went wrong. {key} is  not a valid request type.")

                elif key.__contains__('Update'):
                    if key.__contains__('Card'):
                        updateCard(value)
                    elif key.__contains__('Checklist'):
                        updateChecklist(value)
                    elif key.__contains__('CheckItem'):
                        updateCheckItem(value)
                    else:
                        print(f"Something went wrong. {key} is  not a valid request type.")
                
                else:
                    print(f"Something went wrong. {key} is not a valid request type.")
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

    # Clear the lists of returned items at the end of each task, before the next task starts.
    listReturnedChecklists.clear()
    listReturnedCheckItems.clear()

# Update tasklist.yml whenever a task completes
def updateTasklist():
    stream = open(tasklistFilename, mode='w+')
    yaml.dump(data=taskList, stream=stream, Dumper=NoAliasDumper, explicit_start=True)
    return

# Get the information on Lists
def readLists():
    print('\nReading Lists...')
    listTrelloLists.clear()
    listTrelloLists.extend(getListIds())
    
    for i in range(len(listTrelloLists)):
        tempDict = {listTrelloLists[i].get('name'): i}
        dictTrelloLists.update(tempDict)
        i += 1
    
    return dictTrelloLists, listTrelloLists

# Get the information on Labels
def readLabels():
    print('\nReading Labels...')
    listTrelloLabels.clear()
    listTrelloLabels.extend(getLabelIds())

    for i in range(len(listTrelloLabels)):
        tempDict = {listTrelloLabels[i].get('name'): i}
        dictTrelloLabels.update(tempDict)
        i += 1
    
    return dictTrelloLabels, listTrelloLabels

# Get the {option}s for the "Epic" CustomField
def getEpicOptions():
    print('\nGetting a list of options for the Epic field...')
    # Make sure getCustomFields() has been run at least once
    listCustomFields = getCustomFields()

    # Iterate through listCustomFields[] to find the 'Epic' field, and set it as epicField
    for i in range(len(listCustomFields)):
        if listCustomFields[i].get('name') == 'Epic':
            print(f"Found Epic at Index {i}")
            epicField = listCustomFields[i]
            break
        else:
            epicField = None
        i += 1          

    epicOptions = epicField.get('options')
    # Iterate through epicField[] and add each 'id' and 'value' to listEpicOptions[]
    listEpicOptions = []
    for b in range(len(epicOptions)):
        tempDict = {'id': epicOptions[b].get('id'), 'value': epicOptions[b].get('value')}
        listEpicOptions.append(tempDict)
        b += 1

    return listEpicOptions

# Build a "Create Card" request and feed it to apiCaller
def createCard(newCardDetails: dict):
    print('\nBuilding a new Card...')
    
    # Normalize the request
    normalizedDetails = normalizeRequestDetails(newCardDetails)

    # Instantiate local variables and clear lastReturnedCard{}
    requestDetails = normalizedDetails.get('request')
    idList = normalizedDetails.get('idList')
    idLabels = normalizedDetails.get('idLabels') 
    nameLabels = requestDetails.get('nameLabels')
    nameList = requestDetails.get('nameList')
    listIdLabels = []
    lastReturnedCard.clear()
    
    # Variables to hold values that can't be set by Create Card and require an implicit update
    idCustomField = requestDetails.get('idCustomField')
    nameCustomField = requestDetails.get('nameCustomField')
    valueCustomField = requestDetails.get('valueCustomField')   
    newCardCover = normalizedDetails.get('cover')    
    del normalizedDetails['request']

    # Transmit the Create Card request
    newCardJson = normalizedDetails
    newCardResponse = postNewCard(newCardJson)
    responseMsg = newCardResponse[0]
    returnedCard = newCardResponse[1]
    lastReturnedCard.update(returnedCard)
    
    # Perform implicit updates for card details that can't be added during Create
    if newCardCover is not None or idCustomField is not None or nameCustomField is not None or valueCustomField is not None:
        newElements = {
            'idCustomField': idCustomField,
            'nameCustomField': nameCustomField,
            'valueCustomField': valueCustomField,
            'cover': newCardCover
        }
        implicitUpdateCard = makeImplicitUpdateCard(returnedCard, newElements)
        updateCard(implicitUpdateCard)

    lastReturnedCard.update(returnedCard)
    return returnedCard

# Build an "Update Card" rquest and feed it to apiCaller
def updateCard(updateCardDetails: dict):
    print('\nBuilding an Update Card request...')
    
    # Normalize the request
    normalizedDetails = normalizeRequestDetails(updateCardDetails)
    if normalizedDetails is None:
        return
    # Instantiate local variables
    requestDetails = normalizedDetails.get('request')
    idCard = requestDetails.get('idCard') 
    idList = normalizedDetails.get('idList')
    idLabels = normalizedDetails.get('idLabels')
    idCustomField = requestDetails.get('idCustomField')  
    nameCustomField = requestDetails.get('nameCustomField')
    valueCustomField = requestDetails.get('valueCustomField')
    jobExtensions = normalizedDetails.get('jobExtensions')
    idValue = None

    # Get the Custom Field ID to update if 'idCustomField' is empty but a custom field is named.
    if idCustomField is None:
        if nameCustomField is not None:
            customFields = getCustomFieldIds()
            for i in range(len(customFields)):
                if customFields[i].get('name') == nameCustomField:
                    idCustomField = customFields[i].get('id')
                i += 1

    # Make sure we only try to handle Custom Field values in a valid way
    if valueCustomField is not None:
        if idCustomField is not None:
            customFieldRequest = {'idCustomField': '', 'value': ''}
            
            if nameCustomField == 'Epic':
                epicOptions = getEpicOptions()

                for i in range(len(epicOptions)):
                    epicValue = epicOptions[i].get('value')
                    if epicValue.get('text') == valueCustomField:
                        idValue = epicOptions[i].get('id')
                        customFieldRequest.update(idValue=idValue)
                        valueCustomField = None
                        break
                    i += 1    
            else:
                valueCustomField = {'text': valueCustomField }

            customFieldRequest.update(idCustomField=idCustomField, value=valueCustomField, idValue=idValue)
            updateCardResponse = putUpdateCard(customFieldRequest, idCard)
        else:
            print("Error: A Custom Field Value was specified without a Custom Field ID or Name")

    # Call Extensions if they're requested
    if jobExtensions is not None:
        for i in range(len(jobExtensions)):
            extensionCall = jobExtensions[i]

            enrichedData = eval(extensionCall)
            normalizedDetails.update(enrichedData)
            i += 1
        
    # Some cleanup
    del normalizedDetails['request']
    lastReturnedCard.clear()
    updateCardJson = normalizedDetails

    # Transmit the Update Card requeest
    updateCardResponse = putUpdateCard(updateCardJson, idCard)
    responseMsg = updateCardResponse[0]
    returnedCard = updateCardResponse[1]

    lastReturnedCard.update(returnedCard)
    return returnedCard

# Build a "Create Checklist" request and feed it to apiCaller
def createChecklist(newChecklistDetails: dict):
    print('\nBuilding a new Checklist...')
    # Normalize the request
    normalizedDetails = normalizeRequestDetails(newChecklistDetails)   
    idCard = normalizedDetails.get('idCard')
    lastReturnedChecklist.clear()

    normalizedDetails.update(idCard=idCard)
    newChecklistJson = normalizedDetails
    newChecklistResponse = postNewChecklist(newChecklistJson)
    responseMsg = newChecklistResponse[0]
    returnedChecklist = newChecklistResponse[1]

    lastReturnedChecklist.update(returnedChecklist)
    listReturnedChecklists.append(lastReturnedChecklist)
    return returnedChecklist

# Build a "Create CheckItem" request and feed it to apiCaller
def createCheckItem(newCheckItemDetails: dict):
    print('\nBuilding a new Check Item...')
    checkItemRequest = newCheckItemDetails.get('request')
    idChecklist = checkItemRequest.get('idChecklist')

    if idChecklist is None:
        pass
    elif type(idChecklist) is int:
        idChecklist = lastReturnedChecklist.get('id')

    del newCheckItemDetails['request']
    
    newCheckItemJson = newCheckItemDetails
    newCheckItemResponse = postNewCheckItem(newCheckItemJson, idChecklist)
    responseMsg = newCheckItemResponse[0]
    returnedCheckItem = newCheckItemResponse[1]

    listReturnedCheckItems.append(returnedCheckItem)
    return returnedCheckItem

# Build an "Update Checklist request and feed it to apiCaller"
def updateChecklist(updateChecklistDetails: dict):
    print("The API Caller does not currently have Update Checklist functionality.")
    pass

# Build an "Update CheckItem" request and feed it to apiCaller
def updateCheckItem(updateCheckItemDetails: dict):
    print("The API Caller does not currently have Update Checklist Item functionality.")
    pass

# Normalize common requests to use IDs instead of Names
def normalizeRequestDetails(irregularRequestDetails: dict):
    print('Normalizing request parameters...')
    
    normalizedDetails =  irregularRequestDetails

    # Get the 'request' dict if it exists, create one with None values otherwise
    if irregularRequestDetails.get('request') is not None:
        requestDetails = irregularRequestDetails.get('request')
    else:
        requestDetails = {
            'idCard': None,          
            'nameLabels': None,
            'nameList': None,        
            'idCustomField': None,   
            'nameCustomField': None, 
            'valueCustomField': None
        }
    
    # Special handling for idCard, which may appear in 'request' or the body
    if irregularRequestDetails.get('idCard') is None:
        idCard = requestDetails.get('idCard')
    else:
        idCard = irregularRequestDetails.get('idCard')

    idList = irregularRequestDetails.get('idList')
    idLabels = irregularRequestDetails.get('idLabels') 
    nameLabels = requestDetails.get('nameLabels')
    nameList = requestDetails.get('nameList')
    listIdLabels = []

    # Normalize idList
    if idList is None:
        if nameList is None:
            print('No List specified.')
        else:
            newIndex = dictTrelloLists.get(nameList)
            newList = listTrelloLists[newIndex]
            newListId = newList.get('id')
            normalizedDetails.update(idList=newListId)    

    # Normalize idCard
    if idCard is None:
        print('No Card ID provided')
    elif idCard == 'self':
        idCard = lastReturnedCard.get('id')
        requestDetails.update(idCard=idCard)
    elif idCard == 'list':
        makeIterativeUpdateCard(irregularRequestDetails)
        return

    # normalize idLabels
    if idLabels is None:
        if nameLabels is None:
            print('No Labels provided.')    
        else:
            for i in range(len(nameLabels)):
                searchLabel = nameLabels[i]
                labelIndex = dictTrelloLabels.get(searchLabel)
                listIdLabels.append(listTrelloLabels[labelIndex].get('id'))
                i += 1
            normalizedDetails.update(idLabels=listIdLabels)

    normalizedDetails.update(requestDetails)
    return normalizedDetails

# Create a new dict to feed updateCard() when the New Card task contains elements that Trello doesn't add on creation
def makeImplicitUpdateCard(cardDetails: dict, newElements: dict):
    print('Performing an implicit update...')
    idCard = cardDetails.get('id')
    idCustomField = newElements.get('idCustomField')
    nameCustomField = newElements.get('nameCustomField')
    valueCustomField = newElements.get('valueCustomField')
    cover = newElements.get('cover')

    implicitUpdateCard = {
        'request': {
            'idCard': idCard,
            'idCustomField': idCustomField,
            'nameCustomField': nameCustomField,
            'valueCustomField': valueCustomField,
        },
        'cover': cover
    }

    return implicitUpdateCard

# Use a list to do generate updateCard() calls for each card in the list
def makeIterativeUpdateCard(listCardDetails: dict):
    print('Starting an Iterative Update proces...')

    requestDetails = listCardDetails.get('request')
    idList = listCardDetails.get('idList')
    nameList = requestDetails.get('nameList')
    listIdCards = []
    
    listCardsInList = getCardsInList(idList)
    print(f"Iterating through {len(listCardsInList)} cards...")
    #Iterate through the list of cards in the List and make a list of Card IDs
    for i in range(len(listCardsInList)):
        tempIdCard = listCardsInList[i].get('id')
        listIdCards.append(tempIdCard)
        i += 1
    
    #Iterate through the list of Card IDs and call updateCard() for each one
    for i in range(len(listIdCards)):
        print(f"Building request details for Card #{i+1}")
        tempRequest = requestDetails
        tempRequest.update(idCard=listIdCards[i], nameList=None)
        tempUpdateCard = listCardDetails
        tempUpdateCard.update(request=tempRequest, idList=idList)

        updateCard(tempUpdateCard)
        i += 1

    return

# Main function
def main():
    fetchTaskList(tasklistFilename) 
    readLists()
    readLabels()
    parseTaskList()

if __name__ == '__main__':
    main()