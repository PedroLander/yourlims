from flask import Blueprint, render_template, session, current_app
import requests
import os

experiment_manager = Blueprint('experiment_manager', __name__, url_prefix='/experiments')

@experiment_manager.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))
        abs_path = os.path.abspath(os.path.join(DB_DIR, db_path))
        headers['X-DB-PATH'] = abs_path
    studies = []
    assays = []
    try:
        resp = requests.get(f'{API_URL}/api/studies', headers=headers)
        if resp.status_code == 200:
            studies = resp.json()
        resp2 = requests.get(f'{API_URL}/api/assays', headers=headers)
        if resp2.status_code == 200:
            assays = resp2.json()
    except Exception as e:
        print('Experiment Manager fetch error:', e)
    return render_template('modules/experiment_manager.html', studies=studies, assays=assays)
