import json, random, requests, re

class NLG():
    """Create A Response based on user template"""
    def __init__(self, config):
        self.TYPE_TEXT = "text"
        self.TYPE_API = "api"
        self.TYPE_QUICKREPLIES = "quickreplies"
        self.TYPE_SEARCHBAR = "search_bar"
        self.TYPE_CAROUSEL = "carousel"
        self.DEFAULT_ERROR_RESPONSE = 'utter_default_error'

        self.config = config
        with open('%s' % config["response"]["path"], encoding='utf8') as temp:
            self.response_template = json.load(temp)
        self.request_data = None
        return

    def parse_request(self, request):
        """Store request for one iteration"""
        self.request_data = request
        return

    def get_query(self):
        return self.request_data['tracker']['latest_message']['text']
    
    def get_intent(self):
        intent = self.request_data['tracker']['latest_message']['intent']
        if intent['confidence'] <= self.config['nlu']['threshold']:
            return "default_fallback"
        return self.request_data['tracker']['latest_message']['intent']['name']
    
    def get_sender(self):
        return self.request_data['tracker']['sender_id']
    
    def _get_template(self):
        return self.request_data['template']
        
    def _is_components(self):
        return
    
    def _is_texts(self, object):
        return

    def _get_content(self, lang):
        try:
            return self.response_template[self._get_template()][lang]['content']
        except:
            print(self._get_template())
            return self.response_template[self.DEFAULT_ERROR_RESPONSE][lang]['content']

    def _get_type(self, template, lang):
        return self._get_content(lang)['type']

    def _get_elements(self, lang):
        return self._get_content(lang)['elements']

    def _make_response(self,text="", buttons=[], image=None, attachments=None):
        response = {}
        if text != "":
            response["text"] = text
        
        if len(buttons) > 0:
            response["buttons"] = buttons
        
        if image != None:
            response["image"] = image
        
        if attachments != None:
            response["attachment"] = attachments

        response["intent"] = self.get_intent()
        return response

    def _get_text(self, lang):
        texts = self._get_elements(lang)
        selected_text = ""
        selected_text = texts[random.randint(0, len(texts)-1) if len(texts) > 1 else 0]
    
        return selected_text
    
    def _get_slots(self):
        return self.request_data['tracker']['slots']

    def get_response(self, lang):
        response_type = self._get_type(self._get_template(), lang)
        if response_type == self.TYPE_TEXT:
            return self._make_response(text=self._replace_template_with_value(self._get_text(lang)))
        elif response_type == self.TYPE_API:
            attachments = self._generate_attachment(self._get_content(lang))
            return self._make_response(attachments=attachments)
        else:
            attachments = self._get_content(lang)
            return self._make_response(attachments=attachments)

    def _replace_template_with_value(self, template):
        slot = self._get_slots()
        match = re.findall(r'\{(.*?)\}', template)
        text = template
        for m in match:
            if m not in slot.keys():
                text = template.replace(m, "undefined").replace("{","").replace("}","")
            else:
                text = template.replace(m, slot[m]).replace("{","").replace("}","")
        return text

    def _generate_attachment(self, content):
        data = {}
        resp = None
        for e in content['elements']:
            url = e['url']
            for key, value in e['body']['data'].items():
                data[key] = self._replace_template_with_value(value)
            if e['method'] == "POST":
                if e['body']['type'] == "form":
                    resp = requests.post(url,data=data, headers=e['headers'])
                else:
                    resp = requests.post(url,json=data, headers=e['headers'])
            else:
                resp = requests.get(self._replace_template_with_value(url))

            data = json.loads(resp.text, format="utf-8")
            
            # temp_element = []
            postbacks = []
            embed = ""
            if e['output']['elements']['embed'] != "":
                embed = e['output']['elements']['embed']
            split_text = ""
            if 'split_text' in e['output']['elements'].keys():
                split_text = e['output']['elements']['split_text']
            if '$' in e['output']['elements']['value']:
                val_lookup = e['output']['elements']['value'].replace("$","").split(".")
                if isinstance(data, list):
                    for d in data:
                        v = None
                        v_temp = d[val_lookup[0]]
                        for f in val_lookup[1:]:
                            v = v_temp[f]
                        

                        if embed != "":
                            v = embed.replace('@',v)
                        postbacks.append(v)
                elif isinstance(data[val_lookup[0]], list):
                    for d in range(len(data[val_lookup[0]])):
                        v = None
                        v_temp = data[val_lookup[0]][d]
                        for f in val_lookup[1:]:
                            v = v_temp[f]
                        

                        if embed != "":
                            v = embed.replace('@',v)
                        postbacks.append(v)
                else:
                    v = None
                    for f in val_lookup:
                        v = data[f]
                
                    if embed != "":
                        v = embed.replace('@',v)
                    postbacks.append(v)
            else:
                postbacks.append(e['output']['elements']['value'])

            labels = []
            if '$' in e['output']['elements']['text']:
                text_lookup = e['output']['elements']['text'].replace("$","").split(".")
                if isinstance(data, list):
                    for d in data:
                        t = None
                        t_temp = d[text_lookup[0]]
                        for f in text_lookup[1:]:
                            t = t_temp[f]

                        labels.append(t)
                elif isinstance(data[text_lookup[0]], list):
                    for d in range(len(data[text_lookup[0]])):
                        t = None
                        t_temp = data[text_lookup[0]][d]
                        for f in text_lookup[1:]:
                            t = t_temp[f]

                        labels.append(t)
                else:
                    t = None
                    for f in text_lookup:
                        t = data[f]
                
                    labels.append(t)
            else:
                labels.append(e['output']['elements']['text'])

            subtitle = []
            if '$' in e['output']['elements']['sub_text']:
                subtext_lookup = e['output']['elements']['sub_text'].replace("$","").split(".")
                if isinstance(data, list):
                    for d in data:
                        st = None
                        st_temp = d[subtext_lookup[0]]
                        for f in subtext_lookup[1:]:
                            st = st_temp[f]

                        subtitle.append(st)
                elif isinstance(data[subtext_lookup[0]], list):
                    for d in range(len(data[subtext_lookup[0]])):
                        st = None
                        st_temp = data[subtext_lookup[0]][d]
                        for f in subtext_lookup[1:]:
                            st = st_temp[f]

                        subtitle.append(st)
                else:
                    st = None
                    for f in subtext_lookup:
                        st = data[f]
                
                    subtitle.append(st)
            else:
                subtitle.append(e['output']['elements']['text'])

            images = []
            img_embed = ""
            if e['output']['elements']['img_embed'] != "":
                img_embed = e['output']['elements']['img_embed']
            if '$' in e['output']['elements']['image']:
                img_lookup = e['output']['elements']['image'].replace("$","").split(".")
                if isinstance(data, list):
                    for d in data:
                        i = None
                        i_temp = d[img_lookup[0]]
                        for f in img_lookup[1:]:
                            i = i_temp[f]

                        if img_embed != "":
                            images.append(img_embed.replace('@',i))
                        else:
                            images.append(i)
                elif isinstance(data[img_lookup[0]], list):
                    for d in range(len(data[img_lookup[0]])):
                        i = None
                        i_temp = data[img_lookup[0]][d]
                        for f in img_lookup[1:]:
                            i = i_temp[f]

                        if img_embed != "":
                            images.append(img_embed.replace('@',i))
                        else:
                            images.append(i)
                else:
                    i = None
                    for f in img_lookup:
                        i = data[f]
                
                    images.append(i)
            else:
                images.append(e['output']['elements']['image'])

            
        buttons = {
            "text": [],
            "payload": []
        }

        for btn in e['output']['elements']['buttons']:
            btn_text = []
            if '$' in btn['text']:
                btn_text_lookup = btn['text'].replace("$","").split(".")
                if isinstance(data, list):
                    for d in data:
                        bt = None
                        bt_temp = d[btn_text_lookup[0]]
                        for f in btn_text_lookup[1:]:
                            bt = bt_temp[f]

                        btn_text.append(bt)
                elif isinstance(data[btn_text_lookup[0]], list):
                    for d in range(len(data[btn_text_lookup[0]])):
                        bt = None
                        bt_temp = data[btn_text_lookup[0]][d]
                        for f in btn_text_lookup[1:]:
                            bt = bt_temp[f]

                        btn_text.append(bt)
                else:
                    bt = None
                    for f in btn_text_lookup:
                        bt = data[f]

                    for _ in range(len(labels)):
                        btn_text.append(bt)
            else:
                for _ in range(len(labels)):
                    btn_text.append(btn['text'])

            buttons['text'].append(btn_text)
            
            btn_payload = []
            if '$' in btn['payload']:
                btn_payload_lookup = btn['payload'].replace("$","").split(".")
                if isinstance(data, list):
                    for d in data:
                        bp = None
                        bp_temp = d[btn_payload_lookup[0]]
                        for f in btn_payload_lookup[1:]:
                            bp = bp_temp[f]
                        
                        if btn['embed'] != "":
                            bp = btn['embed'].replace('@',bp)
                        btn_payload.append(bp)
                if isinstance(data[btn_payload_lookup[0]], list):
                    for d in range(len(data[btn_payload_lookup[0]])):
                        bp = None
                        bp_temp = data[btn_payload_lookup[0]][d]
                        for f in btn_payload_lookup[1:]:
                            bp = bp_temp[f]
                        
                        if btn['embed'] != "":
                            bp = btn['embed'].replace('@',bp)
                        btn_payload.append(bp)
                else:
                    bp = None
                    for f in btn_payload_lookup:
                        bp = data[f]
                    for _ in range(len(labels)):
                        if btn['embed'] != "":
                            bp = btn['embed'].replace('@',bp)
                        btn_payload.append(bp)
            else:
                for _ in range(len(labels)):
                    btn_payload.append(btn['payload'])
            buttons['payload'].append(btn_payload)


        
        btn_pack = []
        for x in range(len(labels)):
            tmp = []
            for y in range(len(buttons['text'])):
                tmp.append({
                    "title": buttons['text'][y][x],
                    "payload": buttons['payload'][y][x]
                })
            btn_pack.append(tmp)
        result = {}
        default_answer = e['output']['elements'].get('default_response_text', '')
        result["elements"], result['type'] =  self._generate_by_type(e['output']['type'],postbacks,labels,subtitle,images,btn_pack,e['output']['elements']['title'], embed, split_text, default_answer)
        return result

    def _generate_by_type(self, type_payload, postbacks, labels, subtitle, images, buttons, title, embed, split_text, default_response):
        if len(labels) > 0:
            if type_payload == self.TYPE_QUICKREPLIES:
                qr = {
                "text": self._replace_template_with_value(title)
                }           

                temp_txt = []
                for i in range(len(labels)):
                    temp_txt.append({
                        "title": labels[i],
                        "payload": postbacks[i]
                    })
                qr["replies"] = temp_txt

                return [qr], type_payload
            elif type_payload == self.TYPE_SEARCHBAR:
                select_box = {
                    "type":"search_bar",
                    "text": title,
                    "input_disable": "true"
                }
                data = []
                check = {}
                for i in range(len(labels)):
                    if labels[i] not in check.keys():
                        data.append({
                            "text": labels[i],
                            "payload": postbacks[i]
                        })
                        check[labels[i]] = True
                select_box["data"] = data
                return select_box, type_payload
            elif type_payload == self.TYPE_CAROUSEL:
                carousel = []
                for i in range(len(labels)):
                    card = {
                        "label": labels[i],
                        "description": subtitle[i],
                        "image_type": "url",
                        "image": images[i]
                    }
                    card["buttons"] = buttons[i]
                    carousel.append(card)

                return carousel, type_payload
            elif type_payload == self.TYPE_TEXT:
                if split_text != "":
                    split_text = ","
                item = split_text.join(labels)
                text = embed.replace("@",item)
                return [text], type_payload
        else:
            return [default_response], "text"

