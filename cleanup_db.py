#!/usr/bin/env python3
"""
Direct database cleanup script for Valentine Magic test events.
This script bypasses Flask app initialization to avoid scheduler issues.
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def cleanup_test_events():
    # Database connection parameters
    conn_params = {
        'host': 'localhost',
        'database': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'port': 5432
    }
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Check how many events will be deleted
        cursor.execute("SELECT COUNT(*) FROM event WHERE id >= 2001 AND id <= 2077")
        count = cursor.fetchone()[0]
        print(f"Found {count} test events to delete")
        
        if count > 0:
            # Delete the test events
            cursor.execute("DELETE FROM event WHERE id >= 2001 AND id <= 2077")
            print(f"Deleted {cursor.rowcount} events")
            
            # Commit the transaction
            conn.commit()
            
            # Verify deletion
            cursor.execute("SELECT COUNT(*) FROM event WHERE id >= 2001 AND id <= 2077")
            remaining = cursor.fetchone()[0]
            print(f"Remaining events in range: {remaining}")
            
            # Show current max ID
            cursor.execute("SELECT MAX(id) FROM event")
            max_id = cursor.fetchone()[0]
            print(f"Current max event ID: {max_id}")
            
        else:
            print("No test events found to delete")
            
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    cleanup_test_events()