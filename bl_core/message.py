import inspect
import core_util
from core.message import BluebotMessage

class MessageExecutor():
    def __init__(self):
        self.methods = {}
    
    def load(self):
        for name, method in inspect.getmembers(core_util):
            try:
                if issubclass(method, BluebotMessage) and name is not "BluebotMessage":
                    invocated_method = method() 
                    self.methods[invocated_method.type_name()] = invocated_method
                
            except Exception as e:
                continue

    def parse(self, request):
        session_id = request['recipient_id']
        data = None
        method_type = "message"
        if 'text' in request.keys():
            data = request['text']
        elif 'attachment' in request.keys():
            try:
                data = request['attachment']['elements']
                method_type = request['attachment']['type']
            except:
                pass

        return self.methods[method_type].send(session_id, data)

    def send_typing(self):
        return {"type":"typing"}
        
# e = MessageExecutor()
# e.load()
# print(e.parse({"recipient_id": "123-abc", "attachment": {"type": "carousel", "elements":[]}}))