import asyncio
import json
import logging
import os
import re
import sys
import threading
import time
from hashlib import md5
from urllib import parse

from flask import Flask, Response, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocketError
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from bl_core.facebook_parser import *
from rasa.core.agent import Agent
from rasa.core.channels import UserMessage
from rasa.core.domain import Domain
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.core.tracker_store import MongoTrackerStore
from rasa.utils.endpoints import EndpointConfig

from .config import load_config
from .message import MessageExecutor
from .tracker import Tracker
from .user_map import (UserTracker, isPause, pause_user, send_message,
                       store_user, update_lang, user_map)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('~/logs/connection_interface.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

app = Flask(__name__)
app.debug = True

# Init message sender executor
message_exec = MessageExecutor()
# Load all send methods classes
message_exec.load()

config = load_config()
host, port = '0.0.0.0', config['websocket']['port']
dashlog = Tracker(config['dashbot']['api'], config['dashbot']
                  [config["template"]["module"]]['api_key'])

action_endpoint = EndpointConfig(url=config['server']['actions_endpoint'])
nlg_endpoint = EndpointConfig(url=config['server']['nlg_endpoint'])
domain = Domain.load('domain.yml')
db_conf = config['bluelog']
mongo_tracker = MongoTrackerStore(domain, host=db_conf['host'], db=db_conf['db'], username=db_conf['username'],
                                  password=db_conf['password'], auth_source=db_conf['authsource'], collection=config['template']['module'])

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
            nlu_interpreter_en = RasaNLUInterpreter('./models/nlu/en/latest')
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


class HandleFacebookMessage(threading.Thread):
    def __init__(self, sender_id, used_message, agent_fb):
        self.sender_id = sender_id
        self.used_message = used_message
        self.agent = agent_fb
        super(HandleFacebookMessage, self).__init__()

    def run(self):
        msgRasa = UserMessage(sender_id=self.sender_id, text=self.used_message)
        session_message = self.sender_id
        t = self.agent.log_message(msgRasa)
        print(" this is t, ", t)
        slots = t.current_slot_values()
        print("this is the slots, ", slots)
        if slots['language'] == None:
            slots['language'] = 'en'
        updated = update_lang(session_message, slots['language'])
        if self.used_message == "/restart" or self.used_message == "restart":
            pause_user(self.sender_id, pause=False)

        if not isPause(self.sender_id):
            responses = self.agent.handle_message(msgRasa)
            for response in responses:
                dashlog.log("outgoing", response, response['recipient_id'])
                fb_parse_bot_response(self.sender_id, response)


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


def load_facebook_agent(nlu_interpreter_en, action_endpoint, nlg_endpoint, mongo_tracker):
    agent_fb = Agent.load('./models/' + config['template']['module'] + '/dialogue_fb', interpreter=nlu_interpreter_en,
                          action_endpoint=action_endpoint, generator=nlg_endpoint, tracker_store=mongo_tracker)
    return agent_fb


@app.route("/fbWebhook", methods=["GET", "POST"])
def handle_facebook_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    # get whatever message a user sent the bot
    else:
        try:
            input_msg = request.get_json()
            entry = input_msg.get('entry', None)
            msg = entry[0].get('messaging', None)
            msg_payload = msg[0]
            sender_id = msg_payload['sender']['id']
            store_user(sender_id, None)
            message = msg_payload.get('message', None)
            postback = msg_payload.get('postback', None)
            used_message = None
            if 'delivery' not in msg[0].keys():
                if message != None:
                    msg_key = message.keys()
                    if 'is_echo' in msg_key or 'read' in msg_key or 'delivery' in msg_key:
                        used_message = None
                        pass
                    elif 'quick_reply' in msg_key:
                        used_message = message['quick_reply']['payload']
                    elif 'text' in msg_key:
                        used_message = message.get('text', None)
                    elif 'attachments' in msg_key:
                        pass
                elif postback != None:
                    used_message = postback['payload']

                if used_message != None:
                    agent_fb = load_facebook_agent(
                        nlu_interpreter_en, nlg_endpoint, action_endpoint, mongo_tracker)
                    task = HandleFacebookMessage(
                        sender_id, used_message, agent_fb)
                    task.start()

        except Exception as e:
            logger.exception('Facebook API Handler Error')

        return "success"


@app.route("/whatsappAPI", methods=['POST'])
def handle_whatsapp_messages():
    if request.method == "GET":
        pass
    else:
        try:
            msg = request.values.get('Body')
            sender_id = request.values.get('From')
            numMedia = int(request.values.get('NumMedia'))
            resp = MessagingResponse()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            if msg is not None or msg != " " or msg != "":
                msgRasa = UserMessage(text=msg, sender_id=sender_id)
                responses = loop.run_until_complete(
                    agent_en.handle_message(msgRasa))
                for response in responses:
                    if numMedia > 0:
                        resp.message(response['text'])
                        # Insert media link into the media function
                        resp.message().media("thank-you-lettering.jpg")
                    else:
                        resp.message(response['text'])
                return str(resp)
            else:
                resp.message("Please Type Something")
        except Exception as e:
            logger.exception('Whatsapp API Handler error')
        return "success"


@app.route("/pause", methods=['POST'])
def pause_bot():
    req_data = request.get_json()
    pause_id = req_data['userId']
    pause = req_data['paused']
    pause_user(pause_id, pause)
    logger.debug(f'User Map: {user_map}')
    return Response("OK")


@app.route("/liveperson", methods=["POST"])
def liveperson():
    req_data = request.get_json()
    userID = req_data['userId']
    dashlog.log("outgoing", None, userID,
                queryText=req_data['text'], intent_name='Human In The Loop')
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
            hashed = md5(
                (str(timestamp[0])+"THIS_IS_SECRET_KEY_PLEASE_KEEP_IT_AS_A_SECRET").encode())
            if token is not None and timestamp is not None:
                if (hashed.hexdigest() == token[0]):
                    return True
            return False
        else:
            return True
    except Exception as e:
        logger.debug(f"Can't authorized connection: {e.args}")
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
            logger.exception("Error Handling Websocket")
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
                    msgRasa = UserMessage(
                        sender_id=session_message, text=text_message)
                    if text_message == "/restart" or text_message == "restart":
                        pause_user(session_message, pause=False)

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    t = loop.run_until_complete(agent.log_message(msgRasa))
                    slots = t.current_slot_values()
                    update_lang(session_message, slots['language'])

                    if not isPause(session_message):
                        responses = loop.run_until_complete(
                            agent.handle_message(msgRasa))
                        for response in responses:
                            log_message = ""
                            if 'text' in response.keys():
                                log_message = response['text']
                            else:
                                log_message = json.dumps(
                                    response['attachment'], indent=3)
                            dashlog.log("outgoing", response,
                                        response['recipient_id'])
                            time.sleep(1)
                            websocket.send(json.dumps(
                                message_exec.send_typing()))
                            time.sleep(1.5)
                            parsed_message = message_exec.parse(response)
                            websocket.send(json.dumps(parsed_message))
                    else:
                        dashlog.log("incoming", None, session_message,
                                    queryText=text_message, intent_name='Human In The Loop')
            except KeyboardInterrupt:
                sys.exit()
            except WebSocketError as ex:
                logger.exception("Websocket Error")
    else:
        raise Exception(f"Agent not found, agent: {agent}")


if __name__ == '__main__':
    userTrack = UserTracker()
    userTrack.start()
    http_server = WSGIServer((host, port), wsgi_app,
                             handler_class=WebSocketHandler)
    logger.info('Server started at %s:%s' % (host, port))
    http_server.serve_forever()
