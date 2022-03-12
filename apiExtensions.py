#This script adds extended capabilities to apiScheduler in an interchangeable way.

import yaml
from time import sleep
import json
import datetime
import os
import sys
from dateutil.parser import isoparse
from dotenv import load_dotenv
from apiCaller import *
import apiScheduler

#Globals can go here if needed:
readLists = apiScheduler.readLists()
dictLists = readLists[0]
listLists = readLists[1]

#Determine whether a Card represents a Delivered package and report back to the parent function
def packageTracking(idCard: str):
    print(f"Starting {sys._getframe().f_code.co_name} for Card {idCard}")
    
    #Initialize enrichedCardDetails
    enrichedCardDetails = {
        'request': {
            'idCard': idCard
        },
        'closed': False
    }

    pluginDataResponse = getPluginData(idCard)
    if len(pluginDataResponse) == 0:
        return enrichedCardDetails

    pluginValue = json.loads(pluginDataResponse[0].get('value'))
    pluginStatus = pluginValue.get('statuses')[0]
    
    if pluginStatus.get('status') == 'DELIVERED':
        enrichedCardDetails.update(closed=True)

    return enrichedCardDetails

#Determine whether a Card has been in the 'To Do' list longer than 10 days and report back to the parent function
def staleCards(idCard: str, idList: str):
    print(f"Starting {sys._getframe().f_code.co_name} for Card {idCard}")

    #Initialize enrichedCardDetails
    enrichedCardDetails = {
        'request': {
            'idCard': idCard
        },
        'idList': idList
    }

    #Other useful locals
    listFilters = [
        'updateCard',
        'createCard',
        'convertCardFromCheckItem',
        'copyCard',
        'moveCardToBoard'
    ]
    toDoDate = ''

    #Get the idList for Backburner
    backburnerIndex = dictLists.get('Backburner')
    backburneridList = listLists[backburnerIndex].get('id')

    actionResponse = getCardActions(idCard, listFilters)
    del listFilters[0]

    for i in range(len(actionResponse)):
        tempDict = actionResponse[i]

        if tempDict.get('type') in listFilters:
            toDoDate = tempDict.get('date')
            break
        else:
            tempDictData = tempDict.get('data')
            if 'listAfter' in tempDictData:
                tempListAfter = tempDictData.get('listAfter')
                tempIdList = tempListAfter.get('id')
                if tempIdList == idList:
                    toDoDate = tempDict.get('date')
                    break
        i += 1

    datetimeToDoDate = isoparse(toDoDate)
    datetimeNow = datetime.datetime.now().astimezone(tz=datetime.timezone.utc)

    # timeInToDo = datetimeNow.date() - datetimeToDoDate.date()
    timeInToDo = datetimeNow - datetimeToDoDate
    daysInToDo = timeInToDo.days

    print(f'Card has been in To Do status for {daysInToDo} days')
    if daysInToDo >= 10:
        enrichedCardDetails.update(idList=backburneridList)

    return enrichedCardDetails