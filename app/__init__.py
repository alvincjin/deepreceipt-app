from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from flask_moment import Moment
from flask_admin import Admin
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
admin = Admin(name='DeepFit')
lm = LoginManager()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)

    lm.session_protection = 'strong'
    lm.login_view = 'auth.login'  # need right namespace
    lm.init_app(app)

    bootstrap = Bootstrap(app)
    moment = Moment(app)
    admin.init_app(app)
    mail.init_app(app)

    if not app.debug:
        import logging
        from logging.handlers import SMTPHandler
        from logging.handlers import RotatingFileHandler

        credentials = None
        if MAIL_USERNAME or MAIL_PASSWORD:
            credentials = (MAIL_USERNAME, MAIL_PASSWORD)
        mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'DeepFit Webapp failure', credentials)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        file_handler = RotatingFileHandler('tmp/deepfit-app.log', 'a', 1 * 1024 * 1024, 10)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('DeepFit App Startup')

        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)

        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')

        from .api import api as api_blueprint
        app.register_blueprint(api_blueprint, url_prefix='/api')

        return app

from app import models


