from flask import Blueprint, render_template

experiment_manager = Blueprint('experiment_manager', __name__, url_prefix='/experiments')

@experiment_manager.route('/')
def index():
    return render_template('modules/experiment_manager.html')
