from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_from_directory, g
import requests
import subprocess
import glob
import sys
import os

sys.path.append('yourlims')
from yourlims.database.utils import get_table_schema, list_tables
from yourlims.frontend.modules.experiment_manager import experiment_manager
from yourlims.frontend.modules.sample_tracker import sample_tracker
from yourlims.frontend.modules.inventory_manager import inventory_manager
from yourlims.frontend.modules.instrument_manager import instrument_manager
from yourlims.frontend.modules.sop_manager import sop_manager
from yourlims.frontend.modules.personnel_manager import personnel_manager
from yourlims.frontend.modules.qa_qc import qa_qc
from yourlims.frontend.modules.results_reporting import results_reporting
from yourlims.frontend.modules.ontology_hub import ontology_hub
from yourlims.frontend.modules.integration_automation import integration_automation
from yourlims.frontend.modules.accounting import accounting
from yourlims.frontend.modules.profile import profile

API_URL = 'http://localhost:5000'
API_KEY = 'your-secret-api-key'

app = Flask(__name__)
app.secret_key = 'frontend-secret-key'

# Register blueprints for all modules
app.register_blueprint(experiment_manager)
app.register_blueprint(sample_tracker)
app.register_blueprint(inventory_manager)
app.register_blueprint(instrument_manager)
app.register_blueprint(sop_manager)
app.register_blueprint(personnel_manager)
app.register_blueprint(qa_qc)
app.register_blueprint(results_reporting)
app.register_blueprint(ontology_hub)
app.register_blueprint(integration_automation)
app.register_blueprint(accounting)
app.register_blueprint(profile)

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../databases'))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = 'lims.db'

def api_headers():
    headers = {'X-API-KEY': API_KEY}
    db_path = get_db_path()
    print(f"[FRONTEND DEBUG] Using db_path: {db_path}")  # DEBUG
    if db_path:
        headers['X-DB-PATH'] = db_path
    return headers

def get_db_path():
    db = session.get('db_path')
    if not db:
        print('[FRONTEND ERROR] No database selected in session.')
        return None
    abs_path = os.path.abspath(os.path.join(DB_DIR, db))
    if not os.path.exists(abs_path):
        print(f'[FRONTEND ERROR] Database file does not exist: {abs_path}')
    else:
        print(f'[FRONTEND DEBUG] Using db_path: {abs_path}')
    return abs_path

