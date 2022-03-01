# TrelloCardAutomation

## TO DO:
* Implement the Tasklist Parser
* Improved logic for Implicit Updates
* Implement error-handling

## Scripts
* apiCaller.py - Interfaces with Trello API using environment variables
* apiScheduler.py - Parses tasklists and tasks and implements apiCaller functions accordingly

## Tasklist
tasklist.yml is parsed by apiScheduler to determine what tasks to perform during a given run.

## Tasks
This directory contains the YAML files that represent the configuration of individual cards.
