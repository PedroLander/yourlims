# YourLIMS

A minimal Laboratory Information Management System (LIMS) built with Python, Flask, and SQLite.

## Project Structure

- `yourlims/models/` — Data models for samples, users, and tests
- `yourlims/database/` — Database connection and initialization
- `yourlims/api/` — Flask API endpoints
- `yourlims/tests/` — Test scaffolding
- `yourlims/frontend/` — Web frontend

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the API:
   ```bash
   python yourlims/api/app.py
   ```
3. Visit [http://localhost:5000](http://localhost:5000)

## Web Frontend

A simple web frontend is available in `yourlims/frontend/`.

To run the frontend (after starting the API backend):
```bash
pip install -r requirements.txt
python yourlims/frontend/app.py
```
Then visit [http://localhost:5001](http://localhost:5001) in your browser.

## Database Initialization/Reset

To initialize or reset the database, run:
```bash
python scripts/init_db.py
```
This will delete any existing `lims.db` file and create a fresh database schema.

## Load Example Data

To populate the database with example users, samples, and tests for a molecular biology lab, run:
```bash
python scripts/load_example_data.py
```

## Next Steps
- Implement CRUD endpoints for samples, users, and tests
- Add authentication and authorization
- Build a frontend (optional)
- Write more tests