def fetch_schema():
    resp = requests.get(f'{API_URL}/api/schema', headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return {}

@app.route('/')
def index():
    # Gather stats for overview
    db_path = get_db_path()
    stats = {
        'personnel_count': 0,
        'instrument_count': 0,
        'sample_count': 0,
        'inventory_count': 0,
        'recent_activity': []
    }
    if db_path:
        import sqlite3
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            c.execute('SELECT COUNT(*) FROM staff'); stats['personnel_count'] = c.fetchone()[0]
            c.execute('SELECT COUNT(*) FROM instruments'); stats['instrument_count'] = c.fetchone()[0]
            c.execute('SELECT COUNT(*) FROM samples'); stats['sample_count'] = c.fetchone()[0]
            c.execute('SELECT COUNT(*) FROM inventory'); stats['inventory_count'] = c.fetchone()[0]
            # Recent activity: last 5 tests or samples
            c.execute('SELECT name, collected_at FROM samples ORDER BY collected_at DESC LIMIT 3')
            stats['recent_activity'] += [f"Sample '{row[0]}' collected on {row[1]}" for row in c.fetchall()]
            c.execute('SELECT test_type, tested_at FROM tests ORDER BY tested_at DESC LIMIT 2')
            stats['recent_activity'] += [f"Test '{row[0]}' performed on {row[1]}" for row in c.fetchall()]
        except Exception as e:
            pass
        conn.close()
    return render_template('index.html', stats=stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        resp = requests.post(f'{API_URL}/users', json={'username': username, 'role': role}, headers=api_headers())
        if resp.status_code == 201:
            flash('User registered successfully!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        # For demo: just check if user exists
        resp = requests.get(f'{API_URL}/users', headers=api_headers())
        users = resp.json() if resp.status_code == 200 else []
        user = next((u for u in users if u['username'] == username), None)
        if user:
            session['username'] = username
            session['role'] = user['role']
            flash('Logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/samples/create', methods=['GET', 'POST'])
def create_sample_page():
    if request.method == 'POST':
        name = request.form['name']
        collected_by = session.get('username', 'unknown')
        collected_at = request.form['collected_at']
        resp = requests.post(f'{API_URL}/samples', json={'name': name, 'collected_by': collected_by, 'collected_at': collected_at}, headers=api_headers())
        if resp.status_code == 201:
            flash('Sample created!', 'success')
            return redirect(url_for('samples'))
        else:
            flash('Failed to create sample', 'danger')
    return render_template('create_sample.html')

@app.route('/tests/create', methods=['GET', 'POST'])
def create_test_page():
    if request.method == 'POST':
        sample_id = request.form['sample_id']
        test_type = request.form['test_type']
        result = request.form['result']
        tested_at = request.form['tested_at']
        resp = requests.post(f'{API_URL}/tests', json={'sample_id': sample_id, 'test_type': test_type, 'result': result, 'tested_at': tested_at}, headers=api_headers())
        if resp.status_code == 201:
            flash('Test created!', 'success')
            return redirect(url_for('tests'))
        else:
            flash('Failed to create test', 'danger')
    return render_template('create_test.html')

@app.route('/db/select', methods=['GET', 'POST'])
def select_db():
    dbs = [f for f in os.listdir(DB_DIR) if f.endswith('.db')]
    if request.method == 'POST':
        # Handle file upload if present
        if 'dbFile' in request.files and request.files['dbFile'].filename:
            file = request.files['dbFile']
            filename = file.filename
            if not filename.endswith('.db'):
                flash('Please select a valid .db file.', 'danger')
                return redirect(url_for('select_db'))
            save_path = os.path.join(DB_DIR, filename)
            file.save(save_path)
            session['db_path'] = filename
            flash(f'Uploaded and selected database: {filename}', 'success')
            return redirect(url_for('index'))
        # Handle radio selection
        db_path = request.form.get('db_path')
        if db_path:
            session['db_path'] = db_path
            flash(f'Selected database: {db_path}', 'success')
            return redirect(url_for('index'))
    return render_template('select_db.html', dbs=dbs, current=get_db_path())

@app.route('/db/create', methods=['GET', 'POST'])
def create_db():
    if request.method == 'POST':
        db_name = request.form['db_name']
        schemas = request.form.getlist('schemas')
        # Join schema filenames as comma-separated string for backend script
        schema_arg = ','.join(schemas)
        result = subprocess.run(['python', 'scripts/init_db.py', '--db', db_name, '--schemas', schema_arg], capture_output=True, text=True)
        if result.returncode == 0:
            flash(f'Database {db_name} created!', 'success')
            session['db_path'] = db_name
            return redirect(url_for('index'))
        else:
            flash('Failed to create database: ' + result.stderr, 'danger')
    return render_template('create_db.html')

@app.route('/db/load_example', methods=['POST'])
def load_example():
    # Step 1: Create a new example database with all schemas
    db_name = 'example_lims.db'
    DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../databases'))
    db_path = os.path.join(DB_DIR, db_name)
    all_schemas = [
        'international.json',
        'experimental_metadata.json',
        'domain_metadata.json',
        'biosample_metadata.json',
        'chemicals_inventory.json',
        'logistics_inventory.json',
        'instrument_data.json',
        'staff_competency.json',
        'automation_integration.json',
        'quality_compliance.json',
        'results_representation.json',
        'data_interchange.json'
    ]
    schema_arg = ','.join(all_schemas)
    result = subprocess.run(['python', 'scripts/init_db.py', '--db', db_name, '--schemas', schema_arg], capture_output=True, text=True)
    if result.returncode != 0:
        flash('Failed to create example database: ' + result.stderr, 'danger')
        return redirect(url_for('index'))
    # Step 2: Populate the new database with example data
    result2 = subprocess.run(['python', 'scripts/load_example_data.py', db_path], capture_output=True, text=True)
    if result2.returncode == 0:
        flash('Example molecular biology lab data loaded!', 'success')
        session['db_path'] = db_name
    else:
        flash('Failed to load example data: ' + result2.stderr, 'danger')
    return redirect(url_for('index'))

@app.route('/tables')
def list_tables_page():
    schema = fetch_schema()
    return render_template('tables.html', schema=schema)

@app.route('/tables/<table>')
def show_table(table):
    schema = fetch_schema()
    columns = [col['name'] for col in schema.get(table, [])]
    import requests
    resp = requests.get(f'{API_URL}/api/{table}', headers=api_headers())
    if resp.status_code == 200:
        data = resp.json()
    else:
        data = []
    return render_template('table.html', table=table, rows=data, columns=columns)

@app.route('/tables/<table>/create', methods=['GET', 'POST'])
def create_row(table):
    db_path = get_db_path()
    columns = [col[1] for col in get_table_schema(db_path, table) if col[1] != get_table_schema(db_path, table)[0][1]]
    if request.method == 'POST':
        data = {col: request.form[col] for col in columns if col in request.form}
        import requests
        resp = requests.post(f'{API_URL}/api/{table}', json=data, headers=api_headers())
        if resp.status_code == 201:
            flash(f'{table.capitalize()} entry created!', 'success')
            return redirect(url_for('show_table', table=table))
        else:
            flash('Error: ' + resp.text, 'danger')
    return render_template('dynamic_form.html', table=table, columns=columns, action='Create')

@app.route('/tables/<table>/<int:row_id>/edit', methods=['GET', 'POST'])
def edit_row(table, row_id):
    db_path = get_db_path()
    columns = [col[1] for col in get_table_schema(db_path, table)]
    import requests
    resp = requests.get(f'{API_URL}/api/{table}/{row_id}', headers=api_headers())
    if resp.status_code != 200:
        abort(404)
    row = resp.json()
    if request.method == 'POST':
        data = {col: request.form[col] for col in columns if col in request.form}
        resp2 = requests.put(f'{API_URL}/api/{table}/{row_id}', json=data, headers=api_headers())
        if resp2.status_code == 200:
            flash(f'{table.capitalize()} entry updated!', 'success')
            return redirect(url_for('show_table', table=table))
        else:
            flash('Error: ' + resp2.text, 'danger')
    return render_template('dynamic_form.html', table=table, columns=columns, row=row, action='Edit')

@app.route('/tables/<table>/<int:row_id>/delete', methods=['POST'])
def delete_row(table, row_id):
    import requests
    resp = requests.delete(f'{API_URL}/api/{table}/{row_id}', headers=api_headers())
    if resp.status_code == 200:
        flash(f'{table.capitalize()} entry deleted!', 'success')
    else:
        flash('Error: ' + resp.text, 'danger')
    return redirect(url_for('show_table', table=table))

@app.before_request
def require_db_selected():
    allowed_routes = ['select_db', 'create_db', 'index', 'static']
    if request.endpoint not in allowed_routes and not get_db_path():
        flash('Please select a database first.', 'warning')
        return redirect(url_for('select_db'))

@app.before_request
def update_db_badge():
    g.db_path = session.get('db_path')

@app.context_processor
def inject_schema():
    db_path = get_db_path()
    def get_schema(table):
        try:
            return get_table_schema(db_path, table)
        except Exception:
            return []
    def get_tables():
        try:
            return list_tables(db_path)
        except Exception:
            return []
    def get_db_path_for_badge():
        return session.get('db_path') or 'None'
    return dict(get_schema=get_schema, get_tables=get_tables, get_db_path=get_db_path_for_badge)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
