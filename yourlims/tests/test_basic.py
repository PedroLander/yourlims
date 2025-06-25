import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from yourlims.api.app import app, API_KEY

def setup_test_db():
    # Create a temp db in the correct directory
    test_db_dir = os.path.join(os.path.dirname(__file__), '../../databases')
    os.makedirs(test_db_dir, exist_ok=True)
    test_db_path = os.path.abspath(os.path.join(test_db_dir, 'test_lims.db'))
    # Use the schema from international.json
    import sqlite3, json
    schema_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database/international.json'))
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    with open(schema_file) as f:
        schema = json.load(f)
    conn = sqlite3.connect(test_db_path)
    c = conn.cursor()
    for table in schema:
        cols = []
        fks = []
        for col in table['columns']:
            coldef = f"{col['name']} {col['type']}"
            cols.append(coldef)
            if 'foreign' in col:
                ref = col['foreign']
                fks.append(f"FOREIGN KEY({col['name']}) REFERENCES {ref}")
        stmt = f"CREATE TABLE {table['name']} (" + ', '.join(cols + fks) + ")"
        c.execute(stmt)
    conn.commit()
    conn.close()
    return test_db_path

@pytest.fixture(scope='session')
def test_db():
    path = setup_test_db()
    yield path
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def client(test_db):
    app.config['TESTING'] = True
    with app.test_client() as client:
        client.environ_base['HTTP_X_DB_PATH'] = test_db
        yield client

def auth_headers(test_db):
    return {'X-API-KEY': API_KEY, 'X-DB-PATH': test_db}

def test_index(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'LIMS API is running.' in resp.data

def test_auth_required(client):
    resp = client.get('/samples')
    assert resp.status_code == 401

def test_sample_crud(client, test_db):
    data = {'name': 'Sample1', 'collected_by': 'User1', 'collected_at': '2025-06-25'}
    resp = client.post('/samples', json=data, headers=auth_headers(test_db))
    assert resp.status_code == 201
    sample_id = resp.get_json()['sample_id']
    resp = client.get('/samples', headers=auth_headers(test_db))
    assert resp.status_code == 200
    resp = client.get(f'/samples/{sample_id}', headers=auth_headers(test_db))
    assert resp.status_code == 200
    data['name'] = 'Sample1-updated'
    resp = client.put(f'/samples/{sample_id}', json=data, headers=auth_headers(test_db))
    assert resp.status_code == 200
    resp = client.delete(f'/samples/{sample_id}', headers=auth_headers(test_db))
    assert resp.status_code == 200

def test_user_crud(client, test_db):
    data = {'username': 'testuser', 'role': 'admin'}
    resp = client.post('/users', json=data, headers=auth_headers(test_db))
    assert resp.status_code == 201
    user_id = resp.get_json()['user_id']
    resp = client.get('/users', headers=auth_headers(test_db))
    assert resp.status_code == 200
    resp = client.get(f'/users/{user_id}', headers=auth_headers(test_db))
    assert resp.status_code == 200
    data['role'] = 'user'
    resp = client.put(f'/users/{user_id}', json=data, headers=auth_headers(test_db))
    assert resp.status_code == 200
    resp = client.delete(f'/users/{user_id}', headers=auth_headers(test_db))
    assert resp.status_code == 200

def test_test_crud(client, test_db):
    # Need a sample first
    sample_data = {'name': 'Sample2', 'collected_by': 'User2', 'collected_at': '2025-06-25'}
    resp = client.post('/samples', json=sample_data, headers=auth_headers(test_db))
    assert resp.status_code == 201
    sample_id = resp.get_json()['sample_id']
    data = {'sample_id': sample_id, 'test_type': 'PCR', 'result': 'Positive', 'tested_at': '2025-06-26'}
    resp = client.post('/tests', json=data, headers=auth_headers(test_db))
    assert resp.status_code == 201
    test_id = resp.get_json()['test_id']
    resp = client.get('/tests', headers=auth_headers(test_db))
    assert resp.status_code == 200
    resp = client.get(f'/tests/{test_id}', headers=auth_headers(test_db))
    assert resp.status_code == 200
    data['result'] = 'Negative'
    resp = client.put(f'/tests/{test_id}', json=data, headers=auth_headers(test_db))
    assert resp.status_code == 200
    resp = client.delete(f'/tests/{test_id}', headers=auth_headers(test_db))
    assert resp.status_code == 200
