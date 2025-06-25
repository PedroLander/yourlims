import os
import sqlite3
import json
import sys

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../databases'))
os.makedirs(DB_DIR, exist_ok=True)

# Helper to load a schema file
SCHEMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../yourlims/database'))
ALL_SCHEMA_FILES = [
    'international.json',
    'experimental_metadata.json',
    'domain_metadata.json',
    'biosample_metadata.json',
    'chemicals_inventory.json',
    'logistics_inventory.json',
    'instrument_data.json',
    'staff_competency.json',
    'automation_integration.json',
    'quality_compliance.json',
    'results_representation.json',
    'data_interchange.json'
]

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

def populate_example_data(conn):
    c = conn.cursor()
    try:
        # Users
        c.executemany("INSERT INTO users (username, role, email, created_at) VALUES (?, ?, ?, ?)", [
            ('alice', 'admin', 'alice@lab.com', '2025-06-01'),
            ('bob', 'scientist', 'bob@lab.com', '2025-06-02'),
            ('carol', 'technician', 'carol@lab.com', '2025-06-03'),
            ('dave', 'scientist', 'dave@lab.com', '2025-06-04'),
            ('eve', 'admin', 'eve@lab.com', '2025-06-05')
        ])
        # Equipment
        c.executemany("INSERT INTO equipment (name, model, serial_number, location, status, last_maintenance) VALUES (?, ?, ?, ?, ?, ?)", [
            ('Centrifuge', 'Eppendorf 5424', 'SN12345', 'Lab A', 'active', '2025-05-01'),
            ('PCR Machine', 'BioRad T100', 'SN54321', 'Lab B', 'maintenance', '2025-04-15'),
            ('Spectrophotometer', 'NanoDrop 2000', 'SN67890', 'Lab C', 'active', '2025-03-20')
        ])
        # Storage
        c.executemany("INSERT INTO storage (name, location, temperature) VALUES (?, ?, ?)", [
            ('Freezer 1', 'Room 101', '-20C'),
            ('Refrigerator', 'Room 102', '4C'),
            ('Liquid Nitrogen Tank', 'Room 103', '-196C')
        ])
        # Inventory
        c.executemany("INSERT INTO inventory (name, product_type, lot_number, quantity, unit, expiration_date, storage_id) VALUES (?, ?, ?, ?, ?, ?, ?)", [
            ('Buffer', 'reagent', 'LOT42', 10, 'L', '2025-12-31', 1),
            ('Enzyme Mix', 'enzyme', 'LOT99', 5, 'ml', '2026-01-15', 2),
            ('Agarose', 'gel', 'LOT77', 2, 'kg', '2027-05-10', 1)
        ])
        # Samples
        c.executemany("INSERT INTO samples (name, sample_type, collected_by, collected_at, storage_id, description) VALUES (?, ?, ?, ?, ?, ?)", [
            ('Blood sample A', 'blood', 'alice', '2025-06-01', 1, 'Routine check'),
            ('DNA extract B', 'dna', 'bob', '2025-06-02', 2, 'PCR prep'),
            ('Tissue sample C', 'tissue', 'carol', '2025-06-03', 3, 'Biopsy'),
            ('Serum D', 'serum', 'dave', '2025-06-04', 1, 'Serology'),
            ('Plasma E', 'plasma', 'eve', '2025-06-05', 2, 'Clinical trial')
        ])
        # DNA
        c.executemany("INSERT INTO dna (sample_id, concentration, unit, organism, extraction_method) VALUES (?, ?, ?, ?, ?)", [
            (1, 50.0, 'ng/ul', 'Homo sapiens', 'phenol-chloroform'),
            (2, 30.5, 'ng/ul', 'Mus musculus', 'kit'),
            (3, 80.2, 'ng/ul', 'Homo sapiens', 'phenol-chloroform')
        ])
        # Tissues
        c.executemany("INSERT INTO tissues (sample_id, tissue_type, organism, preservation_method) VALUES (?, ?, ?, ?)", [
            (3, 'liver', 'Homo sapiens', 'frozen'),
            (4, 'kidney', 'Mus musculus', 'formalin'),
            (5, 'heart', 'Homo sapiens', 'frozen')
        ])
        # Antibodies
        c.executemany("INSERT INTO antibodies (name, host_species, target, clonality, lot_number, storage_id) VALUES (?, ?, ?, ?, ?, ?)", [
            ('Anti-GAPDH', 'rabbit', 'GAPDH', 'monoclonal', 'AB123', 1),
            ('Anti-Actin', 'mouse', 'Actin', 'polyclonal', 'AB456', 2),
            ('Anti-Tubulin', 'goat', 'Tubulin', 'monoclonal', 'AB789', 3)
        ])
        # Tests
        c.executemany("INSERT INTO tests (sample_id, test_type, result, tested_at, performed_by, equipment_id) VALUES (?, ?, ?, ?, ?, ?)", [
            (1, 'PCR', 'Positive', '2025-06-04', 'bob', 1),
            (2, 'Sequencing', 'Clean', '2025-06-05', 'alice', 2),
            (3, 'Histology', 'Normal', '2025-06-06', 'carol', 3),
            (4, 'ELISA', 'Negative', '2025-06-07', 'dave', 1),
            (5, 'Western Blot', 'Positive', '2025-06-08', 'eve', 2)
        ])
        # Staff
        c.executemany("INSERT INTO staff (name, role, training, edu_term) VALUES (?, ?, ?, ?)", [
            ('Frank', 'PI', 'Lab Safety', 'EDU:0001'),
            ('Grace', 'Lab Tech', 'PCR', 'EDU:0002'),
            ('Heidi', 'Postdoc', 'Sequencing', 'EDU:0003')
        ])
        # Chemicals
        c.executemany("INSERT INTO chemicals (name, chebi_id, pubchem_id, unii, unit, quantity, expiration_date) VALUES (?, ?, ?, ?, ?, ?, ?)", [
            ('Tris', 'CHEBI:9754', '31354', 'UNII-8U8Z', 'g', 100, '2026-01-01'),
            ('EDTA', 'CHEBI:42191', '6049', 'UNII-9G34', 'g', 50, '2026-06-01'),
            ('NaCl', 'CHEBI:26710', '5234', 'UNII-9G1', 'g', 200, '2027-01-01')
        ])
        # Containers
        c.executemany("INSERT INTO containers (type, location, gs1_code) VALUES (?, ?, ?)", [
            ('Box', 'Shelf 1', 'GS1-001'),
            ('Tube', 'Shelf 2', 'GS1-002'),
            ('Plate', 'Shelf 3', 'GS1-003')
        ])
        # Sequencing Runs
        c.executemany("INSERT INTO sequencing_runs (platform, protocol, mixs_standard) VALUES (?, ?, ?)", [
            ('Illumina', '16S', 'MIxS:0001'),
            ('PacBio', 'Shotgun', 'MIxS:0002'),
            ('Nanopore', 'WGS', 'MIxS:0003')
        ])
        # Omics Data
        c.executemany("INSERT INTO omics_data (run_id, type, mimarks, miame) VALUES (?, ?, ?, ?)", [
            (1, 'metagenomics', 'MIMARKS:1', 'MIAME:1'),
            (2, 'transcriptomics', 'MIMARKS:2', 'MIAME:2'),
            (3, 'proteomics', 'MIMARKS:3', 'MIAME:3')
        ])
        # Specimens
        c.executemany("INSERT INTO specimens (taxon, dwc_term, envo_term, field_location) VALUES (?, ?, ?, ?)", [
            ('Homo sapiens', 'dwc:0001', 'ENVO:0001', 'Field A'),
            ('Mus musculus', 'dwc:0002', 'ENVO:0002', 'Field B'),
            ('Arabidopsis thaliana', 'dwc:0003', 'ENVO:0003', 'Field C')
        ])
        # Automation
        c.executemany("INSERT INTO automation (type, driver, sop_id) VALUES (?, ?, ?)", [
            ('robot', 'SiLA2', '1'),
            ('liquid handler', 'OPC-UA', '2'),
            ('incubator', 'Custom', '3')
        ])
        # Instruments
        c.executemany("INSERT INTO instruments (name, model, serial_number, calibration_date, animl_id) VALUES (?, ?, ?, ?, ?)", [
            ('HPLC', 'Agilent 1100', 'HPLC-001', '2025-01-01', 'ANIML:001'),
            ('GC-MS', 'Shimadzu QP2010', 'GCMS-002', '2025-02-01', 'ANIML:002'),
            ('Plate Reader', 'BioTek Synergy', 'PLATE-003', '2025-03-01', 'ANIML:003')
        ])
        # Calibrations
        c.executemany("INSERT INTO calibrations (instrument_id, date, adf_id) VALUES (?, ?, ?)", [
            (1, '2025-01-10', 'ADF:001'),
            (2, '2025-02-10', 'ADF:002'),
            (3, '2025-03-10', 'ADF:003')
        ])
        # SOPS
        c.executemany("INSERT INTO sops (title, version, iso_standard, revision_date) VALUES (?, ?, ?, ?)", [
            ('DNA Extraction', '1.0', 'ISO17025', '2025-01-01'),
            ('PCR Protocol', '2.0', 'ISO15189', '2025-02-01'),
            ('Sample Storage', '1.1', 'ISO17025', '2025-03-01')
        ])
        # Audit Trails
        c.executemany("INSERT INTO audit_trails (sop_id, event, timestamp) VALUES (?, ?, ?)", [
            (1, 'created', '2025-01-01T10:00:00'),
            (2, 'revised', '2025-02-01T11:00:00'),
            (3, 'reviewed', '2025-03-01T12:00:00')
        ])
        # Results
        c.executemany("INSERT INTO results (type, value, unit, statistic, stato_term) VALUES (?, ?, ?, ?, ?)", [
            ('concentration', '5.2', 'ng/ul', 'mean', 'STATO:0001'),
            ('purity', '1.8', 'A260/A280', 'median', 'STATO:0002'),
            ('yield', '100', 'ug', 'sum', 'STATO:0003')
        ])
        # Interchange
        c.executemany("INSERT INTO interchange (jsonld, rdf, ro_crate, dublin_core) VALUES (?, ?, ?, ?)", [
            ('{"@context": "..."}', '<rdf>...</rdf>', '{"@graph":[]}', '{"title":"Example"}'),
            ('{"@context": "...2"}', '<rdf>...2</rdf>', '{"@graph":[1]}', '{"title":"Example2"}'),
            ('{"@context": "...3"}', '<rdf>...3</rdf>', '{"@graph":[2]}', '{"title":"Example3"}')
        ])
        # Studies
        c.executemany("INSERT INTO studies (title, description, start_date, end_date, isa_investigation) VALUES (?, ?, ?, ?, ?)", [
            ('Cancer Study', 'Study on cancer markers', '2025-01-01', '2025-06-01', 'INV:001'),
            ('Plant Growth', 'Arabidopsis growth', '2025-02-01', '2025-07-01', 'INV:002'),
            ('Microbiome', 'Gut microbiome', '2025-03-01', '2025-08-01', 'INV:003')
        ])
        # Assays
        c.executemany("INSERT INTO assays (study_id, type, platform, obi_term) VALUES (?, ?, ?, ?)", [
            (1, 'ELISA', 'BioTek', 'OBI:0001'),
            (2, 'qPCR', 'BioRad', 'OBI:0002'),
            (3, 'Metagenomics', 'Illumina', 'OBI:0003')
        ])
        # Conditions
        c.executemany("INSERT INTO conditions (assay_id, factor, value) VALUES (?, ?, ?)", [
            (1, 'temperature', '37C'),
            (2, 'pH', '7.4'),
            (3, 'salinity', '0.9%')
        ])
    except Exception as e:
        print('Warning: Example data insert failed:', e)
    conn.commit()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Populate a LIMS database with example data')
    parser.add_argument('db_path', help='Path to the database file to populate (in yourlims/databases)')
    args = parser.parse_args()
    db_path = args.db_path
    if not os.path.isabs(db_path):
        db_path = os.path.join(DB_DIR, db_path)
    if not os.path.exists(db_path):
        # Create the database with all schemas if it does not exist
        import subprocess
        schema_arg = ','.join(ALL_SCHEMA_FILES)
        subprocess.run(['python', os.path.join(os.path.dirname(__file__), 'init_db.py'), '--db', os.path.basename(db_path), '--schemas', schema_arg], check=True)
    conn = sqlite3.connect(db_path)
    populate_example_data(conn)
    conn.close()
    print(f'Example data loaded into {db_path}')
