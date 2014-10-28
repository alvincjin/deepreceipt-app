from hashlib import md5
from app import db
from app import app
import flask.ext.whooshalchemy as whooshalchemy
from werkzeug import generate_password_hash, check_password_hash
ROLE_USER = 0
ROLE_ADMIN = 1

HOUSE = 0
CONDO = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), unique = True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120), index = True, unique = True)
    pwdhash = db.Column(db.String(54))
    phone = db.Column(db.Integer)
   
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    posts = db.relationship('Post', order_by="Post.timestamp", backref = 'author', lazy = 'dynamic',cascade="all, delete, delete-orphan")
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    portrait = db.Column(db.String(140))
    pref = db.relationship('Preference', uselist=False, backref = 'author')
    fav = db.relationship('Favourite', backref = 'user', lazy = 'dynamic')
    
    active = db.Column(db.Boolean, default = False)

    @staticmethod
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
    
    def __init__(self, nickname, firstname, lastname, email, password, role):
        self.nickname = nickname.title()
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.set_password(password)
        self.role = role
     
    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)
   
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)
   
    def is_authenticated(self):
        return True

    def is_active(self):
        if self.active == True:
            return True
        else:
            return False

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)
     
    def __repr__(self):
        return '<User %r>' % (self.nickname)    
        
class Post(db.Model):
    __searchable__ = ['body']
    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(1400))
    img = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    location = db.Column(db.String(140))
    price = db.Column(db.Integer)
    interested_user = db.relationship('Favourite', backref = 'author', lazy = 'dynamic',cascade="all, delete, delete-orphan")
    style = db.Column(db.String(10), default = "house")
    bedroom_no = db.Column(db.Integer, default = 1)
    bathroom_no = db.Column(db.Integer, default = 1)
    garage_no = db.Column(db.Integer, default = 0)
    address = db.Column(db.String(100))
    coordinate = db.Column(db.String(50))

    def __repr__(self):
        return '<Post %r>' % (self.body)
'''
#Create M2M table
user_favourite_table = db.Table('Favourite', db.Model.metadata,
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                db.Column('post_id', db.Integer, db.ForeignKey('post.id')) 
                                )

'''
class Favourite(db.Model):
   
    id = db.Column(db.String(10), primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __init__(self, user_id, post_id):
        self.id = str(user_id)+':'+str(post_id)
        self.user_id = user_id
        self.post_id = post_id


class Preference(db.Model):
       
    id = db.Column(db.Integer, primary_key = True)
    style = db.Column(db.String(10), default = "house")
    bedroom_no = db.Column(db.Integer)
    bathroom_no = db.Column(db.Integer)
    garage_no = db.Column(db.Integer)
    location = db.Column(db.String(140))
    price = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    notify = db.Column(db.SmallInteger, default = 1)

    
            
whooshalchemy.whoosh_index(app, Post)
