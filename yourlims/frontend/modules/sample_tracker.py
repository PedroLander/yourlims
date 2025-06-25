from flask import Blueprint, render_template

sample_tracker = Blueprint('sample_tracker', __name__, url_prefix='/samples')

@sample_tracker.route('/')
def index():
    return render_template('modules/sample_tracker.html')
