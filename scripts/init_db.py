import os
import sqlite3
import json

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), '../yourlims/database/schemas.json')
DB_DIR = os.path.join(os.path.dirname(__file__), '../databases')
os.makedirs(DB_DIR, exist_ok=True)

def load_schema(schema_name='international'):
    with open(SCHEMA_FILE) as f:
        schemas = json.load(f)
    return schemas[schema_name]

def init_db(db_name='lims.db', schema_name='international'):
    db_path = os.path.join(DB_DIR, db_name)
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    schema = load_schema(schema_name)
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
    print(f'{schema_name.capitalize()} LIMS database initialized at {db_path}.')

def list_databases():
    return [f for f in os.listdir(DB_DIR) if f.endswith('.db')]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Initialize/select LIMS database')
    parser.add_argument('--db', default='lims.db', help='Database file name')
    parser.add_argument('--schema', default='international', help='Schema name')
    args = parser.parse_args()
    init_db(args.db, args.schema)
    print('Available databases:', list_databases())
