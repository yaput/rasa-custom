import inspect
import bl_core.core_util as core_util
from .bluemessage import BluebotMessage

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
        method_type = "text"
        if 'text' in request.keys():
            data = request['text']
        elif 'attachment' in request.keys():
            try:
                data = request['attachment']['elements']
                loc = request['attachment'].get('location', 'false')
                method_type = request['attachment']['type']
            except:
                pass

        
        try:
            # TODO: Change this to use better way
            if method_type == "carousel":
                return self.methods[method_type].send(session_id, data, loc)
            return self.methods[method_type].send(session_id, data)
        except Exception as e:
            return self.methods['text'].send(session_id, data) 

    def send_typing(self):
        return {"type":"typing"}
        
# e = MessageExecutor()
# e.load()
# print(e.parse({"recipient_id": "123-abc", "attachment": {"type": "carousel", "elements":[]}}))