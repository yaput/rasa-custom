import json

from rasa.nlu.training_data import load_data
from rasa.nlu.model import Trainer, Interpreter
from rasa.nlu import config


def train_nlu(name, lang="en",production_build=False):
    model_name = "production"
    if not production_build:
        model_name = "latest"
    training_data = load_data('./data/'+name+'/nlu/'+lang+"/")
    trainer = Trainer(config.load("config.yml"))
    trainer.train(training_data)
    trainer.persist('./models/nlu/'+lang+"/", fixed_model_name=model_name)

def run(lang):
    interpreter = Interpreter.load("./models/nlu/" + lang+ "/latest")
    while True:
        message = input()
        result = interpreter.parse(message)
        print(json.dumps(result, indent=2))

import sys
if sys.argv[1] == '--name':
    data = str(sys.argv[2])

if sys.argv[3] == '--lang':
    lang = str(sys.argv[4])

train_nlu(data, lang)
run(lang)