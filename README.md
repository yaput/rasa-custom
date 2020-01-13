Recommended install virtualenv
```bash
$ sudo apt-get install virtualenv
```
Use python3.7 and also `python-dev` package
```bash
$ sudo apt-get install python3.7 python-dev python3-dev python3.7-dev  build-essential
```

create virtualenv to isolate the package for the development
```bash
$ virtualenv your_env_name --python=`which python3.7`
```
to deactivate the virtualenv type `deactivate`

to activate virtualenv after creating
```bash
$ source your/virtualenv/folder/name/bin/activate
```

Install the library with
```bash
$ pip install git+https://gitlab.com/bluelogic/bl-core.git
```

It will ask you to download english model for spacy. To do this you can use:
```bash
$ pip install spacy
$ python -m spacy download en
```

To start your project, you can download the default structure from `https://gitlab.com/bluelogic/clientinstance`
Use the downloaded `clientinstance` and change the folder name as you want, then go inside the folder ex: `cd clientinstance` and run the 3 commands below.
Or you can copy and paste below script and `chmod +x script_name.sh` then run it `./script_name.sh`
```bash
#!/bin/bash

echo "Init Blue Logic Chatbot Structure"
echo "What is the name of the project?"
read project_name

echo "Please tell me the repository URL"
read repo_source

git clone git@gitlab.com:bluelogic/clientinstance.git $project_name

cd $project_name

git remote rm origin

git remote add origin $repo_source

git remote -v

ls
```

Some features are included in this module like logger into dashbot.io, persist the conversation into mongodb.

## To run the chatbot we need to run 3 services:
- Run connection interface to handle websocket, pause chatbot and liveperson for dashbot.io
  to run this, you can run `python -m bl_core.connection_interface -vv` to enable debug, without `-vv or --debug` will not log debug
- Run NLG server to generate the chatbot response run this with `python -m bl_core.nlg -p 5016` this -p is mandatory to define port. It will use the `response.json` file.
- Run custom action server with `rasa run actions` if your module name is actions.

Also keep in mind regarding the folder structure, it will handle multiple agents for different language.
