import logging, json, os
def load_config(file='./config/development.config.json'):
    """Return loaded config from JSON file.

    >>> load_config("config_test.json")
    {'test': 'ok'}
    """
    env = os.getenv("BLUELOGIC_ENV", "development")
    file = './config/%s.config.json' % env
    with open(file, errors='ignore') as cfg:
        logging.info("Config Loaded from: %s" % file)
        config = json.load(cfg)
        return config