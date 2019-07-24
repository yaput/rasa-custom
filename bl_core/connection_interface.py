import asyncio
import datetime
import json
import re
import signal
import sys
import time
from pprint import pprint

import requests
import websockets
from flask import Flask, Response, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocketError
from rasa_core.agent import Agent
from rasa_core.channels import UserMessage
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.utils import EndpointConfig
from rasa_core.tracker_store import MongoTrackerStore
from rasa_core.domain import Domain

from .blue_config import load_config
from .core_util import parse_bot_response, send_typing

from pydashbot.tracker import Tracker
from user_map import (isPause, pause_user, pop_user, send_message, store_user,
                      user_map, UserTracker, update_lang)

app = Flask(__name__)
app.debug = True


config = load_config()
host,port='0.0.0.0',config['websocket']['port']
dashlog = Tracker(config['dashbot']['api'],config['dashbot'][config["template"]["module"]]['api_key'])



nlu_interpreter = RasaNLUInterpreter('./models/'+config['template']['module']+'/nlu/global/latest')
action_endpoint = EndpointConfig(url=config['server']['actions_endpoint'])
nlg_endpoint = EndpointConfig(url=config['server']['nlg_endpoint'])
domain = Domain.load('./data/'+config['template']['module']+'/domain.yml')
db_conf = config['bluelog']
mongo_tracker = MongoTrackerStore(domain, host=db_conf['host'], db=db_conf['db'], username=db_conf['username'], password=db_conf['password'], auth_source=db_conf['authsource'], collection=config['template']['module'])

agent = Agent.load('./models/'+config['template']['module']+'/dialogue', interpreter=nlu_interpreter, action_endpoint=action_endpoint,generator=nlg_endpoint, tracker_store=mongo_tracker)


@app.route("/pause", methods=['POST'])
def pause_bot():
    req_data = request.get_json()
    pause_id = req_data['userId']
    pause = req_data['paused']
    pause_user(pause_id, pause)
    print(user_map)
    return Response("OK")

@app.route("/liveperson", methods=["POST"])
def liveperson():
    req_data = request.get_json()
    userID = req_data['userId']
    dashlog.log("outgoing", None, userID,queryText=req_data['text'],intent_name='Human In The Loop')
    if not isPause(userID):
        pause_user(userID)
    send_message(userID, req_data['text'])
    return Response("OK")

def wsgi_app(environ, start_response):  
    path = environ["PATH_INFO"]  
    if path == "/ws":
        try:  
            handle_websocket(environ["wsgi.websocket"])
        except:
            print("Stop Connection")
        return []
    else:  
        return app(environ, start_response)  
def handle_websocket(websocket):
    session_message = None
    if websocket != None:
        try:
            while True:
                msg = websocket.receive()
                try:
                    message = json.loads(msg)
                except:
                    break
                session_message = message['user']
                store_user(session_message, websocket)
                text_message = message['text']
                if '[' in text_message and ']' in text_message:
                    text_message = '/submit_symptom{"symptom": "'+text_message.replace('[','').replace(']', '').replace('"', "")+'"}'

                welcome = re.search("_hi_(.*)_((e|E)ng(.*)|(a|A)rab(.*))",text_message)
                if welcome:
                    split_txt = text_message.split("_")
                    text_message = '/session_started{"language": "'+split_txt[3]+'"}'

                msgRasa = UserMessage(sender_id=session_message,text=text_message)
                t = agent.log_message(msgRasa)
                slots = t.current_slot_values()
                update_lang(session_message, slots['language'])
                
                if text_message == "/restart" or text_message == "restart":
                    pause_user(session_message, pause=False)

                if not isPause(session_message):
                    responses = agent.handle_message(msgRasa)
                    for response in responses:
                        dashlog.log("outgoing", response,response['recipient_id'])
                        time.sleep(1)
                        websocket.send(json.dumps(send_typing()))
                        time.sleep(1.5)
                        parsed_message = parse_bot_response(response)
                        websocket.send(json.dumps(parsed_message))
                else:
                    dashlog.log("incoming", None, session_message,queryText=text_message,intent_name='Human In The Loop')
        except WebSocketError as ex:
            print(ex)

if __name__ == '__main__':
    userTrack = UserTracker()
    userTrack.start()
    http_server = WSGIServer((host,port), wsgi_app, handler_class=WebSocketHandler)
    print('Server started at %s:%s'%(host,port))
    http_server.serve_forever()
