from flask_httpauth import HTTPBasicAuth
from flask import g, jsonify
from ..models import User
from .errors import unauthorized, forbidden
from . import api_bp

auth = HTTPBasicAuth()


@api_bp.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@auth.verify_password
def verify_password(email_or_token, password):
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.check_password(password)


@api_bp.route('/token')
def get_token():
    if g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600),
                    'expiration': 3600})


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')
