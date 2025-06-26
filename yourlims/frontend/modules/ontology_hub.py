from flask import Blueprint, render_template, session
import requests

ontology_hub = Blueprint('ontology_hub', __name__, url_prefix='/ontology')

@ontology_hub.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
        import os
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))
        abs_path = os.path.abspath(os.path.join(DB_DIR, db_path))
        headers['X-DB-PATH'] = abs_path
    interchange = []
    omics_data = []
    try:
        resp = requests.get(f'{API_URL}/api/interchange', headers=headers)
        if resp.status_code == 200:
            interchange = resp.json()
        resp2 = requests.get(f'{API_URL}/api/omics_data', headers=headers)
        if resp2.status_code == 200:
            omics_data = resp2.json()
    except Exception as e:
        print('Ontology Hub fetch error:', e)
    return render_template('modules/ontology_hub.html', interchange=interchange, omics_data=omics_data)
