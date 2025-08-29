#!/usr/bin/env python3
"""
Test script for Neon PostgreSQL connection
"""

import psycopg2
from urllib.parse import urlparse

def test_neon_connection():
    """Test connection to Neon PostgreSQL"""
    
    # Your connection parameters
    host = "ep-steep-bird-ad2sl2ot-pooler.c-2.us-east-1.aws.neon.tech"
    database = "neondb"
    user = "neondb_owner"
    password = "npg_elOCzby1W5Tr"
    port = 5432
    
    print("=== Testing Neon PostgreSQL Connection ===")
    print(f"Host: {host}")
    print(f"Database: {database}")
    print(f"User: {user}")
    print(f"Port: {port}")
    print(f"Password: {password[:4]}...{password[-4:] if len(password) > 8 else '***'}")
    print()
    
    try:
        # Test direct connection
        print("Testing direct psycopg2 connection...")
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
            sslmode='require'
        )
        
        print("✅ Successfully connected to Neon PostgreSQL!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL Version: {version[0]}")
        
        cursor.close()
        conn.close()
        print("✅ Connection test completed successfully!")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\n=== Troubleshooting Tips ===")
        print("1. Check if password is correct in Neon dashboard")
        print("2. Try resetting the password")
        print("3. Verify user permissions")
        print("4. Check if database exists")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_neon_connection()
