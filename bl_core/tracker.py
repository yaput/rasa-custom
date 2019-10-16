import json, logging, requests

class Tracker(object):
    """Create logger object for chatbot. Using dashbot format"""
    def __init__(self, url, api_key):
        self.tracker = dict()
        self._url = url
        self._api_key = api_key

    def _add_required(self, text, userID):
        self.tracker["text"] = text
        self.tracker["userId"] = userID

    def _add_intent(self, intent_name, inputs=None):
        if intent_name != None:
            self.tracker["intent"] = {
                "name": intent_name
            }
        if inputs != None:
            self.tracker["intent"]["inputs"] = inputs
    
    def _add_image(self, images=None):
        if images != None:
            self.tracker["images"] = images
    
    def _add_button(self, buttons=None):
        if buttons != None:
            self.tracker["buttons"] = buttons
    
    def _add_button(self, postback=None):
        if postback != None:
            self.tracker["postback"] = postback

    def _add_custom_payload(self, payload=None):
        if payload != None:
            self.tracker["platformJson"] = payload
    
    def _send_log(self, tracker, msg_type):
        try:
            full_url = self._url % (msg_type,self._api_key)
            resp = requests.post(full_url, json=tracker)
            if resp.status_code == 200:
                logging.debug("REQUEST SUCCESS TO LOG DASHBOT")
            else:
                logging.debug("REQUEST FAILED TO LOG DASHBOT")
        except Exception as e:
            print(e.args)

    def log(self,msg_type, response, userID, intent_name=None, queryText=""):
        self._add_intent(intent_name, None)
        if queryText != "":
            self._add_required(queryText, userID)
        else:
            if 'text' in response.keys():
                if response['text'] != "":
                    self._add_required(response['text'], userID)
            if 'image' in response.keys():
                self._add_image(response['image'])
            if 'buttons' in response.keys():
                if len(response['buttons']) > 0:
                    self._add_button(response['buttons'])
            if 'attachment' in response.keys():
                self._add_required(response['attachment'], userID)
                self._add_custom_payload(response['attachment'])

        self._send_log(self.tracker,msg_type)

    def view_tracker(self):
        logging.info(json.dumps(self.tracker, indent=3))
        print(json.dumps(self.tracker, indent=3))

    def log_event(self, event_name, userID, extraInfo):
        """
        Log custom event(for now), for extra info you can add
        custom object json containing every info that we needed
        """
        event = {
            "name" : event_name,
            "type": "customEvent",
            "userId": userID,
            "extraInfo": extraInfo
        }
        self._send_log(event, "event")
