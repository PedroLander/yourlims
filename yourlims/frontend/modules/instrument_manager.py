from flask import Blueprint, render_template

instrument_manager = Blueprint('instrument_manager', __name__, url_prefix='/instruments')

@instrument_manager.route('/')
def index():
    return render_template('modules/instrument_manager.html')
