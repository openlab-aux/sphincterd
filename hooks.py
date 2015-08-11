#
# hooks will be executed when the corresponding event occurs
# 

def open_hook():
    pass

def closed_hook():
    pass

def failure_hook():
    pass

def timer_hook(status):
    import requests
    import json
    
    logging.info("starting timer_hook")
    
    api_status = False
    if status == "UNLOCKED" or status == "OPEN":
        api_status = True
    
    url = "https://api.openlab-augsburg.de/13/edit/door/"
    data = {
        "token": "n8TvfFOciPrcJ67Vn3tTlI7",
        "status": api_status
    }
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain'
    }
    try:
        requests.post(url, data=json.dumps(data), headers=headers)
    except Exception:
	pass
 
    logging.info("finishing timer_hook")
