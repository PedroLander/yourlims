from flask import Blueprint, render_template, session
import requests

sop_manager = Blueprint('sop_manager', __name__, url_prefix='/sop')

@sop_manager.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
        import os
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))
        abs_path = os.path.abspath(os.path.join(DB_DIR, db_path))
        headers['X-DB-PATH'] = abs_path
    sops = []
    audit_trails = []
    try:
        resp = requests.get(f'{API_URL}/api/sops', headers=headers)
        if resp.status_code == 200:
            sops = resp.json()
        resp2 = requests.get(f'{API_URL}/api/audit_trails', headers=headers)
        if resp2.status_code == 200:
            audit_trails = resp2.json()
    except Exception as e:
        print('SOP Manager fetch error:', e)
    return render_template('modules/sop_manager.html', sops=sops, audit_trails=audit_trails)
