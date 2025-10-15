import redis 
import json 

r = redis.Redis(host='localhost', port=6379, db=0 )

def add_message(session_id: str, message: str):
    history = r.get(session_id)
    if history:
        history= json.loads(history)
    else:
        history=[]
    history.append(message)
    r.set(session_id,json.dumps(history))

def get_history(session_id: str):
    history= r.get(session_id)
    if history:
        return json.loads(history)
    return[]
