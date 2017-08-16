from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, RadioField,SelectField,IntegerField, FileField,SubmitField,validators, ValidationError, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.recaptcha import RecaptchaField
from .. models import User


class EditForm(FlaskForm):
    nickname = StringField('nickname', validators = [DataRequired()])
    about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])
    phone = IntegerField('phone')
    fileName = FileField()

    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname
        
    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname = self.nickname.data).first()
        
        if user is not None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True


class PostForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    style = SelectField('Property Type', choices=[('House', 'House'), ('Town House','Town House'),
                                                  ('Condo', 'Condo'), ('Apartment','Apartment')])
    bedroom_no = IntegerField('Bedroom', validators = [NumberRange(min=1, max= 5)])
    bathroom_no = IntegerField('Bathroom', validators = [NumberRange(min=1, max= 5)])
    garage_no = IntegerField('Garage', validators = [NumberRange(min=0, max= 4)])
    body = TextAreaField('Body')
    fileName = FileField()
    location = location = SelectField('City', choices=[('Toronto', 'Toronto'), ('Mississauga', 'Mississauga'),
                                                       ('Markham','Markham'),('Richmond Hill','Richmond Hill'),
                                                       ('Vaughan','Vaughan'),('Milton','Milton')])
    price = IntegerField('Price', validators = [NumberRange(min=100000, max= 10000000)])
    address = StringField('Address')
    

class ContactForm(FlaskForm):
    name = StringField("Name",  [validators.required("Please enter your name.")])
    email = StringField("Email",  [validators.required("Please enter your email address."),
                                   validators.Email("e.g. user@example.com")])
    subject = StringField("Subject",  [validators.required("Please enter a subject.")])
    message = TextAreaField("Message",  [validators.required("Please enter a message.")])
    submit = SubmitField("Send")


class SignupForm(FlaskForm):
    firstname = StringField("First name",  [validators.required("Please enter your first name.")])
    lastname = StringField("Last name",  [validators.required("Please enter your last name.")])
    email = StringField("Email",  [validators.required("Please enter your email address."),
                                   validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.required("Please enter a password.")])
    # Select fields keep a choices property which is a sequence of (value, label) pairs.
    user_role = SelectField('Role', choices=[('user', 'User'), ('agent', 'Agent')])
    recaptcha = RecaptchaField()
    submit = SubmitField("Create account")
 
    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
 
    def validate(self):
        if not FlaskForm.validate(self):
            return False
        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append("That email is already taken")
            return False
        else:
            return True

'''
class SigninForm(FlaskForm):
    email = StringField("Email", [validators.required("Please enter your email address."),
                                  validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.required("Please enter a password.")])
    remember_me = BooleanField('Remember me', default = False)
    submit = SubmitField("Sign In")
    
    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
 
    def validate(self):
        if not FlaskForm.validate(self):
            return False
     
        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append("Invalid e-mail or password")
            return False
'''

class PeferForm(FlaskForm):
    style = SelectField('Property Type', choices=[('House', 'House'), ('Town House','Town House'),
                                                  ('Condo', 'Condo'), ('Apartment','Apartment')])
    bedroom_no = IntegerField('Bedroom', default = 3, validators = [NumberRange(min=1, max= 5)])
    bathroom_no = IntegerField('Bathroom', default = 3, validators = [NumberRange(min=1, max= 5)])
    garage_no = IntegerField('Garage', default = 1, validators = [NumberRange(min=0, max= 4)])
    notify = BooleanField('Notify Me', default = True)
    location = SelectField('Location', choices=[('Toronto', 'Toronto'), ('Mississauga', 'Mississauga'),
                                                ('Markham','Markham'),('Richmond Hill','Richmond Hill'),
                                                ('Vaughan','Vaughan'),('Milton','Milton')])
    price = IntegerField('Price', validators = [NumberRange(min=100000, max= 10000000)])
    
    submit = SubmitField("Send")
    
    def validate(self):
        return True

    
class OrderForm(FlaskForm):
    order = SelectField('Sort By', choices=[('price', 'Price'), ('location', 'Location'),
                                            ('style','Type'), ('date','Date')])