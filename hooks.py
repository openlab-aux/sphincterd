#
# hooks will be executed when the corresponding event occurs
# 
import logging

def open_hook():
    logging.info("Starting OpenHook")
    import requests
    import json
    url = "https://api.openlab-augsburg.de/13/edit/door/"
    data = {
        "token": "n8TvfFOciPrcJ67Vn3tTlI7",
        "status": True
    }
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain'
    }
    requests.post(url, data=json.dumps(data), headers=headers)
    logging.info("Finishing OpenHook")
    
def closed_hook():
    logging.info("Starting ClosedHook")
    import requests
    import json
    url = "https://api.openlab-augsburg.de/13/edit/door/"
    data = {
        "token": "n8TvfFOciPrcJ67Vn3tTlI7",
        "status": False
    }
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain'
    }
    requests.post(url, data=json.dumps(data), headers=headers)
    logging.info("Finishing ClosedHook")

def failure_hook():
    pass
