import json, logging, requests
from chatbase import Message

class Tracker(object):
    """Create logger object for chatbot. Using dashbot format"""
    def __init__(self, api_key, platform, version='0.1'):
        self.tracker = dict()
        self._api_key = api_key
        self.platform = platform
        self.version = version

    def log(self, userID, intent_name=None, queryText="", agent=True):
        msg_log = Message(self._api_key, self.platform, queryText, intent_name, self.version, userID)
        if intent_name == None or intent_name == "default_fallback":
            msg_log.set_as_not_handled()
        else:
            msg_log.set_as_handled()
        if agent:
            msg_log.set_as_type_agent()
        else:
            msg_log.set_as_type_user()
        
        msg_log.send()

    def view_tracker(self):
        print(json.dumps(self.tracker, indent=3))

    def log_event(self, event_name, userID, extraInfo):
        """
        Log custom event(for now), for extra info you can add
        custom object json containing every info that we needed
        """
        pass