from .tracker import Tracker
from .config import load_config
from flask import Flask, Response, request

config = load_config()
response_template = None
n = NLG(config)
dashlog = Tracker(config['dashbot']['api'],config['dashbot'][config["template"]["module"]]['api_key'])
with open('%s' % config["response"]["path"], encoding='utf8') as temp:
    response_template = json.load(temp)

app = Flask(__name__)

@app.route("/nlg", methods=['POST'])
def nlg():
    req_data = request.get_json()
    n.parse_request(req_data)
    text = n.get_query()
    intent = n.get_intent()
    if intent == None or intent == "":
        intent = "default_fallback"
    sender_id = n.get_sender()
    slot = n._get_slots()
    lang = "en"
    if 'language' in slot.keys():
        lang = slot['language']
    if lang == None or lang == "":
        lang = "en"
    dashlog.log("incoming", None, sender_id,queryText=text,intent_name=intent)
    response = n.get_response(lang)
    return Response(json.dumps(response,indent=3), mimetype="application/json")


from waitress import serve
import os, sys
env = os.getenv("BLUELOGIC_ENV", "development")
port = 5006
if sys.argv[1] == '-p':
    port = int(sys.argv[2])
if __name__ == "__main__":
    if env == "production":
        serve(app, listen='*:%d' % port)
    else:
        app.run(debug=True, port=port)
    # serve(app, listen='*:%d' % port)
