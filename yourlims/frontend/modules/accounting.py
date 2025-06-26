from flask import Blueprint, render_template, session
import requests
import os
import sqlite3

accounting = Blueprint('accounting', __name__, url_prefix='/accounting')

@accounting.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))
        abs_path = os.path.abspath(os.path.join(DB_DIR, db_path))
        headers['X-DB-PATH'] = abs_path
    inventory = []
    chemicals = []
    accounting_data = []
    try:
        resp = requests.get(f'{API_URL}/api/inventory', headers=headers)
        if resp.status_code == 200:
            inventory = resp.json()
        resp2 = requests.get(f'{API_URL}/api/chemicals', headers=headers)
        if resp2.status_code == 200:
            chemicals = resp2.json()
        # Directly query accounting table
        if db_path:
            conn = sqlite3.connect(abs_path)
            c = conn.cursor()
            c.execute('SELECT year, budget, spent, balance, last_update FROM accounting ORDER BY year DESC')
            accounting_data = [dict(zip(['year','budget','spent','balance','last_update'], row)) for row in c.fetchall()]
            conn.close()
    except Exception as e:
        print('Accounting fetch error:', e)
    return render_template('modules/accounting.html', inventory=inventory, chemicals=chemicals, accounting_data=accounting_data)
