from flask import Blueprint
ads_bp = Blueprint('ads', __name__, template_folder='templates')
from app.ads import routes  # noqa
