#This function determines what API calls should be run on a given day, then coordinates the requests

#Get the items in joblist, figure out what should be run, build the tasks to run, and update joblist with last-run date
import yaml
from time import sleep
import json
import requests
import datetime
import os
import sys
from dotenv import load_dotenv
from apiCaller import *
from apiExtensions import *

#Some global lists and dicts
taskList = {}
dictTrelloLists = {}
dictTrelloLabels = {}
listTrelloLists = []
listTrelloLabels = []

#Globally, the last returned card and checklist's json dicts for reference in further tasks in a given job
lastReturnedCard = {}
lastReturnedChecklist = {}

#Globally, a list of checklists and checkitems generated by previous tasks, to be referenced in later tasks in a given job
listReturnedChecklists = []
listReturnedCheckItems = []

#Fetch the list of scheduled Tasks and store it as a dict
def fetchTaskList(filename: str):
    print('Fetching the tasklist...')
    stream = open(filename, 'r')
    taskList.update(yaml.load(stream, yaml.Loader))
    print('Tasklist fetched successfully.')

#Analyze the taskList to determine what tasks need to be performed today, in which order #IN PROGRESS
def parseTaskList():
    print('Parsing the tasklist...')
    #Still need to add run day handling
    taskIndex = 0
    for key, value in taskList.items():
        taskIndex += 1 
        taskFile = f'{sys.path[0]}{os.sep}Tasks{os.sep}'
        taskFile += value.get('File')
        print(f"Starting Task {taskIndex}: {value.get('Name')}")
        readTask(taskFile)

#Fetch the specified Task YAML file, read it, and call the appropriate functions in order #IN PROGRESS
def readTask(filename: str):
    stream = open(filename, 'r')
    readTasks = yaml.load(stream, yaml.Loader)
    print('Opened Task File successfully.')

    if readTasks is None:
        print("Nothing to do. Skipping.")
        return

    # numTasks = len(readTasks)

    #I like this logic for iterating through the Task file and pointing to request functions
    #But it doesn't take into account the Card -> Checklist -> CheckItem dependency flow
    #I don't know if I should try to account for that here so that tasks can be out of order 
    #or build it into the functions that extend apiCaller.
    for key, value in readTasks.items():
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

    #Clear the lists of returned items at the end of each task, before the next task starts.
    listReturnedChecklists.clear()
    listReturnedCheckItems.clear()
            
#Get the information on Lists
def readLists():
    print('Reading Lists...')
    listTrelloLists.clear()
    listTrelloLists.extend(getListIds())
    
    for i in range(len(listTrelloLists)):
        tempDict = {listTrelloLists[i].get('name'): i}
        dictTrelloLists.update(tempDict)
        i += 1
    
    return dictTrelloLists, listTrelloLists

#get the information on Labels
def readLabels():
    print('Reading Labels...')
    listTrelloLabels.clear()
    listTrelloLabels.extend(getLabelIds())

    for i in range(len(listTrelloLabels)):
        tempDict = {listTrelloLabels[i].get('name'): i}
        dictTrelloLabels.update(tempDict)
        i += 1
    
    return dictTrelloLabels, listTrelloLabels

#Get the {option}s for the "Epic" CustomField
def getEpicOptions():
    print('Getting a list of options for the Epic field...')
    #Make sure getCustomFields() has been run at least once
    listCustomFields = getCustomFields()

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
    listEpicOptions = []
    for b in range(len(epicOptions)):
        tempDict = {'id': epicOptions[b].get('id'), 'value': epicOptions[b].get('value')}
        listEpicOptions.append(tempDict)
        b += 1

    return listEpicOptions

