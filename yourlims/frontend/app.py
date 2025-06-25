from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_from_directory, g
import requests
import subprocess
import glob
import sys
import os

sys.path.append('yourlims')
from yourlims.database.utils import get_table_schema, list_tables

API_URL = 'http://localhost:5000'
API_KEY = 'your-secret-api-key'

app = Flask(__name__)
app.secret_key = 'frontend-secret-key'

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
    return render_template('index.html')

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
        schema = request.form['schema']
        result = subprocess.run(['python', 'scripts/init_db.py', '--db', db_name, '--schema', schema], capture_output=True, text=True)
        if result.returncode == 0:
            flash(f'Database {db_name} created!', 'success')
            session['db_path'] = db_name
            return redirect(url_for('index'))
        else:
            flash('Failed to create database: ' + result.stderr, 'danger')
    return render_template('create_db.html')

@app.route('/db/load_example', methods=['POST'])
def load_example():
    db_path = get_db_path()
    result = subprocess.run(['python', 'scripts/load_example_data.py', db_path], capture_output=True, text=True)
    if result.returncode == 0:
        flash('Example molecular biology lab data loaded!', 'success')
    else:
        flash('Failed to load example data: ' + result.stderr, 'danger')
    return redirect(url_for('index'))

@app.route('/tables')
def list_tables_page():
    schema = fetch_schema()
    return render_template('tables.html', schema=schema)

@app.route('/<table>')
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

@app.route('/<table>/create', methods=['GET', 'POST'])
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

@app.route('/<table>/<int:row_id>/edit', methods=['GET', 'POST'])
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

@app.route('/<table>/<int:row_id>/delete', methods=['POST'])
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
