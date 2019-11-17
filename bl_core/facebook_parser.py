from pymessenger.bot import Bot
from .config import load_config

config = load_config()
ACCESS_TOKEN = config["facebook_tokens"]["access_token"]
VERIFY_TOKEN = config["facebook_tokens"]["verify_token"]
#ACCESS_TOKEN = 'EAAGwvab3ol8BAAmIz9fszZAPZCF6wv2REXuu7Y8c5adPdtFOclZCwnrO7ZCIfJrVGPQ9RXxFRdohd4lT7BvcRZCeyZCQy6vWGkpri94oXBJ5WHI6yskbZBIpUopIcPOZAzb1ZBZCwfZCgQZAwLlcyzj6S7AZAr60jgn3QWvqnA8YeuTSzEhcVF7yKEhaM'
#VERIFY_TOKEN = 'secret'
fb_bot = Bot(ACCESS_TOKEN)


def fb_send_carousel(user_id, carousel_data):
    data_fb = []

    for i in carousel_data:
        btn = []
        for j in i['buttons']:
            btn.append({
                "type": "postback",
                "title": j['title'],
                "payload": j['payload']
            })
        e = {
            "title": i['label'],
            "subtitle": i['description'],
            "image_url": i['image'],
            "buttons": btn
        }
        data_fb.append(e)

    # payload = {
    #     'recipient': {
    #         'id': user_id
    #     },
    #     'message': {
    #         "elements": data_fb
    #             }
    #         }

    fb_bot.send_generic_message(user_id, data_fb)
    # return payload


# def fb_send_quick_replies(user_id, quick_reply):
#     payload = {
#         'recipent': {
#             'id': user_id
#         },
#         'messaging_type': 'RESPONSE',
#         'message': {
#             'text':  '',
#             'quick_replies': quick_reply

#         }
#     }
#     fb_bot.send_raw(payload)
# return payload


def fb_send_text_message(user_id, message):
    # payload = {
    #     'recipient': {
    #         'id': user_id
    #     },
    #     'message': {
    #         'text': message
    #     }
    # }
    fb_bot.send_text_message(user_id, message)
    # return payload


def fb_send_quick_replies(user_id, quick_reply):
    new_data = []
    for i in quick_reply[0]['replies']:
        new = {
            'content_type': "text",
            'title': i['title'],
            'payload': i['payload']
        }
        new_data.append(new)

    payload = {
        'recipient': {
            'id': user_id
        },
        'messaging_type': 'RESPONSE',
        'message': {
            'text': quick_reply[0]['text'],
            'quick_replies': new_data

        }
    }
    fb_bot.send_raw(payload)
    # return payload


def fb_send_restart(user_id, quick_reply):
    new_data = quick_reply['elements'][0]
    new = [{
        'content_type': 'text',
        'title': new_data['replies'][0]['title'],
        'payload': new_data['replies'][0]['payload']
    }]
    payload = {
        'recipient': {
            'id': user_id
        },
        'messaging_type': 'RESPONSE',
        'message': {
            'text': new_data['text'],
            'quick_replies': new
        }
    }
    fb_bot.send_raw(payload)


def fb_send_image(user_id, response):
    return fb_bot.send_raw({
        "recipient": {
            "id": user_id
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": response[0],
                    "is_reusable": True
                }
            }
        }
    })


def fb_send_link(user_id, response):
    return fb_bot.send_raw({
        "recipient": {
            "id": user_id
        },
        "timestamp": 1458692752478,
        "referral": {
            "ref": "REGISTRATION_CODE",
            "source": "SHORTLINK",
            "type": "OPEN_THREAD",
        }
    })


def fb_parse_bot_response(user_id, response):
    map_attachment_response = {
        'carousel': fb_send_carousel,
        'quickreplies': fb_send_quick_replies,
        'text': fb_send_text_message,
        'image': fb_send_image,
    }
    if 'text' in response.keys():
        return fb_send_text_message(user_id, response['text'])
    elif 'attachment' in response.keys():
        # try:
        #     data = response['attachment']['elements']
        #     data_final = fb_send_carousel(user_id, response['attachment']['elements'])
        #     return data_final
        # except:
        #     data = []
        try:
            data = response['attachment']['elements']
        except:
            data = []
        print("************debug**********")
        print(response.keys())
        return map_attachment_response[response['attachment']['type']](user_id, data)