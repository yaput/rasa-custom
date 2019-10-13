import asyncio
import json
import re
import time
import os

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

from .config import load_config
from .core_util import parse_bot_response, send_typing

from .tracker import Tracker
from .user_map import (isPause, pause_user, send_message, store_user,
                      user_map, UserTracker)

app = Flask(__name__)
app.debug = True


config = load_config()
host,port='0.0.0.0',config['websocket']['port']
dashlog = Tracker(config['dashbot'][config["template"]["module"]]['api_key'], 'web')

action_endpoint = EndpointConfig(url=config['server']['actions_endpoint'])
nlg_endpoint = EndpointConfig(url=config['server']['nlg_endpoint'])
domain = Domain.load('domain.yml')
db_conf = config['bluelog']
mongo_tracker = MongoTrackerStore(domain, host=db_conf['host'], db=db_conf['db'], username=db_conf['username'], password=db_conf['password'], auth_source=db_conf['authsource'], collection=config['template']['module'])

agent_all = {}

try:
    if os.path.isdir('./models/nlu'):
        if os.path.isdir('./models/nlu/idn'):
            nlu_interpreter_idn = RasaNLUInterpreter('./models/nlu/idn/')
            agent_idn = Agent.load('./models/core/core.tar.gz',
                                   interpreter=nlu_interpreter_idn,
                                   action_endpoint=action_endpoint,
                                   generator=nlg_endpoint,
                                   tracker_store=mongo_tracker)
            agent_all["idn"] = agent_idn
        else:
            pass
        if os.path.isdir('./models/nlu/en'):
            nlu_interpreter_en = RasaNLUInterpreter('./models/nlu/en/')
            agent_en = Agent.load('./models/core/core.tar.gz',
                                  interpreter=nlu_interpreter_en,
                                  action_endpoint=action_endpoint,
                                  generator=nlg_endpoint,
                                  tracker_store=mongo_tracker)
            agent_all["en"] = agent_en
        else:
            pass
        if os.path.isdir('./models/nlu/ar'):
            nlu_interpreter_ar = RasaNLUInterpreter('./models/nlu/ar/')
            agent_ar = Agent.load('./models/core/core.tar.'
                                  'gz',
                                  interpreter=nlu_interpreter_ar,
                                  action_endpoint=action_endpoint,
                                  generator=nlg_endpoint,
                                  tracker_store=mongo_tracker)
            agent_all["ar"] = agent_ar
        else:
            pass
        if os.path.isdir('./models/nlu/er'):
            nlu_interpreter_er = RasaNLUInterpreter('./models/nlu/er')
            agent_er = Agent.load('./models/core/core.tar.gz',
                                  interpreter=nlu_interpreter_er,
                                  action_endpoint=action_endpoint,
                                  generator=nlg_endpoint,
                                  tracker_store=mongo_tracker)
            agent_all["er"] = agent_er
        else:
            pass
    else:
        raise Exception("Couldn't find path ./models/nlu")
except Exception as e:
    print('Message: '+repr(e))

"""agent_all = {"idn": agent_idn,
             "en": agent_en,
             "ar": agent_ar,
             "er": agent_er}"""


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
    dashlog.log(userID, intent_name='Human In The Loop', queryText=req_data['text'])
    if not isPause(userID):
        pause_user(userID)
    send_message(userID, req_data['text'])
    return Response("OK")


def wsgi_app(environ, start_response):  
    path = environ["PATH_INFO"]  
    if path == "/ws/en":
        try:  
            handle_websocket(environ["wsgi.websocket"], "en")
        except Exception as e:
            print(e)
            print("Stop Connection")
        return []
    elif path == '/ws/idn':
        try:  
            handle_websocket(environ["wsgi.websocket"], "idn")
        except Exception as e:
            print(e)
            print("Stop Connection")
        return []
    elif path== '/ws/ar':
        try:
            handle_websocket(environ["wsgi.websocket"], "ar")
        except Exception as e:
            print(e)
            print("Stop Connection")
        return []
    elif path == '/ws/er':
        try:
            handle_websocket(environ["wsgi.websocket"], "er")
        except Exception as e:
            print(e)
            print("Stop Connection")
        return []

    else:  
        return app(environ, start_response)


def handle_websocket(websocket, lang):
    agent = agent_all
    if lang == "idn":
        agent = agent_all['idn']
    elif lang == "en":
        agent = agent_all['en']
    elif lang == "ar":
        agent = agent_all['ar']
    elif lang == "er":
        agent = agent_all['er']
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
                if text_message == "/restart" or text_message == "restart":
                    pause_user(session_message, pause=False)

                if not isPause(session_message):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    responses = loop.run_until_complete(agent.handle_message(msgRasa))
                    for response in responses:
                        log_message = ""
                        if 'text' in response.keys():
                            log_message = response['text']
                        else:
                            log_message = json.dumps(response['attachment'], indent=3)
                        dashlog.log(response['recipient_id'], intent_name="", queryText=log_message)
                        time.sleep(1)
                        websocket.send(json.dumps(send_typing()))
                        time.sleep(1.5)
                        parsed_message = parse_bot_response(response)
                        websocket.send(json.dumps(parsed_message))
                else:
                    dashlog.log(session_message, intent_name="Human In The Loop", queryText=text_message, agent=False)
        except WebSocketError as ex:
            print(ex)


if __name__ == '__main__':
    userTrack = UserTracker()
    userTrack.start()
    http_server = WSGIServer((host,port), wsgi_app, handler_class=WebSocketHandler)
    print('Server started at %s:%s'%(host,port))
    http_server.serve_forever()