from flask import Blueprint, render_template, session
import requests

inventory_manager = Blueprint('inventory_manager', __name__, url_prefix='/inventory')

@inventory_manager.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
        import os
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))
        abs_path = os.path.abspath(os.path.join(DB_DIR, db_path))
        headers['X-DB-PATH'] = abs_path
    inventory = []
    chemicals = []
    containers = []
    try:
        resp = requests.get(f'{API_URL}/api/inventory', headers=headers)
        if resp.status_code == 200:
            inventory = resp.json()
        resp2 = requests.get(f'{API_URL}/api/chemicals', headers=headers)
        if resp2.status_code == 200:
            chemicals = resp2.json()
        resp3 = requests.get(f'{API_URL}/api/containers', headers=headers)
        if resp3.status_code == 200:
            containers = resp3.json()
    except Exception as e:
        print('Inventory Manager fetch error:', e)
    return render_template('modules/inventory_manager.html', inventory=inventory, chemicals=chemicals, containers=containers)
