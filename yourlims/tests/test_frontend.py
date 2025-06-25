import pytest
from yourlims.frontend.app import app as frontend_app
import requests
from flask import url_for

API_KEY = 'your-secret-api-key'

@pytest.fixture
def client():
    frontend_app.config['TESTING'] = True
    with frontend_app.test_client() as client:
        yield client

def test_index_page(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Laboratory Information Management System' in resp.data

def test_samples_page(client, monkeypatch):
    # Mock requests.get to return fake API data
    class MockResponse:
        def __init__(self, json_data, status_code):
            self._json = json_data
            self.status_code = status_code
        def json(self):
            return self._json
    monkeypatch.setattr(requests, 'get', lambda url, headers=None: MockResponse([
        {'sample_id': 1, 'name': 'SampleX', 'collected_by': 'alice', 'collected_at': '2025-06-01'}
    ], 200))
    resp = client.get('/samples')
    assert resp.status_code == 200
    assert b'SampleX' in resp.data
    assert b'alice' in resp.data

def test_users_page(client, monkeypatch):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self._json = json_data
            self.status_code = status_code
        def json(self):
            return self._json
    monkeypatch.setattr(requests, 'get', lambda url, headers=None: MockResponse([
        {'user_id': 1, 'username': 'bob', 'role': 'admin'}
    ], 200))
    resp = client.get('/users')
    assert resp.status_code == 200
    assert b'bob' in resp.data
    assert b'admin' in resp.data

def test_tests_page(client, monkeypatch):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self._json = json_data
            self.status_code = status_code
        def json(self):
            return self._json
    monkeypatch.setattr(requests, 'get', lambda url, headers=None: MockResponse([
        {'test_id': 1, 'sample_id': 1, 'test_type': 'PCR', 'result': 'Positive', 'tested_at': '2025-06-11'}
    ], 200))
    resp = client.get('/tests')
    assert resp.status_code == 200
    assert b'PCR' in resp.data
    assert b'Positive' in resp.data
