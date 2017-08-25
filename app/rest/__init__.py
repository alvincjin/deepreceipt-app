from flask import Blueprint

rest_bp = Blueprint('rest', __name__)

from . import tasks