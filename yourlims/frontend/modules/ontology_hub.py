from flask import Blueprint, render_template

ontology_hub = Blueprint('ontology_hub', __name__, url_prefix='/ontology')

@ontology_hub.route('/')
def index():
    return render_template('modules/ontology_hub.html')
