from flask import Flask, request, jsonify
from functools import wraps
import sqlite3
import os
from yourlims.database.utils import get_table_schema, list_tables

app = Flask(__name__)

API_KEY = 'your-secret-api-key'  # Change this to a secure value

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.endpoint == 'index':
            return f(*args, **kwargs)
        key = request.headers.get('X-API-KEY')
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def get_connection(db_path=None):
    if db_path is None:
        db_path = request.headers.get('X-DB-PATH')
    # Always resolve DB_DIR relative to the project root, not the current file
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.realpath(os.path.join(project_root, 'databases'))
    db_path = os.path.realpath(db_path)
    print(f"[API DEBUG] Using db_path: {db_path}")  # DEBUG
    if not db_path:
        print("[API ERROR] No database selected. Please select a database.")
        raise Exception('No database selected. Please select a database.')
    if not db_path.startswith(db_dir) or not db_path.endswith('.db'):
        print(f"db_dir:{db_dir}")
        print(f"db_path:{db_path}")
        print(f"[API ERROR] Invalid database path: {db_path}")
        raise Exception('Invalid database file path.')
    if not os.path.exists(db_path):
        print(f"[API ERROR] Database file does not exist: {db_path}")
        raise Exception('Database file does not exist.')
    return sqlite3.connect(db_path)

def get_table_columns(table):
    conn = get_connection()
    c = conn.cursor()
    c.execute(f'PRAGMA table_info({table})')
    columns = [row[1] for row in c.fetchall()]
    conn.close()
    return columns

@app.route('/')
def index():
    return 'LIMS API is running.'

# CRUD endpoints for samples
@app.route('/samples', methods=['POST'])
@require_api_key
def create_sample():
    data = request.json
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO samples (name, collected_by, collected_at) VALUES (?, ?, ?)',
              (data['name'], data['collected_by'], data['collected_at']))
    conn.commit()
    sample_id = c.lastrowid
    conn.close()
    return jsonify({'sample_id': sample_id}), 201

@app.route('/samples', methods=['GET'])
@require_api_key
def get_samples():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT sample_id, name, collected_by, collected_at FROM samples')
    samples = [dict(zip(['sample_id', 'name', 'collected_by', 'collected_at'], row)) for row in c.fetchall()]
    conn.close()
    return jsonify(samples)

@app.route('/samples/<int:sample_id>', methods=['GET'])
@require_api_key
def get_sample(sample_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT sample_id, name, collected_by, collected_at FROM samples WHERE sample_id = ?', (sample_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify(dict(zip(['sample_id', 'name', 'collected_by', 'collected_at'], row)))
    else:
        return jsonify({'error': 'Sample not found'}), 404

@app.route('/samples/<int:sample_id>', methods=['PUT'])
@require_api_key
def update_sample(sample_id):
    data = request.json
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE samples SET name = ?, collected_by = ?, collected_at = ? WHERE sample_id = ?',
              (data['name'], data['collected_by'], data['collected_at'], sample_id))
    conn.commit()
    updated = c.rowcount
    conn.close()
    if updated:
        return jsonify({'message': 'Sample updated'})
    else:
        return jsonify({'error': 'Sample not found'}), 404

@app.route('/samples/<int:sample_id>', methods=['DELETE'])
@require_api_key
def delete_sample(sample_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM samples WHERE sample_id = ?', (sample_id,))
    conn.commit()
    deleted = c.rowcount
    conn.close()
    if deleted:
        return jsonify({'message': 'Sample deleted'})
    else:
        return jsonify({'error': 'Sample not found'}), 404

# CRUD endpoints for users
@app.route('/users', methods=['POST'])
@require_api_key
def create_user():
    data = request.json
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO users (username, role) VALUES (?, ?)',
              (data['username'], data['role']))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return jsonify({'user_id': user_id}), 201

@app.route('/users', methods=['GET'])
@require_api_key
def get_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT user_id, username, role FROM users')
    users = [dict(zip(['user_id', 'username', 'role'], row)) for row in c.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
@require_api_key
def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT user_id, username, role FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify(dict(zip(['user_id', 'username', 'role'], row)))
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:user_id>', methods=['PUT'])
@require_api_key
def update_user(user_id):
    data = request.json
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET username = ?, role = ? WHERE user_id = ?',
              (data['username'], data['role'], user_id))
    conn.commit()
    updated = c.rowcount
    conn.close()
    if updated:
        return jsonify({'message': 'User updated'})
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:user_id>', methods=['DELETE'])
@require_api_key
def delete_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    deleted = c.rowcount
    conn.close()
    if deleted:
        return jsonify({'message': 'User deleted'})
    else:
        return jsonify({'error': 'User not found'}), 404

