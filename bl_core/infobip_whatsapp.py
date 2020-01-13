class WhatsappResult:
    def __init__(self):
        self.sender_id = ""
        self.receiver_id = ""
        self.integration_type = ""
        self.receive_at = ""
        self.message_id = ""
        self.paired_message_id = None
        self.callback_data = None
        self.message = WhatsappMessage
        self.contact = WhatsappContact
        self.price = None

class WhatsappMessage:
    def __init__(self):
        self.type = None
        self.text = None
    
    @property
    def message(self):
        return {"type": self.type, "text": self.text}
    
    def parse(self, message_dict):
        self.type = message_dict.get('type')
        self.text = message_dict.get('text')
        return self

class WhatsappContact:
    def __init__(self):
        self.name = ""

    @property
    def contact(self):
        return {"name": self.name}

    def parse(self, dict_obj):
        self.name = dict_obj.get('name')
        return self

class InfobipWhatsappIncomingMessage:
    def __init__(self):
        self.results = [WhatsappResult]
        self.message_count = 0
        self.pending_message_count = 0

    def parse_dict(self, incoming_object):
        """Parse dictionary to whatsapp incoming message object"""
        self.message_count = incoming_object.get('messageCount')
        self.pending_message_count = incoming_object.get('pendingMessageCount')
        self.results = []
        for result in incoming_object.get('results', []):
            whatsapp_result = WhatsappResult()
            whatsapp_result.sender_id = result.get('from') 
            whatsapp_result.receiver_id = result.get('to')
            whatsapp_result.integration_type = result.get('integrationType')
            whatsapp_result.receive_at = result.get('receivedAt')
            whatsapp_result.message_id = result.get('messageId')
            message = WhatsappMessage().parse(result.get('message'))
            whatsapp_result.message = message
            whatsapp_result.contact = WhatsappContact().parse(result.get('contact'))
            self.results.append(whatsapp_result)
        
        return self

import requests
from requests.auth import HTTPBasicAuth
class InfobipWhatsappOutgoing:
    def __init__(self):
        self.scenario_key = ""
        self.whatsapp_msg = ""
        self.sms = ""
        self.phone_number_to = ""
    
    def json(self):
        payload = {
            "scenarioKey": self.scenario_key,
            "destinations": [
                {
                    "to": {
                        "phoneNumber": self.phone_number_to
                    }
                }
            ],
            "whatsApp": {
                "text": self.whatsapp_msg
            }
        }	
        return payload

    def template_json(self):
        payload = {
            "scenarioKey": self.scenario_key,
            "destinations": [
                {
                    "to": {
                        "phoneNumber": self.phone_number_to
                    }
                }
            ],
            "whatsApp": {
                "templateName": "infobip_test_hsm", # TODO: Change template name
                "templateNamespace": "whatsapp:hsm:it:infobip", # TODO: Change template namespace
                "templateData": [
                    "Someone",
                    "Bluelogic"
                ], # TODO: change template data
                "language": "en_GB"
            }
        }	
        return payload

    def send(self, obj_message): 
        url = "https://ej8yk3.api.infobip.com/omni/1/advanced" # TODO: Change URL 
        return requests.post(url, json=obj_message, auth=HTTPBasicAuth('bltestinfobip', "Bluelogic#123")) # TODO: Change username and password


# Test Usage

# m = InfobipWhatsappOutgoing()
# m.scenario_key = "FB579BC2150650B35252D0894ED0C0F0"
# m.phone_number_to = "971547657841"
# m.whatsapp_msg = "Hey there"
# print(m.send(m.template_json()).text) # For sending template
# print(m.send(m.json()).text) # For sending free form