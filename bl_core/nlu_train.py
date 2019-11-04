from rasa.nlu.training_data import load_data
from rasa.nlu.model import Trainer
from rasa.nlu import config

def train_nlu(name, lang="en",production_build=False):
    model_name = "production"
    if not production_build:
        model_name = "latest"

    training_data = load_data('./data/nlu/'+lang+"/")
    trainer = Trainer(config.load("config.yml"))
    trainer.train(training_data)
    trainer.persist('./models/nlu/'+lang+"/", fixed_model_name=model_name)

import sys

if sys.argv[1] == '--name':
    data = str(sys.argv[2])

if sys.argv[3] == '--lang':
    lang = str(sys.argv[4])

train_nlu(data, lang)
