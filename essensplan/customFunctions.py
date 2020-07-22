from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta


def getMonday(choosenDate):
    """ 
    getMonday() gibt das Datum des letzten Montag des gegebenen Datum zurück
    """
    choosenDate
    today = choosenDate.weekday()
    dateMonday = choosenDate-timedelta(days=today)
    return dateMonday

def addTodoListToWunderlist(todo_string:str):
    # Fügt eine Todo der Liste "wochenplan" hinzu
    import requests
    import json

    access_token = 'bafaf35af71f62ee44b6f9a1d8f9079f236e982d9d310ee89d75ff04d2cd'
    client_id = '41e835d6b9c4a9c911d7'
    list_id = '396960287'

    headers={'X-Access-Token': access_token, 'X-Client-ID': client_id, 'Content-Type' : 'application/json'}
    todo = {
        "list_id": 396960287,
        "title": todo_string,
        "assignee_id": 123,
        "completed": False,
        "starred": False
    }  
    data_json = json.dumps(todo)
    # print(data_json)
    # print("Querying Wunderlist...")
    f = requests.post('https://a.wunderlist.com/api/v1/tasks', headers=headers, data=data_json)
    # print("Done! Code: "+str(f.status_code))
    j = json.loads(f.text)
    # print(j)
    #print(todo_string)
    return f.status_code