# CRUD endpoints for tests
@app.route('/tests', methods=['POST'])
@require_api_key
def create_test():
    data = request.json
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO tests (sample_id, test_type, result, tested_at) VALUES (?, ?, ?, ?)',
              (data['sample_id'], data['test_type'], data['result'], data['tested_at']))
    conn.commit()
    test_id = c.lastrowid
    conn.close()
    return jsonify({'test_id': test_id}), 201

@app.route('/tests', methods=['GET'])
@require_api_key
def get_tests():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT test_id, sample_id, test_type, result, tested_at FROM tests')
    tests = [dict(zip(['test_id', 'sample_id', 'test_type', 'result', 'tested_at'], row)) for row in c.fetchall()]
    conn.close()
    return jsonify(tests)

@app.route('/tests/<int:test_id>', methods=['GET'])
@require_api_key
def get_test(test_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT test_id, sample_id, test_type, result, tested_at FROM tests WHERE test_id = ?', (test_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify(dict(zip(['test_id', 'sample_id', 'test_type', 'result', 'tested_at'], row)))
    else:
        return jsonify({'error': 'Test not found'}), 404

@app.route('/tests/<int:test_id>', methods=['PUT'])
@require_api_key
def update_test(test_id):
    data = request.json
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE tests SET sample_id = ?, test_type = ?, result = ?, tested_at = ? WHERE test_id = ?',
              (data['sample_id'], data['test_type'], data['result'], data['tested_at'], test_id))
    conn.commit()
    updated = c.rowcount
    conn.close()
    if updated:
        return jsonify({'message': 'Test updated'})
    else:
        return jsonify({'error': 'Test not found'}), 404

@app.route('/tests/<int:test_id>', methods=['DELETE'])
@require_api_key
def delete_test(test_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM tests WHERE test_id = ?', (test_id,))
    conn.commit()
    deleted = c.rowcount
    conn.close()
    if deleted:
        return jsonify({'message': 'Test deleted'})
    else:
        return jsonify({'error': 'Test not found'}), 404

# Generic CRUD API endpoints
@app.route('/api/<table>', methods=['GET'])
@require_api_key
def api_list(table):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute(f'SELECT * FROM {table}')
        rows = c.fetchall()
        data = [dict(row) for row in rows]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/<table>/<int:row_id>', methods=['GET'])
@require_api_key
def api_get(table, row_id):
    pk = get_table_columns(table)[0]
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute(f'SELECT * FROM {table} WHERE {pk} = ?', (row_id,))
        row = c.fetchone()
        if row:
            return jsonify(dict(row))
        else:
            return jsonify({'error': f'{table} entry not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/<table>', methods=['POST'])
@require_api_key
def api_create(table):
    data = request.json
    columns = get_table_columns(table)
    fields = [k for k in data.keys() if k in columns and k != columns[0]]
    values = [data[k] for k in fields]
    placeholders = ','.join(['?'] * len(fields))
    sql = f'INSERT INTO {table} ({", ".join(fields)}) VALUES ({placeholders})'
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(sql, values)
        conn.commit()
        return jsonify({columns[0]: c.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/<table>/<int:row_id>', methods=['PUT'])
@require_api_key
def api_update(table, row_id):
    data = request.json
    columns = get_table_columns(table)
    pk = columns[0]
    fields = [k for k in data.keys() if k in columns and k != pk]
    values = [data[k] for k in fields]
    set_clause = ', '.join([f'{k} = ?' for k in fields])
    sql = f'UPDATE {table} SET {set_clause} WHERE {pk} = ?'
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(sql, values + [row_id])
        conn.commit()
        if c.rowcount:
            return jsonify({'message': f'{table} entry updated'})
        else:
            return jsonify({'error': f'{table} entry not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/<table>/<int:row_id>', methods=['DELETE'])
@require_api_key
def api_delete(table, row_id):
    pk = get_table_columns(table)[0]
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(f'DELETE FROM {table} WHERE {pk} = ?', (row_id,))
        conn.commit()
        if c.rowcount:
            return jsonify({'message': f'{table} entry deleted'})
        else:
            return jsonify({'error': f'{table} entry not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/schema', methods=['GET'])
@require_api_key
def api_schema():
    db_path = request.headers.get('X-DB-PATH')
    if not db_path:
        db_path = os.path.abspath('databases/lims.db')
    tables = list_tables(db_path)
    schema = {}
    for table in tables:
        columns = get_table_schema(db_path, table)
        schema[table] = [
            {
                'cid': col[0],
                'name': col[1],
                'type': col[2],
                'notnull': col[3],
                'default': col[4],
                'pk': col[5]
            } for col in columns
        ]
    return jsonify(schema)

if __name__ == '__main__':
    app.run(debug=True)
