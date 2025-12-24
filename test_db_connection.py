#!/usr/bin/env python
"""
Test script to verify Supabase PostgreSQL connection.
Can be run standalone or as a Django management command.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection_standalone():
    """Test database connection using psycopg2 directly"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        print("Testing Supabase PostgreSQL connection...")
        print("=" * 50)
        
        # Get connection parameters
        db_host = os.getenv('SUPABASE_DB_HOST', '')
        db_port = os.getenv('SUPABASE_DB_PORT', '5432')
        db_name = os.getenv('SUPABASE_DB_NAME', 'postgres')
        db_user = os.getenv('SUPABASE_DB_USER', '')
        db_password = os.getenv('SUPABASE_DB_PASSWORD', '')
        database_url = os.getenv('DATABASE_URL', '')
        
        # Determine connection method
        if database_url and 'pooler' not in db_host:
            print("Using DATABASE_URL connection string")
            parsed = urlparse(database_url)
            conn_params = {
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'database': parsed.path.lstrip('/'),
                'user': parsed.username,
                'password': parsed.password,
            }
        elif db_host and 'pooler' in db_host:
            print("Using pooler connection")
            conn_params = {
                'host': db_host,
                'port': int(db_port) if db_port else 6543,
                'database': db_name,
                'user': db_user,
                'password': db_password,
            }
        else:
            print("Using direct connection")
            conn_params = {
                'host': db_host,
                'port': int(db_port) if db_port else 5432,
                'database': db_name,
                'user': db_user,
                'password': db_password,
            }
        
        # Add SSL configuration
        conn_params['sslmode'] = 'require'
        
        print(f"   Host: {conn_params['host']}")
        print(f"   Port: {conn_params['port']}")
        print(f"   Database: {conn_params['database']}")
        print(f"   User: {conn_params['user']}")
        print(f"   Password: {'*' * len(conn_params['password']) if conn_params['password'] else 'NOT SET'}")
        print()
        
        # Attempt connection
        print("Attempting connection...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute('SELECT version(), NOW(), current_database(), current_user;')
        result = cursor.fetchone()
        
        print("SUCCESS: Connection successful!")
        print("=" * 50)
        print(f"PostgreSQL Version: {result[0]}")
        print(f"Current Time: {result[1]}")
        print(f"Database: {result[2]}")
        print(f"User: {result[3]}")
        print("=" * 50)
        
        # Test additional queries
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        table_count = cursor.fetchone()[0]
        print(f"Public schema tables: {table_count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except ImportError:
        print("ERROR: psycopg2 is not installed")
        print("   Install it with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print("ERROR: Connection failed!")
        print("=" * 50)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        if hasattr(e, 'pgcode'):
            print(f"PostgreSQL Error Code: {e.pgcode}")
        print("=" * 50)
        return False

def test_connection_django():
    """Test database connection using Django"""
    try:
        import django
        from django.conf import settings
        from django.db import connection
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wesolucions.settings')
        django.setup()
        
        print("Testing Supabase PostgreSQL connection via Django...")
        print("=" * 50)
        
        # Get database config
        db_config = settings.DATABASES['default']
        print(f"   Engine: {db_config['ENGINE']}")
        print(f"   Host: {db_config['HOST']}")
        print(f"   Port: {db_config['PORT']}")
        print(f"   Database: {db_config['NAME']}")
        print(f"   User: {db_config['USER']}")
        print()
        
        # Test connection
        print("Attempting connection...")
        with connection.cursor() as cursor:
            cursor.execute('SELECT version(), NOW(), current_database(), current_user;')
            result = cursor.fetchone()
            
            print("SUCCESS: Connection successful!")
            print("=" * 50)
            print(f"PostgreSQL Version: {result[0]}")
            print(f"Current Time: {result[1]}")
            print(f"Database: {result[2]}")
            print(f"User: {result[3]}")
            print("=" * 50)
            
            # Test table count
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
            table_count = cursor.fetchone()[0]
            print(f"Public schema tables: {table_count}")
        
        return True
        
    except Exception as e:
        print("ERROR: Connection failed!")
        print("=" * 50)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("=" * 50)
        return False

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  WEsolucions Backend - Database Connection Test")
    print("=" * 50 + "\n")
    
    # Try Django first, fallback to standalone
    if os.path.exists('manage.py'):
        print("Django project detected, using Django connection...\n")
        success = test_connection_django()
    else:
        print("Standalone mode, using direct psycopg2 connection...\n")
        success = test_connection_standalone()
    
    sys.exit(0 if success else 1)

