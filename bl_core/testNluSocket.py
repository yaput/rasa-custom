from flask import Flask
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocketError
from rasa.nlu.model import Interpreter
import json
import os


app = Flask(__name__)
app.debug = True

host, port = '0.0.0.0', 2501

def getNLUInterpreter(folderName):

    """
    This function loads the nlu model and returns it to websocket handle function.
    It needs folderName as parameter to load the model from that folder.
    """
    try:
        if os.path.isdir('./models/nlu'):
            if os.path.isdir('./models/nlu/en'):
                folder_path = './models/nlu/en/'+folderName
                if os.path.isdir(folder_path):
                    nlu_interpreter_en = Interpreter.load(folder_path)
                    return nlu_interpreter_en
                else:
                    raise Exception("No folder by name "+folderName+" in ./models/nlu/en path")
            else:
                raise Exception("Couldn't find an english NLU model at path ./models/nlu/en")
        else:
            raise Exception("Couldn't find path ./models/nlu")
    except Exception as e:
        print('Message: ' + repr(e))

def wsgi_app(environ, start_response):

    """
    This function checks if environ path provided when connecting matches to /ws/en
    and then calls handle function to handle websocket connection and passes the
    websocket object to the handler.
    :param environ:
    :param start_response:
    :return:
    """
    path = environ["PATH_INFO"]
    if path == "/ws/en":
        try:
            handle_websocket(environ["wsgi.websocket"])
        except Exception as e:
            print(e)
            print("Stop Connection")
        return []
    else:
        return app(environ, start_response)

def handle_websocket(websocket):

    """
    This function handles request to websocket. Loads interpreter model from folderName
    send through message to websocket and returns the intent and entities the model
    has predicted for a message.
    :param websocket: websocket object
    """

    if websocket is not None:
        try:
            while True:
                msg = websocket.receive()
                try:
                    message = json.loads(msg)
                except:
                    break
                text_message = message['text'] # Getting text from message
                folder_name = message['folder_name'] # Getting folder_name from message
                # Calling function to load NLU model from folder
                interpreter = getNLUInterpreter(folder_name)
                # Checking which intent and entities model predicts for a message
                responses = interpreter.parse(text_message)
                print(responses)
                intent_message = responses['intent']
                entity_message = responses['entities']
                # Returning predicted intent with confidence score
                websocket.send(json.dumps(intent_message))
                # Returning predicted entities
                websocket.send(json.dumps(entity_message))
        except WebSocketError as ex:
            print(ex)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    http_server = WSGIServer((host, port), wsgi_app, handler_class=WebSocketHandler)
    print('Server started at %s:%s' % (host, port))
    http_server.serve_forever()