from flask import Blueprint, render_template, session
import requests

sample_tracker = Blueprint('sample_tracker', __name__, url_prefix='/samples')

@sample_tracker.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
        import os
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))
        abs_path = os.path.abspath(os.path.join(DB_DIR, db_path))
        headers['X-DB-PATH'] = abs_path
    samples = []
    specimens = []
    try:
        resp = requests.get(f'{API_URL}/api/samples', headers=headers)
        if resp.status_code == 200:
            samples = resp.json()
        resp2 = requests.get(f'{API_URL}/api/specimens', headers=headers)
        if resp2.status_code == 200:
            specimens = resp2.json()
    except Exception as e:
        print('Sample Tracker fetch error:', e)
    return render_template('modules/sample_tracker.html', samples=samples, specimens=specimens)
