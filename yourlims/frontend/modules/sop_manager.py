from flask import Blueprint, render_template

sop_manager = Blueprint('sop_manager', __name__, url_prefix='/sop')

@sop_manager.route('/')
def index():
    return render_template('modules/sop_manager.html')
