from flask import Blueprint, render_template, session
import requests

integration_automation = Blueprint('integration_automation', __name__, url_prefix='/integration')

@integration_automation.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
        import os
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))
        abs_path = os.path.abspath(os.path.join(DB_DIR, db_path))
        headers['X-DB-PATH'] = abs_path
    automation = []
    try:
        resp = requests.get(f'{API_URL}/api/automation', headers=headers)
        if resp.status_code == 200:
            automation = resp.json()
    except Exception as e:
        print('Integration Automation fetch error:', e)
    return render_template('modules/integration_automation.html', automation=automation)
