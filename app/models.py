from datetime import datetime
from app import db
from app.exceptions import ValidationError
from flask import current_app, url_for
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from . import lm

ROLE_APPLICANT = 0
ROLE_ADVISER = 1
ROLE_ADMIN = 2

HOUSE = 0
CONDO = 1


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), unique=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120), index=True, unique=True)
    pwdhash = db.Column(db.String(54))
    phone = db.Column(db.Integer)
    address = db.Column(db.String(64))
    confirmed = db.Column(db.Boolean, default=False)

    role = db.Column(db.SmallInteger, default=ROLE_APPLICANT)
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    posts = db.relationship('Post', order_by="Post.timestamp", backref='author',
                            lazy='dynamic', cascade="all, delete, delete-orphan")
    about_me = db.Column(db.Text())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    portrait = db.Column(db.String(140))
    pref = db.relationship('Preference', uselist=False, backref='author')
    fav = db.relationship('Favourite', backref='user', lazy='dynamic')

    active = db.Column(db.Boolean, default=False)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
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

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def is_authenticated(self):
        return True

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.confirmed = True
        db.session.add(self)
        return True

    def to_json(self):
        json_user = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'nickname': self.nickname,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'post_count': self.posts.count(),
        }
        return json_user

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def is_active(self):
        if self.active is True:
            return True
        else:
            return False

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % self.nickname


class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(1400))
    img = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    location = db.Column(db.String(140))
    price = db.Column(db.Integer)
    interested_user = db.relationship('Favourite', backref='author', lazy='dynamic',
                                      cascade="all, delete, delete-orphan")
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    style = db.Column(db.String(10), default="house")
    bedroom_no = db.Column(db.Integer, default=1)
    bathroom_no = db.Column(db.Integer, default=1)
    garage_no = db.Column(db.Integer, default=0)
    address = db.Column(db.String(100))
    coordinate = db.Column(db.String(50))

    def __repr__(self):
        return '<Post %r>' % (self.body)

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'title': self.title,
            'body': self.body,
            'author': url_for('api.get_user', id=self.user_id, _external=True),
            'location': self.location,
            'timestamp': self.timestamp,
            'price': self.price,
            'style': self.style,
            'bedroom_no': self.bedroom_no,
            'bathroom_no': self.bathroom_no,
            'garage_no': self.garage_no,
            'address': self.address,
            'comments': url_for('api.get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


class Favourite(db.Model):
    __tablename__ = 'favourites'
    id = db.Column(db.String(10), primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __init__(self, user_id, post_id):
        self.id = str(user_id) + ':' + str(post_id)
        self.user_id = user_id
        self.post_id = post_id


class Preference(db.Model):
    __tablename__ = 'preferences'
    id = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.String(10), default="house")
    bedroom_no = db.Column(db.Integer)
    bathroom_no = db.Column(db.Integer)
    garage_no = db.Column(db.Integer)
    location = db.Column(db.String(140))
    price = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    notify = db.Column(db.SmallInteger, default=1)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)
