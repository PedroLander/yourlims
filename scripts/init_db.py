import os
import sqlite3
import json

DB_DIR = os.path.join(os.path.dirname(__file__), '../databases')
os.makedirs(DB_DIR, exist_ok=True)
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), '../yourlims/database')

def load_schema_file(schema_file):
    schema_path = os.path.join(SCHEMA_DIR, schema_file)
    with open(schema_path) as f:
        return json.load(f)

def merge_schemas(schema_files):
    tables = []
    seen = set()
    for schema_file in schema_files:
        schema = load_schema_file(schema_file)
        for table in schema:
            if table['name'] not in seen:
                tables.append(table)
                seen.add(table['name'])
    return tables

def init_db(db_name='lims.db', schema_files=None, schema_name=None):
    db_path = os.path.join(DB_DIR, db_name)
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if schema_files:
        tables = merge_schemas(schema_files)
    elif schema_name:
        # fallback for old usage
        schema = load_schema_file(f'{schema_name}.json')
        tables = schema
    else:
        raise ValueError('No schema(s) provided')
    for table in tables:
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
        # Auto-populate accounting table with demo data on creation
        if table['name'] == 'accounting':
            c.executemany("INSERT INTO accounting (year, budget, spent, balance, last_update) VALUES (?, ?, ?, ?, ?)", [
                (2023, 100000, 80000, 20000, '2023-12-31'),
                (2024, 120000, 95000, 25000, '2024-12-31'),
                (2025, 130000, 110000, 20000, '2025-06-26')
            ])
    conn.commit()
    conn.close()
    print(f'LIMS database initialized at {db_path} with {len(tables)} tables.')

def list_databases():
    return [f for f in os.listdir(DB_DIR) if f.endswith('.db')]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Initialize/select LIMS database')
    parser.add_argument('--db', default='lims.db', help='Database file name')
    parser.add_argument('--schema', default=None, help='Schema name (legacy, single schema)')
    parser.add_argument('--schemas', default=None, help='Comma-separated list of schema JSON files')
    args = parser.parse_args()
    if args.schemas:
        schema_files = [s.strip() for s in args.schemas.split(',') if s.strip()]
        init_db(args.db, schema_files=schema_files)
    else:
        init_db(args.db, schema_name=args.schema)
    print('Available databases:', list_databases())
