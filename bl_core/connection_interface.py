import asyncio
import json
import re
import time
import os, sys

from flask import Flask, Response, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocketError
from rasa.core.agent import Agent
from rasa.core.channels import UserMessage
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.utils.endpoints import EndpointConfig
from rasa.core.tracker_store import MongoTrackerStore
from rasa.core.domain import Domain

from .config import load_config
from .message import MessageExecutor

from .tracker import Tracker
from .user_map import (isPause, pause_user, send_message, store_user,
                      user_map, UserTracker, update_lang)
from urllib import parse
from hashlib import md5



app = Flask(__name__)
app.debug = True

# Init message sender executor
message_exec = MessageExecutor()
# Load all send methods classes
message_exec.load()

config = load_config()
host,port='0.0.0.0',config['websocket']['port']
dashlog = Tracker(config['dashbot']['api'],config['dashbot'][config["template"]["module"]]['api_key'])

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
            agent_ar = Agent.load('./models/core/core.tar.gz',
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
    dashlog.log("outgoing", None, userID,queryText=req_data['text'],intent_name='Human In The Loop')
    if not isPause(userID):
        pause_user(userID)
    send_message(userID, req_data['text'])
    return Response("OK")

@app.route("/hello")
def hello():
    return "OK"


def authorized_connection(environ):
    try:
        if environ is not None:
            query = parse.parse_qs(environ['QUERY_STRING'])
            token = query.get('token', None)
            timestamp = query.get('timestamp', None)
            hashed = md5((str(timestamp[0])+"THIS_IS_SECRET_KEY_PLEASE_KEEP_IT_AS_A_SECRET").encode())
            if token is not None and timestamp is not None:
                if (hashed.hexdigest() == token[0]):
                    return True
            return False
        else:
            return True
    except Exception as e:
        print(f"Can't authorized connection: {e.args}")
        return False


def wsgi_app(environ, start_response):
    path = environ["PATH_INFO"]  
    if '/ws/' in path:
        try:  
            if authorized_connection(environ):
                handle_websocket(environ["wsgi.websocket"], path)
            else:
                raise Exception("Unauthorized")
        except Exception as e:
            print(e)
            print("Stop Connection")
        return []
    else:  
        return app(environ, start_response)


def handle_websocket(websocket, path):
    path_split = path.split('/')
    lang = path_split[len(path_split)-1]
    agent = agent_all.get(lang, None)
    session_message = None
    if agent is not None:
        if websocket is not None:
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
                    msgRasa = UserMessage(sender_id=session_message,text=text_message)
                    if text_message == "/restart" or text_message == "restart":
                        pause_user(session_message, pause=False)

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    t = loop.run_until_complete(agent.log_message(msgRasa))
                    slots = t.current_slot_values()
                    update_lang(session_message, slots['language'])

                    if not isPause(session_message):
                        responses = loop.run_until_complete(agent.handle_message(msgRasa))
                        for response in responses:
                            log_message = ""
                            if 'text' in response.keys():
                                log_message = response['text']
                            else:
                                log_message = json.dumps(response['attachment'], indent=3)
                            dashlog.log("outgoing", response,response['recipient_id'])
                            time.sleep(1)
                            websocket.send(json.dumps(message_exec.send_typing()))
                            time.sleep(1.5)
                            parsed_message = message_exec.parse(response)
                            websocket.send(json.dumps(parsed_message))
                    else:
                        dashlog.log("incoming", None, session_message,queryText=text_message,intent_name='Human In The Loop')
            except KeyboardInterrupt:
                sys.exit()
            except WebSocketError as ex:
                print(ex)
    else:
        raise Exception(f"Agent not found, agent: {agent}")
        

if __name__ == '__main__':
    userTrack = UserTracker()
    userTrack.start()
    http_server = WSGIServer((host,port), wsgi_app, handler_class=WebSocketHandler)
    print('Server started at %s:%s'%(host,port))
    http_server.serve_forever()