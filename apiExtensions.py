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

# Globals can go here if needed:
read_lists = apiScheduler.read_lists()
dict_lists = read_lists[0]
list_lists = read_lists[1]

# Determine whether a Card represents a Delivered package and report back to the parent function
def package_tracking(idCard: str):
    print(f"Starting {sys._getframe().f_code.co_name} for Card {idCard}")
    
    #Initialize enriched_card_details
    enriched_card_details = {
        'request': {
            'idCard': idCard
        },
        'closed': False
    }

    plugin_data_response = get_plugin_data(idCard)
    if len(plugin_data_response) == 0:
        return enriched_card_details

    plugin_value = json.loads(plugin_data_response[0].get('value'))
    plugin_status = plugin_value.get('statuses')[0]
    
    if plugin_status.get('status') == 'DELIVERED':
        enriched_card_details.update(closed=True)

    return enriched_card_details

# Determine whether a Card has been in the 'To Do' list longer than 10 days and report back to the parent function
def stale_cards(idCard: str, idList: str):
    print(f"Starting {sys._getframe().f_code.co_name} for Card {idCard}")

    #Initialize enriched_card_details
    enriched_card_details = {
        'request': {
            'idCard': idCard
        },
        'idList': idList
    }

    #Other useful locals
    list_filters = [
        'updateCard',
        'createCard',
        'convertCardFromCheckItem',
        'copyCard',
        'moveCardToBoard'
    ]
    to_do_date = ''

    #Get the idList for Backburner
    backburner_index = dict_lists.get('Backburner')
    backburner_id_list = list_lists[backburner_index].get('id')

    action_response = get_card_actions(idCard, list_filters)
    del list_filters[0]

    for i in range(len(action_response)):
        temp_dict = action_response[i]

        if temp_dict.get('type') in list_filters:
            to_do_date = temp_dict.get('date')
            break
        else:
            temp_dict_data = temp_dict.get('data')
            if 'list_after' in temp_dict_data:
                temp_list_after = temp_dict_data.get('list_after')
                temp_id_list = temp_list_after.get('id')
                if temp_id_list == idList:
                    to_do_date = temp_dict.get('date')
                    break
        i += 1

    datetime_to_do_date = isoparse(to_do_date)
    datetime_now = datetime.datetime.now().astimezone(tz=datetime.timezone.utc)

    # time_in_to_do = datetime_now.date() - datetime_to_do_date.date()
    time_in_to_do = datetime_now - datetime_to_do_date
    days_in_to_do = time_in_to_do.days

    print(f'Card has been in To Do status for {days_in_to_do} days')
    if days_in_to_do >= 10:
        enriched_card_details.update(idList=backburner_id_list)

    return enriched_card_details