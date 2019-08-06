import json, requests, random

def request_query(query='', session_id=''):
    data_request = { 
        "sender": session_id, 
        "message": query
    }
    print(data_request)
    res = requests.post('http://localhost:5005/webhooks/rest/webhook',json=data_request)
    return res.json()

def send_quickreplies(session_id, quickreplies):
    return {
        "text": quickreplies[0].get('text',""),
        "quick_replies": quickreplies[0]['replies'],
        "channel":"socket",
        "user": session_id,
        "to": session_id,
        "type":"message",
        "input_disable": quickreplies[0].get('input_disable', 'false'),
    }

def send_nothing(session_id, data):
    return {
        "channel":"socket",
        "user": session_id,
        "to": session_id,
        "type":"skip_this",
        "input_disable": 'false',
    }

def send_carousel(session_id, carousel_data):
    return {
        "type":"carousel",
        "text":"mainCarousel",
        "data":carousel_data,
        "channel":"socket",
        "user":session_id,
        "to":session_id
    }

def send_list(session_id, list_data):
    return {
        "type":"list",
        "channel":"socket",
        "text":"list",
        "data": list_data,
        "user":session_id,
        "to":session_id
    }

def send_image(session_id, image_data):
    return {
        "text":"image",
        "type":"image",
        "data":image_data,
        "channel":"socket",
        "continue_typing":True,
        "user":session_id,
        "to":session_id
    }

def send_text(session_id, message):
    if isinstance(message, list):
        message = message[random.randint(0, len(message)-1)]
    return {
        'type':'message',
        'text':message,
        'user':session_id,
        'channel':'socket'
    }

def send_existing_user_form(session_id, message=None):
    return{
        "type": "existing_user_form",
        "channel": "socket",
    }

def send_new_user_form(session_id, message=None):
    return {
        "type": "new_user_form",
        "channel": "socket",
        "input_disable": "true",
        "content": {
                "type": "new_user_form",
                "text": "Super! I would appreciate it if you could fill out the form (for the patient) below to help me book you in. 😎"
        }
    }

def send_driving_license_form(session_id, message=None):
    return { 
        "type": "identity_verify_selection", 
        "channel": "socket"
    }

def send_vehicle_detail_form(session_id, message=None):
    return { 
        "type": "car_verify_selection", 
        "channel": "socket"
    }

def send_payment_form(session_id, message=None):
    return { 
        "type": "payment_request", 
        "channel": "socket"
    }
    
def send_final_qoute(session_id, message=None):
    return { 
        "type": "comprehensive", 
        "channel": "socket"
    }

def send_qoute_compare(session_id, message=None):
    return {
        "type": "quote_request",  
        "channel": "socket"
    }

def send_email_sent_popup(session_id, message=None):
    return {
        "type": "confimation_popup",  
        "channel": "socket"
    }

def send_insurance_invoice(session_id, message=None):
    return {
        "type": "invoice_display",  
        "channel": "socket"
    }

def send_email_form(session_id, message=None):
    return {
        "type": "collect_email",  
        "channel": "socket"
    }

def send_account_form(session_id, message=None):
    return {
        "type": "register_account",  
        "channel": "socket"
    }

def send_typing():
    return {"type":"typing"}

def send_search_bar(session_id, data):
    if isinstance(data, list):
        data = data[0]
    items = []
    for d in data['data']:
        items.append({
           "title": d['text'],
           "payload": d['payload']
        })
    return {
        "type": "daynamic_search_bar",
        "channel": "socket",
        "data": items,
        "input_disable": "true",
        "text": data['text']
    }

def send_dynamic_form(session_id, data):
    return {
        "type": "daynamic_form",
        "channel": "socket",
        "input_disable": "true",
        "data": {
            "fields": data
        }
    }

def send_sound(session_id, data):
    d = data[0]
    return {
        "is_received": True,
        "type": "sound_tract",
        "text": d['text'],
        "channel": "socket",
        "link": d['sound']
    }

def send_get_user_location(session_id, data):
    return {
        "type": "get_user_location",
        "channel": "socket",
        "input_disable": "true",
        "content": {
            "type": "get_user_location",
            "text": "get_user_location"
        }
    }

