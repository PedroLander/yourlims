from flask import Blueprint, render_template, session
import requests
import os

results_reporting = Blueprint('results_reporting', __name__, url_prefix='/results')

@results_reporting.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))
        abs_path = os.path.abspath(os.path.join(DB_DIR, db_path))
        headers['X-DB-PATH'] = abs_path
    results = []
    try:
        resp = requests.get(f'{API_URL}/api/results', headers=headers)
        if resp.status_code == 200:
            results = resp.json()
    except Exception as e:
        print('Results Reporting fetch error:', e)
    return render_template('modules/results_reporting.html', results=results)
