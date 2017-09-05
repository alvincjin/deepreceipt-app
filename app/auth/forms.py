from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, validators
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from flask_wtf.recaptcha import RecaptchaField
from ..models import User


class LoginForm(FlaskForm):
    email = StringField("Email", [validators.required("Please enter your email address."),
                                  Email("Please enter your email address.")])
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


class SignupForm(FlaskForm):
    firstname = StringField("First name",  validators=[
        DataRequired(), Length(1, 10),
        Regexp('^[A-Za-z]', 0, 'Usernames must have only letters')])

    lastname = StringField("Last name",   validators=[
        DataRequired(), Length(1, 10),
        Regexp('^[A-Za-z]', 0, 'Usernames must have only letters')])
    email = StringField("Email",  [validators.required("Please enter your email address."),
                                   validators.Email("Please enter your email address.")])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    # Select fields keep a choices property which is a sequence of (value, label) pairs.
    user_role = SelectField('Role', choices=[('applicant', 'Applicant'), ('adviser', 'Adviser')])
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
