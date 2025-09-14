#!/usr/bin/env python3
"""
Legal AI Database Initialization Script
Sets up SQLite database with schema and sample legal data
"""

import sqlite3
import os
from pathlib import Path

def initialize_database():
    """Initialize the legal AI database with schema and sample data"""

    # Ensure database directory exists
    db_dir = Path("database")
    db_dir.mkdir(exist_ok=True)

    # Database file path
    db_path = db_dir / "legal_data.db"

    # Read schema file
    schema_path = db_dir / "schema.sql"
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return False

    try:
        # Connect to database
        print(f"🗄️  Initializing database: {db_path}")
        conn = sqlite3.connect(db_path)

        # Read and execute schema (includes sample data)
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute schema
        conn.executescript(schema_sql)
        conn.commit()

        # Verify tables were created
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"✅ Database initialized successfully!")
        print(f"📊 Created {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {table[0]}: {count} records")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def verify_legal_data():
    """Verify legal data integrity"""
    try:
        db_path = Path("database/legal_data.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check case law data
        cursor.execute("SELECT COUNT(*) FROM case_law")
        case_count = cursor.fetchone()[0]

        # Check statutes data
        cursor.execute("SELECT COUNT(*) FROM statutes")
        statute_count = cursor.fetchone()[0]

        # Check precedents data
        cursor.execute("SELECT COUNT(*) FROM legal_precedents")
        precedent_count = cursor.fetchone()[0]

        # Check contracts data
        cursor.execute("SELECT COUNT(*) FROM contracts")
        contract_count = cursor.fetchone()[0]

        print(f"📚 Legal Knowledge Base:")
        print(f"   - Case Law: {case_count} cases")
        print(f"   - Statutes: {statute_count} statutes")
        print(f"   - Precedents: {precedent_count} precedents")
        print(f"   - Contracts: {contract_count} templates")

        # Verify indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND sql IS NOT NULL;")
        indexes = cursor.fetchall()
        print(f"🔍 Database Indexes: {len(indexes)} performance indexes created")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Data verification failed: {e}")
        return False

if __name__ == "__main__":
    print("⚖️  Legal AI Database Initialization")
    print("=" * 50)

    # Initialize database
    if initialize_database():
        # Verify data integrity
        if verify_legal_data():
            print("\n✅ Legal AI database ready for use!")
            print("🔧 Start the backend with: python app.py")
        else:
            print("\n⚠️  Database created but data verification failed")
    else:
        print("\n❌ Database initialization failed")
        exit(1)