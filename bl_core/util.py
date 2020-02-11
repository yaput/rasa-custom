import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email import encoders

def sendMail(user, password, to, attachments, message_text, subject, cc =[], smptp_service="gmail"):
    """Gmail Sending Email Server"""
    gmail_user = user #'blbotcrew@gmail.com'  
    gmail_password = password #'BlueLogic@123'
    email_to = to
    # Create the container email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = email_to
    msg['Cc'] = ','.join(cc)
    message_text = message_text
    msg.attach(MIMEText(message_text, 'plain'))
    # Open the files in binary mode.  Use imghdr to figure out the
    # MIME subtype for each specific image.
    for attachment in attachments:
        with open(attachment, 'rb') as fp:
            img_data = fp.read()
            img = MIMEImage(img_data)
            msg.attach(img)


    text = msg.as_string()
    addresses = [email_to]
    if len(cc) > 0 :
        addresses =  addresses + cc

    try:  
        smtp_service_url = 'smtp-mail.outlook.com'
        port_smtp = 587
        if smptp_service == "gmail":
            smtp_service_url = 'smtp.gmail.com'
            port_smtp = 465
        server = smtplib.SMTP_SSL(smtp_service_url, port_smtp)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, ','.join(addresses), text)
        server.quit()
        return True
    except:  
        return False
