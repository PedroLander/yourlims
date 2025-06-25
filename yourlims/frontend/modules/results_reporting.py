from flask import Blueprint, render_template

results_reporting = Blueprint('results_reporting', __name__, url_prefix='/results')

@results_reporting.route('/')
def index():
    return render_template('modules/results_reporting.html')
