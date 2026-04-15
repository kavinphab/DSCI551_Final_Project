#!/usr/bin/env python3
"""
Initialize the PostgreSQL database with tables and sample data.
Run this once to set up the database for the dashboard.
"""

import os
import sys
from datetime import datetime, timedelta
import random

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection_kwargs():
    """Get database connection parameters from environment."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return {"conninfo": db_url}
    
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE"),
        "user": os.getenv("PGUSER"),
        "password": os.getenv("PGPASSWORD"),
    }


def create_tables(conn):
    """Create the required tables."""
    with conn.cursor() as cur:
        print("Creating tables...")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id SERIAL PRIMARY KEY,
                owner_id INT,
                asset_name TEXT,
                value INT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id INT,
                asset_id INT,
                amount INT,
                created_at TIMESTAMP
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                event TEXT,
                created_at TIMESTAMP
            );
        """)
        
        conn.commit()
    print("✓ Tables created")


def populate_users(conn, count=100000):
    """Insert sample users."""
    print(f"Inserting {count:,} users...")
    with conn.cursor() as cur:
        for i in range(0, count, 1000):
            batch = []
            for j in range(1000):
                user_id = i + j + 1
                batch.append((
                    f"User_{user_id}",
                    f"user{user_id}@example.com",
                    datetime.now() - timedelta(days=random.randint(1, 365))
                ))
            
            cur.executemany(
                "INSERT INTO users (name, email, created_at) VALUES (%s, %s, %s)",
                batch
            )
            conn.commit()
            if (i + 1000) % 10000 == 0:
                print(f"  {i + 1000:,} users inserted")
    print("✓ Users inserted")


def populate_assets(conn, count=200000):
    """Insert sample assets."""
    print(f"Inserting {count:,} assets...")
    asset_names = ["Stock", "Bond", "Real Estate", "Vehicle", "Equipment", "Cryptocurrency"]
    
    with conn.cursor() as cur:
        for i in range(0, count, 1000):
            batch = []
            for j in range(1000):
                batch.append((
                    random.randint(1, 100000),  # owner_id (users)
                    f"{random.choice(asset_names)}_{i + j + 1}",
                    random.randint(1000, 1000000),
                    datetime.now() - timedelta(days=random.randint(1, 365))
                ))
            
            cur.executemany(
                "INSERT INTO assets (owner_id, asset_name, value, created_at) VALUES (%s, %s, %s, %s)",
                batch
            )
            conn.commit()
            if (i + 1000) % 50000 == 0:
                print(f"  {i + 1000:,} assets inserted")
    print("✓ Assets inserted")


def populate_transactions(conn, count=500000):
    """Insert sample transactions."""
    print(f"Inserting {count:,} transactions...")
    
    with conn.cursor() as cur:
        for i in range(0, count, 1000):
            batch = []
            for j in range(1000):
                batch.append((
                    random.randint(1, 100000),  # user_id
                    random.randint(1, 200000),  # asset_id
                    random.randint(100, 50000),  # amount
                    datetime.now() - timedelta(days=random.randint(1, 365), hours=random.randint(0, 23))
                ))
            
            cur.executemany(
                "INSERT INTO transactions (user_id, asset_id, amount, created_at) VALUES (%s, %s, %s, %s)",
                batch
            )
            conn.commit()
            if (i + 1000) % 100000 == 0:
                print(f"  {i + 1000:,} transactions inserted")
    print("✓ Transactions inserted")


def populate_logs(conn, count=100000):
    """Insert sample logs."""
    print(f"Inserting {count:,} logs...")
    events = [
        "User login",
        "Asset update",
        "Transaction created",
        "Report generated",
        "Database backup",
        "Index created",
        "Query executed"
    ]
    
    with conn.cursor() as cur:
        for i in range(0, count, 1000):
            batch = []
            for j in range(1000):
                batch.append((
                    f"{random.choice(events)} - Event {i + j + 1}",
                    datetime.now() - timedelta(days=random.randint(1, 365), hours=random.randint(0, 23))
                ))
            
            cur.executemany(
                "INSERT INTO logs (event, created_at) VALUES (%s, %s)",
                batch
            )
            conn.commit()
            if (i + 1000) % 10000 == 0:
                print(f"  {i + 1000:,} logs inserted")
    print("✓ Logs inserted")


def main():
    """Initialize the database."""
    try:
        kwargs = get_connection_kwargs()
        print(f"Connecting to database at {kwargs.get('host', 'localhost')}...")
        conn = psycopg.connect(**kwargs)
        
        print("Connected!\n")
        
        # Create tables
        create_tables(conn)
        
        # Populate tables
        populate_users(conn, 100000)
        populate_assets(conn, 200000)
        populate_transactions(conn, 500000)
        populate_logs(conn, 100000)
        
        conn.close()
        print("\n✅ Database initialized successfully!")
        print("\nYou can now run: streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
