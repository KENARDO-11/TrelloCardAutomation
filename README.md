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
* apiExtensions.py - Performs data enrichment required to fulfill specific tasks beyond the basic functionality

## Tasklist
tasklist.yml is parsed by apiScheduler to determine what tasks to perform during a given run.

## Tasks
This directory contains the YAML files that represent the configuration of individual cards.

## Extensions
Tasks can contain a list of 'jobExtensions', which are executable calls to the apiExtensions script. This scheme is intended to provide extensibility, by performing data enrichment to specify capabilities beyond the standard set supported by the API Caller and Scheduler.
Extensions should return a valid body for the kind of API request the parent function is trying to make. (eg When 'Update Card' calls an extension, it should return an acceptable updateCardDetails dict)

### Example use case:
I want to go through all the Cards in a List, determine whether they have Plugin Data that corresponds to a package that has been delivered, and archive the Cards that have, without affecting the Cards that haven't.

### task.yml:
```yaml
---
#Clear any Delivered packages from the tracker
Update Card:
  request:
    idCard: 'list'              
    nameList: 'Package Tracking'             
  closed: true            
  jobExtensions:
  - packageTracking(idCard)
```

### apiExtensions.py
```python
####
def packageTracking(idCard: str)
    doSomething()
    apiCaller.getPluginData(idCard)
    someReturnValue = doSomethingElse()
    return someReturnValue
####
```
The returned value will be used to update() the dict the parent function is operating with, so it should be formatted to achieve the desired result.