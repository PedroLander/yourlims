from flask import Blueprint, render_template

integration_automation = Blueprint('integration_automation', __name__, url_prefix='/integration')

@integration_automation.route('/')
def index():
    return render_template('modules/integration_automation.html')
