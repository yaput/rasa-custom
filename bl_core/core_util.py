import json, requests, random
from .bluemessage import BluebotMessage

class QuickReplies(BluebotMessage):
    """
        Handle Quick Replies request for front end
    """
    def type_name(self):
        return "quickreplies"
    
    def send(self, session_id, data):
        return {
            "text": data[0].get('text',""),
            "quick_replies": data[0]['replies'],
            "channel":"socket",
            "user": session_id,
            "to": session_id,
            "type":"message",
            "input_disable": data[0].get('input_disable', 'false'),
        }

class EmptyMessage(BluebotMessage):
    """
        Handle Empty message for some certain conditions request for front end
    """
    def type_name(self):
        return "send_nothing"
    
    def send(self, session_id, data):
        return {
            "channel":"socket",
            "user": session_id,
            "to": session_id,
            "type":"skip_this",
            "input_disable": 'false',
        }

class Carousel(BluebotMessage):
    """
        Handle Carousel or Cards request for front end
    """
    def type_name(self):
        return "carousel"

    def send(self, session_id, data):
        return {
            "type":"carousel",
            "text":"mainCarousel",
            "data":data,
            "channel":"socket",
            "user":session_id,
            "to":session_id
        }

class List(BluebotMessage):
    """
        Handle List request for front end
    """
    def type_name(self):
        return "list"
    
    def send(self, session_id, list_data):
        return {
            "type":"list",
            "channel":"socket",
            "text":"list",
            "data": list_data,
            "user":session_id,
            "to":session_id
        }


class Image(BluebotMessage):
    """
        Image was not present
    """
    def type_name(self):
        return "image"

    def send(self, session_id, image_data):
        return {
            "text": "image",
            "type": "image",
            "data": image_data,
            "channel": "socket",
            "continue_typing": True,
            "user": session_id,
            "to": session_id
        }

class Text(BluebotMessage):
    """
        Text was not present
    """
    def type_name(self):
        return "text"

    def send(self, session_id, message):
        if isinstance(message, list):
            message = message[random.randint(0, len(message) - 1)]
        return {
            'type': 'message',
            'text': message,
            'user': session_id,
            'channel': 'socket'
        }


class ExistingUserForm(BluebotMessage):
    """
        existing_user_form was not present
    """
    def type_name(self):
        return "existing_user_form"

    def send(self, session_id, message=None):
        return {
            "type": "existing_user_form",
            "channel": "socket",
        }



class DrivingLicenseForm(BluebotMessage):
    """
        driving_license_form was not present
    """
    def type_name(self):
        return "driving_license_form"

    def send(self, session_id, message=None):
        return {
            "type": "identity_verify_selection",
            "channel": "socket"
        }



class VehicleDetailForm(BluebotMessage):
    """
        vehicle_detail_form was not present
    """
    def type_name(self):
        return "vehicle_detail_form"

    def send(self, session_id, message=None):
        return {
            "type": "car_verify_selection",
            "channel": "socket"
        }


class PaymentForm(BluebotMessage):
    """
        payment_form was not present
    """
    def type_name(self):
        return "payment_form"

    def send(self, sessison_id, message):
        return {
            "type": "payment_request",
            "channel": "socket"
        }

class FinalQoute(BluebotMessage):
    """
        final_qoute was not present
    """

    def type_name(self):
        return "final_qoute"

    def send(self, session_id, message=None):
        return {
            "type": "comprehensive",
            "channel": "socket"
        }

class CompareQoute(BluebotMessage):
    """
        compare_qoute was not present
    """

    def type_name(self):
        return "compare_qoute"

    def send(self, session_id, message=None):
        return {
            "type": "quote_request",
            "channel": "socket"
        }

class EmailSendPopup(BluebotMessage):
    """
        email_send_popup was not present
    """

    def type_name(self):
        return "email_send_popup"

    def send(self, session_id, message=None):
        return {
            "type": "confimation_popup",
            "channel": "socket"
        }

class InvoiceDetails(BluebotMessage):
    """
        invoice_details was not present
    """

    def type_name(self):
        return "invoice_details"

    def send(self, session_id, message=None):
        return {
            "type": "invoice_display",
            "channel": "socket"
        }

class EmailSendForm(BluebotMessage):
    """
        email_send_form was not present
    """

    def type_name(self):
        return "email_send_form"

    def send(self, session_id, message=None):
        return {
            "type": "collect_email",
            "channel": "socket"
        }

class CreateAccountForm(BluebotMessage):
    """
        create_account_form was not present
    """

    def type_name(self):
        return "create_account_form"

    def send(self, session_id, message=None):
        return {
            "type": "register_account",
            "channel": "socket"
        }

class SearchBar(BluebotMessage):
    """
        search_bar was not present
    """

    def type_name(self):
        return "search_bar"

    def send(self, session_id, data):
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

class Form(BluebotMessage):
    """
        form was not present
    """

    def type_name(self):
        return "form"

    def send(self, session_id, data):
        return {
            "type": "daynamic_form",
            "channel": "socket",
            "input_disable": "true",
            "data": {
                "fields": data
            }
        }

class Qrcode(BluebotMessage):
    """
        qrcode was not present
    """

    def type_name(self):
        return "qrcode"

    def send(self, session_id, data):
        d = data[0]
        return {
            "is_received": True,
            "type": "qrcode",
            "service_name": d["service_name"],
            "start_date": d["start_date"],
            "customer_count": d["customer_in_queue"],
            "approx_time": d["approx_time"],
            "value": d["customer_token"],
            "channel": "socket"
        }