#Build a "Create Card" request and feed it to apiCaller
def createCard(newCardDetails: dict):
    print('Building a new Card...')
    #Instantiate local variables and clear lastReturnedCard{}
    requestDetails = newCardDetails.get('request')
    idList = newCardDetails.get('idList')
    idLabels = newCardDetails.get('idLabels') 
    nameLabels = requestDetails.get('nameLabels')
    nameList = requestDetails.get('nameList')
    listIdLabels = []
    lastReturnedCard.clear()
    
    #Variables to hold values that can't be set by Create Card and require an implicit update
    idCustomField = requestDetails.get('idCustomField')
    nameCustomField = requestDetails.get('nameCustomField')
    valueCustomField = requestDetails.get('valueCustomField')   
    newCardCover = newCardDetails.get('cover')    
    

    #Get the List ID if there is a named List, but no specified IDs
    if idList is None:
        if nameList is None:
            print('Error')
            #Need to build actual error-handling here
            pass
        else:
            newIndex = dictTrelloLists.get(nameList)
            newList = listTrelloLists[newIndex]
            newListId = newList.get('id')
            newCardDetails.update(idList=newListId)

    #Get the Label IDs if there are named labels, but no specified IDs
    if idLabels is None:
        if nameLabels is None:
            print('Error')    
            #Need to build actual error-handling here
            pass
        else:
            for i in range(len(nameLabels)):
                searchLabel = nameLabels[i]
                labelIndex = dictTrelloLabels.get(searchLabel)
                listIdLabels.append(listTrelloLabels[labelIndex].get('id'))
                i += 1
            newCardDetails.update(idLabels=listIdLabels)

    del newCardDetails['request']

    #Strip the cover if it's present
    if newCardCover is None:
        newCardJson = newCardDetails
    else:
        del newCardDetails['cover']
        newCardJson = newCardDetails

    #Transmit the Create Card request
    newCardResponse = postNewCard(newCardJson)
    responseMsg = newCardResponse[0]
    returnedCard = newCardResponse[1]

    #Perform implicit updates for card details that can't be added during Create
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

#Build an "Update Card" rquest and feed it to apiCaller
def updateCard(updateCardDetails: dict):
    print('Building an Update Card request...')
    #Instantiate local variables
    requestDetails = updateCardDetails.get('request')
    idCard = requestDetails.get('idCard') 
    idCustomField = requestDetails.get('idCustomField')
    idList = updateCardDetails.get('idList')
    idLabels = updateCardDetails.get('idLabels')    
    nameCustomField = requestDetails.get('nameCustomField')
    nameLabels = requestDetails.get('nameLabels')
    nameList = requestDetails.get('nameList')
    valueCustomField = requestDetails.get('valueCustomField')
    jobExtensions = updateCardDetails.get('jobExtensions')
    idValue = None
    listIdLabels = []

    #Get the Card ID to update if 'idCard' is 'self'
    if idCard is None:
        print('Error: no Card ID provided')
        #Need to build some actual error handling here
        pass
    elif idCard == 'self':
        idCard = lastReturnedCard.get('id')
    elif idCard == 'list':
        makeIterativeUpdateCard(updateCardDetails)
        return

    #Get the Custom Field ID to update if 'idCustomField' is empty but a custom field is named.
    if idCustomField is None:
        if nameCustomField is None:
            pass    #move on, we don't need to do anything with customfields
        
        #Get the {id, name}s of customFields, iterate through the list, and get the id of the matching name
        else:
            customFields = getCustomFieldIds()
            for i in range(len(customFields)):
                if customFields[i].get('name') == nameCustomField:
                    idCustomField = customFields[i].get('id')
                i += 1

    #Get the List ID if 'idList' is empty but a new list is named
    if idList is None:
        if nameList is None:
            pass
        else:
            newIndex = dictTrelloLists.get(nameList)
            newList = listTrelloLists[newIndex]
            newListId = newList.get('id')
            updateCardDetails.update(idList=newListId)

    #Get the Label IDs to update if 'idLabels' is empty but there are named Labels
    if idLabels is None:
        if nameLabels is None:
            pass
        else:
            for i in range(len(nameLabels)):
                searchLabel = nameLabels[i]
                labelIndex = dictTrelloLabels.get(searchLabel)
                listIdLabels.append(listTrelloLabels[labelIndex].get('id'))
                i += 1
            updateCardDetails.update(idLabels=listIdLabels)

    #Make sure we only try to handle Custom Field values in a valid way
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

    #Call Extensions if they're requested
    if jobExtensions is not None:
        for i in range(len(jobExtensions)):
            extensionCall = jobExtensions[i]

            enrichedData = eval(extensionCall)
            updateCardDetails.update(enrichedData)
            i += 1
        

    #Some cleanup
    del updateCardDetails['request']
    lastReturnedCard.clear()
    updateCardJson = updateCardDetails

    #Transmit the Update Card requeest
    updateCardResponse = putUpdateCard(updateCardJson, idCard)
    responseMsg = updateCardResponse[0]
    returnedCard = updateCardResponse[1]

    lastReturnedCard.update(returnedCard)
    return returnedCard

