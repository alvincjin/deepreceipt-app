from hashlib import md5
from app import db
from app import app
import flask_whooshalchemy as whooshalchemy
from werkzeug import generate_password_hash, check_password_hash

ROLE_USER = 0
ROLE_ADMIN = 1


class User(db.Document):
    nickname = db.StringField(max_length=10,unique=True)
    firstname = db.StringField(max_length=10)
    lastname = db.StringField(max_length=10)
    pwdhash = db.StringField(max_length=54)
    email = db.StringField(max_length=25, required=True,unique=True)
    role = db.IntField(default = ROLE_USER)
    about_me = db.StringField(max_length=50)
    last_seen = db.DateTimeField(default=datetime.datetime.now, required=True)

"""    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname
 """       
    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.set_password(password)
     
    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)
   
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)
    
    def __repr__(self):
        return '<User %r>' % (self.nickname)    
        
class Post(Document):
    title = db.StringField(max_length=255, required=True)
    body = db.StringField(max_length=1500,required=True)
    img = db.StringField(max_length=255)
    timestamp = db.DateTimeField(default=datetime.datetime.now, required=True)
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))
    author = db.StringField(max_length=55)

    def __repr__(self):
        return '<Post %r>' % (self.body)

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


class Comment(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    body = db.StringField(verbose_name="Comment", required=True)
    author = db.StringField(verbose_name="Name", max_length=255, required=True)


        
#whooshalchemy.whoosh_index(app, Post)
