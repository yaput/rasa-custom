Use python3.7 to run this.

It will ask you to download english model for spacy. To do this you can use:
```bash
python -m spacy download en
```
Some features are included in this module like logger into dashbot.io, persist the conversation into mongodb.

## To run the chatbot we need to run 3 services:
- Run connection interface to handle websocket, pause chatbot and liveperson for dashbot.io
  to run this, you can run `python -m bl_core.connection_interface -vv` to enable debug, without `-vv or --debug` will not log debug
- Run NLG server to generate the chatbot response run this with `python -m bl_core.nlg -p 5016` this -p is mandatory to define port. It will use the `response.json` file.
- Run custom action server with `rasa run actions` if your module name is actions.

Also keep in mind regarding the folder structure, it will handle multiple agents for different language.