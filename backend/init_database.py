#!/usr/bin/env python3

import sqlite3
import os

def init_legal_database():
    """Initialize the legal AI database with schema and sample data"""

    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)

    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect('database/legal_data.db')
    cursor = conn.cursor()

    print("Initializing Legal AI Database...")

    # Execute schema
    print("Creating database schema...")
    with open('database/schema.sql', 'r') as schema_file:
        schema_sql = schema_file.read()
        cursor.executescript(schema_sql)

    # Execute seed data
    print("Inserting sample legal data...")
    with open('database/seed_data.sql', 'r') as seed_file:
        seed_sql = seed_file.read()
        cursor.executescript(seed_sql)

    # Commit changes
    conn.commit()

    # Verify data insertion
    cursor.execute("SELECT COUNT(*) FROM case_law")
    case_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM legal_precedents")
    precedent_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM statutes")
    statute_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contracts")
    contract_count = cursor.fetchone()[0]

    print(f"Database initialized successfully!")
    print(f"  - Case law entries: {case_count}")
    print(f"  - Legal precedents: {precedent_count}")
    print(f"  - Statutes: {statute_count}")
    print(f"  - Contract templates: {contract_count}")

    # Close connection
    conn.close()

if __name__ == "__main__":
    init_legal_database()