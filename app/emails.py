from flask import render_template, current_app
from flask_mail import Message
from app import mail
from config import ADMINS
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    app = current_app._get_current_object()
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
   

def send_emails(subject, text_body, recipient):
    app = current_app._get_current_object()
    recipients_list = list()
    recipients_list.append(recipient)
    msg = Message(subject, sender=ADMINS[0], recipients=recipients_list)
    msg.body = text_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
    

def follower_notification(followed, follower):
    send_email(
        "[DeepFit] %s is now following you!" % follower.nickname,
        ADMINS[0],
        [followed.email],
        render_template("follower_email.txt", user=followed, follower=follower),
        render_template("follower_email.html", user=followed, follower=follower)
    )
