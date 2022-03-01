# TrelloCardAutomation

## TO DO:
* Add features to the Tasklist Parser
* Improved logic for Implicit Updates
* Implement error-handling
* Cover color key binding
* Handling for card -> checklist -> checkitem dependency flow
* More implicit update options
* General cleanup
* Future: integration with a Trello Card Button that invokes a webhook to export the card and crunch it into a yaml task
    * Future Future: Daily and Weekly buttons that also update tasklist.yml

## Scripts
* apiCaller.py - Interfaces with Trello API using environment variables
* apiScheduler.py - Parses tasklists and tasks and implements apiCaller functions accordingly

## Tasklist
tasklist.yml is parsed by apiScheduler to determine what tasks to perform during a given run.

## Tasks
This directory contains the YAML files that represent the configuration of individual cards.
