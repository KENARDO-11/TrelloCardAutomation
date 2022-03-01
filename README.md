# TrelloCardAutomation

## TO DO:
* Add features to the Tasklist Parser
* Improved logic for Implicit Updates
* Implement error-handling
* Cover color key binding
* Handling for card -> checklist -> checkitem dependency flow
* More implicit update options
* General cleanup

## Scripts
* apiCaller.py - Interfaces with Trello API using environment variables
* apiScheduler.py - Parses tasklists and tasks and implements apiCaller functions accordingly

## Tasklist
tasklist.yml is parsed by apiScheduler to determine what tasks to perform during a given run.

## Tasks
This directory contains the YAML files that represent the configuration of individual cards.
