from flask import Blueprint, render_template

qa_qc = Blueprint('qa_qc', __name__, url_prefix='/qa')

@qa_qc.route('/')
def index():
    return render_template('modules/qa_qc.html')
