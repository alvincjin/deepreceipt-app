from flask import render_template
from flask_mail import Message
from app import mail
from decorators import async
from config import ADMINS

@async    
def send_async_email(msg):
    mail.send(msg)
    
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(msg)
   

def send_emails(subject, text_body, recipient):
    recipients_list = []
    recipients_list.append(recipient)
    msg = Message(subject, sender = ADMINS[0], recipients = recipients_list)
    msg.body = text_body
    send_async_email(msg)
    

    
def follower_notification(followed, follower):
    send_email("[microblog] %s is now following you!" % follower.nickname,
        ADMINS[0],
        [followed.email],
        render_template("follower_email.txt", 
            user = followed, follower = follower),
        render_template("follower_email.html", 
            user = followed, follower = follower))
        
