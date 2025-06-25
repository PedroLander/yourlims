import pytest
from yourlims.frontend.app import app as frontend_app
import requests
from flask import url_for, session
import os

API_KEY = 'your-secret-api-key'
TEST_DB = 'test_lims.db'
DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../databases'))

@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    # Create a test db if it doesn't exist
    test_db_path = os.path.join(DB_DIR, TEST_DB)
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    import sqlite3, json
    schema_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database/international.json'))
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
    yield
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.fixture
def client(setup_test_db):
    frontend_app.config['TESTING'] = True
    with frontend_app.test_client() as client:
        with client.session_transaction() as sess:
            sess['db_path'] = TEST_DB
        yield client

def test_index_page(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Laboratory Information Management System' in resp.data

def test_table_dynamic_rendering(client, monkeypatch):
    # Mock requests.get to return fake API data for a generic table
    class MockResponse:
        def __init__(self, json_data, status_code):
            self._json = json_data
            self.status_code = status_code
        def json(self):
            return self._json
    # Simulate a table called 'samples' with dynamic columns
    monkeypatch.setattr(requests, 'get', lambda url, headers=None: MockResponse([
        {'sample_id': 1, 'name': 'SampleX', 'collected_by': 'alice', 'collected_at': '2025-06-01'}
    ], 200) if '/api/samples' in url else MockResponse({}, 200))
    resp = client.get('/samples')
    assert resp.status_code == 200
    assert b'SampleX' in resp.data
    assert b'alice' in resp.data
    # Simulate a table called 'users' with dynamic columns
    monkeypatch.setattr(requests, 'get', lambda url, headers=None: MockResponse([
        {'user_id': 1, 'username': 'bob', 'role': 'admin'}
    ], 200) if '/api/users' in url else MockResponse({}, 200))
    resp = client.get('/users')
    assert resp.status_code == 200
    assert b'bob' in resp.data
    assert b'admin' in resp.data
    # Simulate a table called 'tests' with dynamic columns
    monkeypatch.setattr(requests, 'get', lambda url, headers=None: MockResponse([
        {'test_id': 1, 'sample_id': 1, 'test_type': 'PCR', 'result': 'Positive', 'tested_at': '2025-06-11'}
    ], 200) if '/api/tests' in url else MockResponse({}, 200))
    resp = client.get('/tests')
    assert resp.status_code == 200
    assert b'PCR' in resp.data
    assert b'Positive' in resp.data
    # Test a non-existent table
    monkeypatch.setattr(requests, 'get', lambda url, headers=None: MockResponse([], 200))
    resp = client.get('/nonexistent')
    assert resp.status_code == 200
    assert b'No records found' in resp.data
