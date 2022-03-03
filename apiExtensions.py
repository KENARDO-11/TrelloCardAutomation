#This script adds extended capabilities to apiScheduler in an interchangeable way.

import yaml
from time import sleep
import json
import requests
import datetime
import os
import sys
from dotenv import load_dotenv
from apiCaller import *

#Globals can go here if needed:



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