#Build a "Create Checklist" request and feed it to apiCaller
def createChecklist(newChecklistDetails: dict):
    print('Building a new Checklist...')
    idCard = newChecklistDetails.get('idCard')
    lastReturnedChecklist.clear()

    if idCard is None:
        pass
    elif idCard == 'self':
        idCard = lastReturnedCard.get('id')

    newChecklistDetails.update(idCard=idCard)
    newChecklistJson = newChecklistDetails
    newChecklistResponse = postNewChecklist(newChecklistJson)
    responseMsg = newChecklistResponse[0]
    returnedChecklist = newChecklistResponse[1]

    lastReturnedChecklist.update(returnedChecklist)
    listReturnedChecklists.append(lastReturnedChecklist)
    return returnedChecklist

#Build a "Create CheckItem" request and feed it to apiCaller
def createCheckItem(newCheckItemDetails: dict):
    print('Building a new Check Item...')
    checkItemRequest = newCheckItemDetails.get('request')
    idChecklist = checkItemRequest.get('idChecklist')

    if idChecklist is None:
        pass
    elif idChecklist == 0:
        idChecklist = lastReturnedChecklist.get('id')

    del newCheckItemDetails['request']
    
    newCheckItemJson = newCheckItemDetails
    newCheckItemResponse = postNewCheckItem(newCheckItemJson, idChecklist)
    responseMsg = newCheckItemResponse[0]
    returnedCheckItem = newCheckItemResponse[1]

    listReturnedCheckItems.append(returnedCheckItem)
    return returnedCheckItem

#Build an "Update Checklist request and feed it to apiCaller"
def updateChecklist(updateChecklistDetails: dict):
    print("The API Caller does not currently have Update Checklist functionality.")
    pass

#Build an "Update CheckItem" request and feed it to apiCaller
def updateCheckItem(updateCheckItemDetails: dict):
    print("The API Caller does not currently have Update Checklist Item functionality.")
    pass

#Normalize requests to use IDs instead of Names #TO DO
def normalizeRequestDetails(requestDetails: dict):
    #Get the nested if blocks from createCard(), updateCard(), createChecklist(), and createCheckItem()
    #Refactor them to work in a standard way
    #Use them to update requestDetails
    #Replace them with calls to this function
    return requestDetails

#Create a new dict to feed updateCard() when the New Card task contains elements that Trello doesn't add on creation
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

#Use a list to do generate updateCard() calls for each card in the list
def makeIterativeUpdateCard(listCardDetails: dict):
    print('Starting an Iterative Update proces...')
    requestDetails = listCardDetails.get('request')
    idList = listCardDetails.get('idList')
    nameList = requestDetails.get('nameList')
    listIdCards = []

    #Get the List ID if 'idList' is empty but a new list is named
    if idList is None:
        if nameList is None:
            pass
        else:
            newIndex = dictTrelloLists.get(nameList)
            newList = listTrelloLists[newIndex]
            idList = newList.get('id')
            listCardDetails.update(idList=idList)
    
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

#Main function
def main():
    fetchTaskList(f"{sys.path[0]}{os.sep}tasklist.yml") 
    readLists()
    readLabels()
    parseTaskList()

if __name__ == '__main__':
    main()