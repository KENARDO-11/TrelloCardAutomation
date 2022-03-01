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
import apiCaller


taskList = {}
dictTrelloLists = {}
dictTrelloLabels = {}

listTrelloLists = []
listTrelloLabels = []

lastReturnedCard = {}

#Fetch the list of scheduled Tasks and store it as a dict
def fetchTaskList(filename: str):
    stream = open(filename, 'r')
    taskList.update(yaml.load(stream, yaml.Loader))
    
#Analyze the taskList to determine what tasks need to be performed today, in which order #TO DO
def parseTaskList():



    pass

#Fetch the specified Task YAML file, read it, and call the appropriate functions in order #TO DO
def readTask(filename: str):

    stream = open(filename, 'r')
    readTasks = yaml.load(stream, yaml.Loader)

    numTasks = len(readTasks)

    #I like this logic for iterating through the Task file and pointing to request functions
    #But it doesn't take into account the Card -> Checklist -> CheckItem dependency flow
    #I don't know if I should try to account for that here so that tasks can be out of order 
    #or build it into the functions that extend apiCaller.
    for key, value in readTasks.items():
        if key.__contains__('New'):
            if key.__contains__('Card'):
                createCard(value)
        #     elif key.__contains__('Checklist'):
        #         createChecklist(value)
        #     elif key.__contains__('CheckItem'):
        #         createCheckItem(value)
        #     else:
        #         print(f"Something went wrong. {key} is  not a valid request type.")

        elif key.__contains__('Update'):
            if key.__contains__('Card'):
                updateCard(value)
        #     elif key.__contains__('Checklist'):
        #         updateChecklist(value)
        #     elif key.__contains__('CheckItem'):
        #         updateCheckItem(value)
        #     else:
        #         print(f"Something went wrong. {key} is  not a valid request type.")
        
        else:
            print(f"Something went wrong. {key} is not a valid request type.")
            
#Get the information on Lists
def readLists():
    listTrelloLists.extend(apiCaller.getListIds())
    
    for i in range(len(listTrelloLists)):
        tempDict = {listTrelloLists[i].get('name'): i}
        dictTrelloLists.update(tempDict)
        i += 1
    
    return listTrelloLists

#get the information on Labels
def readLabels():
    listTrelloLabels.extend(apiCaller.getLabelIds())

    for i in range(len(listTrelloLabels)):
        tempDict = {listTrelloLabels[i].get('name'): i}
        dictTrelloLabels.update(tempDict)
        i += 1
    
    return listTrelloLabels

#Build a "Create Card" request and feed it to apiCaller
def createCard(newCardDetails: dict):

    #Instantiate local variables and clear lastReturnedCard{}
    requestDetails = newCardDetails.get('request')
    idList = newCardDetails.get('idList')
    idLabels = newCardDetails.get('idLabels') 
    nameLabels = requestDetails.get('nameLabels')
    nameList = requestDetails.get('nameList')
    listIdLabels = []
    newCardCover = newCardDetails.get('cover')    
    lastReturnedCard.clear()

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

    #Strip the cover and save it for later if needed
    if newCardCover is None:
        newCardJson = newCardDetails
    else:
        del newCardDetails['cover']
        newCardJson = newCardDetails

    #Transmit the Create Card request
    newCardResponse = apiCaller.postNewCard(newCardJson)
    responseMsg = newCardResponse[0]
    returnedCard = newCardResponse[1]

    #Perform implicit updates for card details that can't be added during Create
    if newCardCover is not None:
        #Just gonna hack this together for now for testing
        #It'll make more sense once I add more logic to makeImplicitUpdateCard()
        newElements = {
            'idCustomField': None,
            'nameCustomField': None,
            'valueCustomField': None,
            'cover': newCardCover
        }
        implicitUpdateCard = makeImplicitUpdateCard(returnedCard, newElements)
        print('Performing an implicit update')
        updateCard(implicitUpdateCard)

    lastReturnedCard.update(returnedCard)
    return returnedCard

#Build an "Update Card" rquest and feed it to apiCaller
def updateCard(updateCardDetails: dict):
    
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
    idValue = None
    listIdLabels = []
    
    #Get the Card ID to update if 'idCard' is 'self'
    if idCard is None:
        print('Error: no Card ID provided')
        #Need to build some actual error handling here
        pass
    elif idCard == 'self':
        idCard = lastReturnedCard.get('id')

    #Get the Custom Field ID to update if 'idCustomField' is empty but a custom field is named.
    if idCustomField is None:
        if nameCustomField is None:
            pass    #move on, we don't need to do anything with customfields
        
        #Get the {id, name}s of customFields, iterate through the list, and get the id of the matching name
        else:
            customFields = apiCaller.getCustomFieldIds()
            for i in range(len(customFields)):
                if customFields[i].get('name') == nameCustomField:
                    idCustomField = customFields[i].get('id')
                i += 1

    #Get the List ID if 'idList' is empty but a new list is named
    if idList is None:
        if nameList is None:
            #print('Error')
            #Need to build some actual error handling here
            pass
        else:
            newIndex = dictTrelloLists.get(nameList)
            newList = listTrelloLists[newIndex]
            newListId = newList.get('id')
            updateCardDetails.update(idList=newListId)

    #Get the Label IDs to update if 'idLabels' is empty but there are named Labels
    if idLabels is None:
        if nameLabels is None:
            #print('Error')    
            #Need to build some actual error handling here
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
                epicOptions = apiCaller.getEpicOptions()
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
            updateCardResponse = apiCaller.putUpdateCard(customFieldRequest, idCard)
        else:
            #idCustomField was None, but valueCustomField was not None
            pass

    #Some cleanup
    del updateCardDetails['request']
    lastReturnedCard.clear()
    updateCardJson = updateCardDetails

    #Transmit the Update Card requeest
    updateCardResponse = apiCaller.putUpdateCard(updateCardJson, idCard)
    responseMsg = updateCardResponse[0]
    returnedCard = updateCardResponse[1]

    lastReturnedCard.update(returnedCard)
    return returnedCard

#Build a "Create Checklist" request and feed it to apiCaller #TO DO
def createChecklist(newChecklistDetails: dict):

    # newChecklistJson = {}
    # apiCaller.postNewChecklist(newChecklistJson)
    pass

#Build a "Create CheckItem" request and feed it to apiCaller #TO DO
def createCheckItem(newCheckItemDetails: dict):

    # newCheckItemJson = {}
    # updateChecklistId = ''
    # apiCaller.postNewCheckItem(newCheckItemJson, updateChecklistId)
    pass

#Build an "Update Checklist request and feed it to apiCaller"
def updateChecklist(updateChecklistDetails: dict):
    print("The API Caller does not currently have Update Checklist functionality.")
    pass

#Build an "Update CheckItem" request and feed it to apiCaller
def updateCheckItem(updateCheckItemDetails: dict):
    print("The API Caller does not currently have Update Checklist Item functionality.")
    pass

#Create a new dict to feed updateCard() when the New Card task contains elements that Trello doesn't add on creation
def makeImplicitUpdateCard(cardDetails: dict, newElements: dict):
    
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

# fetchTaskList("C:\\Users\\SUPERDICKS MkVII\\Documents\\Projects\\KENARDONET\\Scripts\\APIs\\Trello\\TrelloCardAutomation\\tasklist.yml") 

readLists()
readLabels()
filename = 'C:\\Users\\SUPERDICKS MkVII\\Documents\\Projects\\KENARDONET\\Scripts\\APIs\\Trello\\TrelloCardAutomation\\Tasks\\feedscirocco.yml'

readTask(filename)