class SoundText(BluebotMessage):
    """
        sound_text was not present
    """

    def type_name(self):
        return "sound_text"

    def send(self, session_id, data):
        d = data[0]
        return {
            "is_received": True,
            "type": "sound_tract",
            "text": d['text'],
            "channel": "socket",
            "link": d['sound']
        }

class GetUserLocation(BluebotMessage):
    """
        get_user_location was not present
    """

    def type_name(self):
        return "get_user_location"

    def send(self, session_id, data):
        return {
            "type": "get_user_location",
            "channel": "socket",
            "input_disable": "true",
            "content": {
                "type": "get_user_location",
                "text": "get_user_location"
            }
        }

class RangeSlider(BluebotMessage):
    """
        range_slider was not present
    """

    def type_name(self):
        return "range_slider"

    def send(self, session_id, data):
        return {
            "type": "range_slider",
            "channel": "socket",
            "text": "range_slider",
            "input_disable": "true",
            "data": data[0]['data']
        }

class MultiSelect(BluebotMessage):
    """
        multi_select was not present
    """

    def type_name(self):
        return "multi_select"

    def send(self, session_id, data):
        return {
            "type": "multi_select",
            "channel": "socket",
            "text": data[0]['text'],
            "input_disable": "true",
            "quick_replies": data[0]['quickreplies']
        }

class GetDirection(BluebotMessage):
    """
        get_direction was not present
    """

    def type_name(self):
        return "get_direction"

    def send(self, session_id, data):
        return {
            "type": "get_map_direction",
            "channel": "socket",
            "content": {
                "type": "get_map_direction",
                "text": "get_map_direction"
            },
            "data": data
        }

class GetOtp(BluebotMessage):
    """
        get_otp was not present
    """

    def type_name(self):
        return "get_otp"

    def send(self, session_id, data):
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

class Callbackform(BluebotMessage):
    """
        callbackform was not present
    """

    def type_name(self):
        return "callbackform"

    def send(self, session_id, data):
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

class ChatWithLiveagent(BluebotMessage):
    """
        chat_with_liveagent was not present
    """

    def type_name(self):
        return "chat_with_liveagent"

    def send(self, session_id, data):
        return {
            "type": "chat_transcript",
            "channel": "socket",
            "content": {
                "type": "chat_transcript",
                "text": "chat_transcript"
            }
        }

class EndSession(BluebotMessage):
    """
        end_session was not present
    """

    def type_name(self):
        return "end_session"

    def send(self, session_id, data):
        return {
            "type": "end_session"
        }

class RestartSession(BluebotMessage):
    """
        restart_session was not present
    """

    def type_name(self):
        return "restart_session"

    def send(self, session_id, data):
        return {
            "type": "restart_session"
        }

class Newlink(BluebotMessage):
    """
        newlink was not present
    """

    def type_name(self):
        return "newlink"

    def send(self, session_id, data):
        return {
            "is_received": True,
            "type": "newlink",
            "data": [{
                "link": data[0]
            }]
        }

class Download(BluebotMessage):
    """
        download was not present
    """

    def type_name(self):
        return "download"

    def send(self, session_id, data):
        file_send = data[0]
        return {
            "is_received": True,
            "type": "download",
            "text": "download",
            "channel": "socket",
            "data": [{"filename": file_send}]
        }

class TenancyForm(BluebotMessage):
    """
        tenancy_form was not present
    """

    def type_name(self):
        return "tenancy_form"

    def send(self, session_id, data):
        form_data = data[0]
        return {
            "type": "tenancy_form",
            "channel": "socket",
            "content": {
                "text": form_data['text'],
                "type": "tenancy_form",
                "input_disable": "true",
                "data": form_data['data']
            }
        }

class NewUserForm(BluebotMessage):
    """
        tenancy_form was not present
    """

    def type_name(self):
        return "new_user_form"

    def send_new_user_form(self, session_id, message=None):
        return {
            "type": "new_user_form",
            "channel": "socket",
            "input_disable": "true",
            "content": {
                "type": "new_user_form",
                "text": "Super! I would appreciate it if you could fill out the form (for the patient) below to help me book you in. 😎"
            }
        }



# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.image import MIMEImage
# from email import encoders
# def sendMail(to, message_text, subject, cc =[], filename=""):
#     gmail_user = 'cbcb@medcarehospital.com'  
#     gmail_password = 'QazWsx@2020'
#     email_to = to
#     # Create the container email message.
#     msg = MIMEMultipart()
#     msg['Subject'] = subject
#     msg['From'] = gmail_user
#     msg['To'] = email_to
#     msg['Cc'] = ','.join(cc)
#     message_text = message_text
#     msg.attach(MIMEText(message_text, 'plain'))
#     if filename != "":
#         with open(filename, encoding='utf8') as f:
#             attachment = MIMEText(f.read())
#             attachment.add_header('Content-Disposition', 'attachment', filename=filename)           
#             msg.attach(attachment)


#     text = msg.as_string()
#     addresses = [email_to]
#     if len(cc) > 0 :
#         addresses =  addresses + cc

#     try:  
#         server = smtplib.SMTP('smtp-mail.outlook.com', 587)
#         server.ehlo()
#         server.starttls()
#         server.ehlo()
#         server.login(gmail_user, gmail_password)
#         server.sendmail(gmail_user, ','.join(addresses), text)
#         server.quit()
#         return True
#     except smtplib.SMTPException as e:  
#         print("DEBUG ERROR SMPT: " + e)

#         return False
