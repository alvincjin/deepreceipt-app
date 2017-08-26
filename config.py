import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

# keys for localhost. Change as appropriate.

RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
    
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# pagination
FLASKY_POSTS_PER_PAGE = 10
FLASKY_COMMENTS_PER_PAGE = 10

FLASKY_MAIL_SUBJECT_PREFIX = '[DeepFit]'
FLASKY_MAIL_SENDER = 'DeepFit Admin <admin@deepfit.io>'
# email server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'alvinuw' # the user name of above server to send emails
MAIL_PASSWORD = ''

# administrator list
ADMINS = ['alvinuw@gmail.com']
