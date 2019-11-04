import json, time
from .config import load_config

from .message import MessageExecutor

config = load_config()
template_message = None
with open('%s' % config["response"]["path"], encoding='utf8') as temp:
    template_message = json.load(temp)

# Init message sender executor
message_exec = MessageExecutor()
# Load all send methods classes
message_exec.load()

user_map = {}

def store_user(userID, websocket):
    if userID not in user_map.keys():
        user_map[userID] = {
            "paused": False,
            "conn": websocket,
            "last_active": time.time()
        }
    else:
        user_map[userID]["last_active"] = time.time()

def pop_user(userID):
    try:
        del user_map[userID]
    except:
        return 
    

def isPause(userID):
    try:  
        return user_map[userID]['paused']
    except:
        return False 

def send_message(userID, message):
    if not user_map[userID]["paused"]:
        user_map[userID]["paused"] = True
    try:
        user_map[userID]['conn'].send(json.dumps({
            'type':'message',
            'text':message,
            'user':userID,
            'channel':'socket'
        }))
    except:
        print("Closed Connection")
        return

def pause_user(userID, pause=True):
    user = None
    try:
        user = user_map[userID]
    except:
        user_map[userID] = {}
        user = user_map[userID]
    user['paused'] = pause

def update_lang(userID, lang):
    user = None
    try:
        user = user_map[userID]
    except:
        user_map[userID] = {}
        user = user_map[userID]
    user['language'] = lang

import datetime
import asyncio
import threading
class UserTracker(threading.Thread):
    def __init__(self):
        super(UserTracker, self).__init__()

    def run(self):
        self.loop()

    def loop(self):
        while True:
            time.sleep(5.0)
            self.deltaTime()

    def deltaTime(self):
        trash = []
        for u in user_map:
            try:
                time_active = user_map[u]["last_active"]
            except:
                user_map[u]['last_active'] = time.time()
                time_active = user_map[u]['last_active']
            t1 = time_active
            t2 = time.time()
            duration = t2 - t1
            minutes = duration // 60 % 60
            if minutes >= 10: #Minute
                trash.append(u)

        for t in trash:
            response = {
                "recipient_id": t,
                "attachment": template_message['utter_session_timeout'][user_map[t]['language']]['content']
            }
            try:
                user_map[t]['conn'].send(json.dumps(message_exec.parse(response)))
            except Exception as e:
                print(e.args)
                pass
            pop_user(t)


