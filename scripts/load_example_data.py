import os
import sqlite3
import json

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../databases'))
SCHEMA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../yourlims/database/international.json'))
EXAMPLE_DB = 'example_lims.db'

os.makedirs(DB_DIR, exist_ok=True)

def load_schema():
    with open(SCHEMA_FILE) as f:
        schema = json.load(f)
    return schema

def create_example_db():
    db_path = os.path.join(DB_DIR, EXAMPLE_DB)
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    schema = load_schema()
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
    # Populate all tables with at least one example row if possible
    try:
        c.execute("INSERT INTO users (username, role, email, created_at) VALUES (?, ?, ?, ?)",
                  ('alice', 'admin', 'alice@lab.com', '2025-06-01'))
        c.execute("INSERT INTO equipment (name, model, serial_number, location, status, last_maintenance) VALUES (?, ?, ?, ?, ?, ?)",
                  ('Centrifuge', 'Eppendorf 5424', 'SN12345', 'Lab A', 'active', '2025-05-01'))
        c.execute("INSERT INTO storage (name, location, temperature) VALUES (?, ?, ?)",
                  ('Freezer 1', 'Room 101', '-20C'))
        c.execute("INSERT INTO inventory (name, product_type, lot_number, quantity, unit, expiration_date, storage_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ('Buffer', 'reagent', 'LOT42', 10, 'L', '2025-12-31', 1))
        c.execute("INSERT INTO samples (name, sample_type, collected_by, collected_at, storage_id, description) VALUES (?, ?, ?, ?, ?, ?)",
                  ('Blood sample A', 'blood', 'alice', '2025-06-01', 1, 'Routine check'))
        c.execute("INSERT INTO dna (sample_id, concentration, unit, organism, extraction_method) VALUES (?, ?, ?, ?, ?)",
                  (1, 50.0, 'ng/ul', 'Homo sapiens', 'phenol-chloroform'))
        c.execute("INSERT INTO tissues (sample_id, tissue_type, organism, preservation_method) VALUES (?, ?, ?, ?)",
                  (1, 'liver', 'Homo sapiens', 'frozen'))
        c.execute("INSERT INTO antibodies (name, host_species, target, clonality, lot_number, storage_id) VALUES (?, ?, ?, ?, ?, ?)",
                  ('Anti-GAPDH', 'rabbit', 'GAPDH', 'monoclonal', 'AB123', 1))
        c.execute("INSERT INTO tests (sample_id, test_type, result, tested_at, performed_by, equipment_id) VALUES (?, ?, ?, ?, ?, ?)",
                  (1, 'PCR', 'Positive', '2025-06-04', 'bob', 1))
    except Exception as e:
        print('Warning: Example data insert failed:', e)
    conn.commit()
    conn.close()
    print(f'Example database created at {db_path}')

if __name__ == '__main__':
    create_example_db()
