from flask import Blueprint

rest = Blueprint('rest', __name__)

from . import tasks