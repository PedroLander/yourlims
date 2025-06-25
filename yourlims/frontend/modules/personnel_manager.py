from flask import Blueprint, render_template

personnel_manager = Blueprint('personnel_manager', __name__, url_prefix='/personnel')

@personnel_manager.route('/')
def index():
    return render_template('modules/personnel_manager.html')
