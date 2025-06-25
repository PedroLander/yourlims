import sqlite3
import os

def get_table_schema(db_path, table_name):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f'PRAGMA table_info({table_name})')
    columns = c.fetchall()
    conn.close()
    return columns

def list_tables(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    conn.close()
    return tables
