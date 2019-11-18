from rasa.nlu.model import Interpreter


def run(lang):
   interpreter = Interpreter.load('./models/nlu/'+lang+'/latest/')
   print("**type your words**")
   while True:
       word = input()
       print(interpreter.parse(word))

import sys
lang = "en"
if sys.argv[1] == '--lang':
    lang = str(sys.argv[2])
    run(lang)
