from flask import Blueprint, render_template, session, request, redirect, url_for, flash
import requests
import os
import json

integration_automation = Blueprint('integration_automation', __name__, url_prefix='/integration')

@integration_automation.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
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

@integration_automation.route('/config', methods=['GET', 'POST'])
def config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases/equipment_config.json'))
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            config_data = json.load(f)
    if request.method == 'POST' and session.get('role') == 'admin':
        config_data = {
            'ip': request.form.get('ip'),
            'port': request.form.get('port'),
            'protocol': request.form.get('protocol'),
            'description': request.form.get('description')
        }
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
        flash('Equipment connection configuration saved.', 'success')
        return redirect(url_for('integration_automation.config'))
    return render_template('modules/integration_config.html', config=config_data)
