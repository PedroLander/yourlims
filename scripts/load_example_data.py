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
        c.executemany("INSERT INTO users (username, role, email, created_at) VALUES (?, ?, ?, ?)", [
            ('alice', 'admin', 'alice@lab.com', '2025-06-01'),
            ('bob', 'scientist', 'bob@lab.com', '2025-06-02'),
            ('carol', 'technician', 'carol@lab.com', '2025-06-03'),
            ('dave', 'scientist', 'dave@lab.com', '2025-06-04'),
            ('eve', 'admin', 'eve@lab.com', '2025-06-05')
        ])
        c.executemany("INSERT INTO equipment (name, model, serial_number, location, status, last_maintenance) VALUES (?, ?, ?, ?, ?, ?)", [
            ('Centrifuge', 'Eppendorf 5424', 'SN12345', 'Lab A', 'active', '2025-05-01'),
            ('PCR Machine', 'BioRad T100', 'SN54321', 'Lab B', 'maintenance', '2025-04-15'),
            ('Spectrophotometer', 'NanoDrop 2000', 'SN67890', 'Lab C', 'active', '2025-03-20')
        ])
        c.executemany("INSERT INTO storage (name, location, temperature) VALUES (?, ?, ?)", [
            ('Freezer 1', 'Room 101', '-20C'),
            ('Refrigerator', 'Room 102', '4C'),
            ('Liquid Nitrogen Tank', 'Room 103', '-196C')
        ])
        c.executemany("INSERT INTO inventory (name, product_type, lot_number, quantity, unit, expiration_date, storage_id) VALUES (?, ?, ?, ?, ?, ?, ?)", [
            ('Buffer', 'reagent', 'LOT42', 10, 'L', '2025-12-31', 1),
            ('Enzyme Mix', 'enzyme', 'LOT99', 5, 'ml', '2026-01-15', 2),
            ('Agarose', 'gel', 'LOT77', 2, 'kg', '2027-05-10', 1)
        ])
        c.executemany("INSERT INTO samples (name, sample_type, collected_by, collected_at, storage_id, description) VALUES (?, ?, ?, ?, ?, ?)", [
            ('Blood sample A', 'blood', 'alice', '2025-06-01', 1, 'Routine check'),
            ('DNA extract B', 'dna', 'bob', '2025-06-02', 2, 'PCR prep'),
            ('Tissue sample C', 'tissue', 'carol', '2025-06-03', 3, 'Biopsy'),
            ('Serum D', 'serum', 'dave', '2025-06-04', 1, 'Serology'),
            ('Plasma E', 'plasma', 'eve', '2025-06-05', 2, 'Clinical trial')
        ])
        c.executemany("INSERT INTO dna (sample_id, concentration, unit, organism, extraction_method) VALUES (?, ?, ?, ?, ?)", [
            (1, 50.0, 'ng/ul', 'Homo sapiens', 'phenol-chloroform'),
            (2, 30.5, 'ng/ul', 'Mus musculus', 'kit'),
            (3, 80.2, 'ng/ul', 'Homo sapiens', 'phenol-chloroform')
        ])
        c.executemany("INSERT INTO tissues (sample_id, tissue_type, organism, preservation_method) VALUES (?, ?, ?, ?)", [
            (3, 'liver', 'Homo sapiens', 'frozen'),
            (4, 'kidney', 'Mus musculus', 'formalin'),
            (5, 'heart', 'Homo sapiens', 'frozen')
        ])
        c.executemany("INSERT INTO antibodies (name, host_species, target, clonality, lot_number, storage_id) VALUES (?, ?, ?, ?, ?, ?)", [
            ('Anti-GAPDH', 'rabbit', 'GAPDH', 'monoclonal', 'AB123', 1),
            ('Anti-Actin', 'mouse', 'Actin', 'polyclonal', 'AB456', 2),
            ('Anti-Tubulin', 'goat', 'Tubulin', 'monoclonal', 'AB789', 3)
        ])
        c.executemany("INSERT INTO tests (sample_id, test_type, result, tested_at, performed_by, equipment_id) VALUES (?, ?, ?, ?, ?, ?)", [
            (1, 'PCR', 'Positive', '2025-06-04', 'bob', 1),
            (2, 'Sequencing', 'Clean', '2025-06-05', 'alice', 2),
            (3, 'Histology', 'Normal', '2025-06-06', 'carol', 3),
            (4, 'ELISA', 'Negative', '2025-06-07', 'dave', 1),
            (5, 'Western Blot', 'Positive', '2025-06-08', 'eve', 2)
        ])
    except Exception as e:
        print('Warning: Example data insert failed:', e)
    conn.commit()
    conn.close()
    print(f'Example database created at {db_path}')

if __name__ == '__main__':
    create_example_db()