def send_scale(session_id, data):
    return {
        "type": "range_slider",
        "channel": "socket",
        "text": "range_slider",
        "input_disable": "true",
        "data": data[0]['data']
    }

def send_multi_select(session_id, data):
    return {
        "type": "multi_select",
        "channel": "socket",
        "text": data[0]['text'],
        "input_disable": "true",
        "quick_replies": data[0]['quickreplies']
    }

def send_get_direction(session_id, data):
    return {
        "type": "get_map_direction",
        "channel": "socket",
        "content": {
            "type": "get_map_direction",
            "text": "get_map_direction"
        },
        "data": data
        }
    
def send_otp(session_id, data):
    return {
            "type": "otp",
            "channel": "socket",
            "content": {
                "type": "otp",
                "text": "OTP-form",
                "input_disable": "true",
                "digit": "6"
            }
        }

def send_callbackform(session_id, data):
    return {
    "type": "callback_form",
    "input_disable": "true",
    "channel": "socket",
    "content": {
        "input_disable": "true",
        "type": "callback_form",
        "text": "callback_form"
    }
    }

def send_liveagent(session_id, data):
    return {
        "type": "chat_transcript",
        "channel": "socket",
        "content": {
            "type": "chat_transcript",
            "text": "chat_transcript"
        }
    }

def send_end_session(session_id, data):
    return {
        "type": "end_session"
    }

def send_restart_session(session_id, data):
    return {
        "type": "restart_session"
    }

def send_new_link(session_id, data):
    return {
           "is_received": True,
           "type": "newlink",
           "data" : [{
                "link": data[0]
           }]
      }

def send_download(session_id, data):
    file_send = data[0]
    return {
        "is_received": True,
        "type": "download",
        "text": "download",
        "channel": "socket",
        "data":[{"filename": file_send}]
    }

def parse_bot_response(response):
    session_id = response['recipient_id']
    map_attachment_response = {
        'carousel': send_carousel,
        'quickreplies': send_quickreplies,
        'existing_user_form': send_existing_user_form,
        'image': send_image,
        'driving_license_form': send_driving_license_form,
        'vehicle_detail_form': send_vehicle_detail_form,
        'payment_form': send_payment_form,
        'final_qoute': send_final_qoute,
        'compare_qoute': send_qoute_compare,
        'email_send_popup':send_email_sent_popup,
        'invoice_details': send_insurance_invoice,
        'email_send_form': send_email_form,
        'create_account_form': send_account_form,
        'search_bar':send_search_bar,
        'form': send_dynamic_form,
        'text': send_text,
        'get_user_location': send_get_user_location,
        'range_slider': send_scale,
        'multi_select': send_multi_select,
        'get_direction': send_get_direction,
        'get_otp': send_otp,
        'list': send_list,
        'callbackform': send_callbackform,
        'chat_with_liveagent': send_liveagent,
        'restart_session': send_restart_session,
        'end_session': send_end_session,
        "newlink": send_new_link,
        'send_nothing': send_nothing,
        "sound_text": send_sound,
        "download": send_download,
    }
    if 'text' in response.keys():
        return send_text(session_id, response['text'])
    elif 'attachment' in response.keys():
        try:
            data = response['attachment']['elements']
        except:
            data = []
        return map_attachment_response[response['attachment']['type']](session_id, data)


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email import encoders
def sendMail(to, message_text, subject, cc =[], filename=""):
    gmail_user = 'cbcb@medcarehospital.com'  
    gmail_password = 'QazWsx@2020'
    email_to = to
    # Create the container email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = email_to
    msg['Cc'] = ','.join(cc)
    message_text = message_text
    msg.attach(MIMEText(message_text, 'plain'))
    if filename != "":
        with open(filename, 'r') as f:
            attachment = MIMEText(f.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)           
            msg.attach(attachment)


    text = msg.as_string()
    addresses = [email_to]
    if len(cc) > 0 :
        addresses =  addresses + cc

    try:  
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, ','.join(addresses), text)
        server.quit()
        return True
    except smtplib.SMTPException as e:  
        print("DEBUG ERROR SMPT: " + e)

        return False