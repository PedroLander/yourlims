from flask import Blueprint, render_template

accounting = Blueprint('accounting', __name__, url_prefix='/accounting')

@accounting.route('/')
def index():
    return render_template('modules/accounting.html')
