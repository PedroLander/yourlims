from flask import Blueprint, render_template

inventory_manager = Blueprint('inventory_manager', __name__, url_prefix='/inventory')

@inventory_manager.route('/')
def index():
    return render_template('modules/inventory_manager.html')
