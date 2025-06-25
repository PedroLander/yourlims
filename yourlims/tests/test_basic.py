import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from yourlims.api.app import app, API_KEY

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def auth_headers():
    return {'X-API-KEY': API_KEY}

def test_index(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'LIMS API is running.' in resp.data

def test_auth_required(client):
    resp = client.get('/samples')
    assert resp.status_code == 401

def test_sample_crud(client):
    # Create
    data = {'name': 'Sample1', 'collected_by': 'User1', 'collected_at': '2025-06-25'}
    resp = client.post('/samples', json=data, headers=auth_headers())
    assert resp.status_code == 201
    sample_id = resp.get_json()['sample_id']
    # Read all
    resp = client.get('/samples', headers=auth_headers())
    assert resp.status_code == 200
    # Read one
    resp = client.get(f'/samples/{sample_id}', headers=auth_headers())
    assert resp.status_code == 200
    # Update
    data['name'] = 'Sample1-updated'
    resp = client.put(f'/samples/{sample_id}', json=data, headers=auth_headers())
    assert resp.status_code == 200
    # Delete
    resp = client.delete(f'/samples/{sample_id}', headers=auth_headers())
    assert resp.status_code == 200

def test_user_crud(client):
    data = {'username': 'testuser', 'role': 'admin'}
    resp = client.post('/users', json=data, headers=auth_headers())
    assert resp.status_code == 201
    user_id = resp.get_json()['user_id']
    resp = client.get('/users', headers=auth_headers())
    assert resp.status_code == 200
    resp = client.get(f'/users/{user_id}', headers=auth_headers())
    assert resp.status_code == 200
    data['role'] = 'user'
    resp = client.put(f'/users/{user_id}', json=data, headers=auth_headers())
    assert resp.status_code == 200
    resp = client.delete(f'/users/{user_id}', headers=auth_headers())
    assert resp.status_code == 200

def test_test_crud(client):
    # Need a sample first
    sample_data = {'name': 'Sample2', 'collected_by': 'User2', 'collected_at': '2025-06-25'}
    resp = client.post('/samples', json=sample_data, headers=auth_headers())
    sample_id = resp.get_json()['sample_id']
    data = {'sample_id': sample_id, 'test_type': 'PCR', 'result': 'Positive', 'tested_at': '2025-06-25'}
    resp = client.post('/tests', json=data, headers=auth_headers())
    assert resp.status_code == 201
    test_id = resp.get_json()['test_id']
    resp = client.get('/tests', headers=auth_headers())
    assert resp.status_code == 200
    resp = client.get(f'/tests/{test_id}', headers=auth_headers())
    assert resp.status_code == 200
    data['result'] = 'Negative'
    resp = client.put(f'/tests/{test_id}', json=data, headers=auth_headers())
    assert resp.status_code == 200
    resp = client.delete(f'/tests/{test_id}', headers=auth_headers())
    assert resp.status_code == 200
    # Clean up sample
    client.delete(f'/samples/{sample_id}', headers=auth_headers())
