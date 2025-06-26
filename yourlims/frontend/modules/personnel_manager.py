from flask import Blueprint, render_template, session
import requests

personnel_manager = Blueprint('personnel_manager', __name__, url_prefix='/personnel')

@personnel_manager.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
        import os
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))
        abs_path = os.path.abspath(os.path.join(DB_DIR, db_path))
        headers['X-DB-PATH'] = abs_path
    staff = []
    try:
        resp = requests.get(f'{API_URL}/api/staff', headers=headers)
        if resp.status_code == 200:
            staff = resp.json()
    except Exception as e:
        print('Personnel Manager fetch error:', e)
    return render_template('modules/personnel_manager.html', staff=staff)
