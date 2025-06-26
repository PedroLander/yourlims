from flask import Blueprint, render_template, session
import requests
from collections import Counter
from datetime import datetime

instrument_manager = Blueprint('instrument_manager', __name__, url_prefix='/instruments')

@instrument_manager.route('/')
def index():
    API_URL = 'http://localhost:5000'
    headers = {'X-API-KEY': 'your-secret-api-key'}
    db_path = session.get('db_path')
    if db_path:
        import os
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))
        abs_path = os.path.abspath(os.path.join(DB_DIR, db_path))
        headers['X-DB-PATH'] = abs_path
    instruments = []
    calibrations = []
    try:
        resp = requests.get(f'{API_URL}/api/instruments', headers=headers)
        if resp.status_code == 200:
            instruments = resp.json()
        resp2 = requests.get(f'{API_URL}/api/calibrations', headers=headers)
        if resp2.status_code == 200:
            calibrations = resp2.json()
    except Exception as e:
        print('Instrument Manager fetch error:', e)
    # Calculate calibrations per year
    cal_years = [datetime.strptime(c['date'], '%Y-%m-%d').year for c in calibrations if c.get('date')]
    year_counts = dict(Counter(cal_years))
    year_labels = list(sorted(year_counts.keys()))
    year_data = [year_counts[y] for y in year_labels]
    return render_template('modules/instrument_manager.html', instruments=instruments, calibrations=calibrations, year_labels=year_labels, year_data=year_data)
