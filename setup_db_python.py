#!/usr/bin/env python3
"""
Python script to setup MySQL database schema.
Works without requiring mysql-client to be installed.
"""
import pymysql
import sys
from pathlib import Path

# Database connection details
MYSQL_CONFIG = {
    'host': 'shortline.proxy.rlwy.net',
    'port': 52538,
    'user': 'root',
    'password': 'tTAhOqSOcqIFcTUygPFvaRJowmMPadgn',
    'database': 'railway',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def print_header(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")

def print_success(msg):
    print(f"✓ {msg}")

def print_error(msg):
    print(f"✗ {msg}", file=sys.stderr)

def print_info(msg):
    print(f"ℹ {msg}")

def main():
    print_header("GenAI Coach - Database Setup (Python)")

    # Check if schema file exists
    schema_file = Path(__file__).parent / 'schema.sql'
    if not schema_file.exists():
        print_error(f"Schema file not found: {schema_file}")
        sys.exit(1)

    print_success(f"Schema file found: {schema_file}")

    # Read schema file
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    try:
        print_header("Connecting to Database")
        print_info(f"Host: {MYSQL_CONFIG['host']}")
        print_info(f"Port: {MYSQL_CONFIG['port']}")
        print_info(f"User: {MYSQL_CONFIG['user']}")
        print_info(f"Database: {MYSQL_CONFIG['database']}")

        # Connect to database
        connection = pymysql.connect(**MYSQL_CONFIG)
        print_success("Connected successfully!")

        with connection:
            with connection.cursor() as cursor:
                print_header("Executing Schema")

                # Split SQL file into individual statements
                statements = []
                current_statement = []

                for line in schema_sql.split('\n'):
                    # Skip comments and empty lines
                    line = line.strip()
                    if not line or line.startswith('--'):
                        continue

                    current_statement.append(line)

                    # Check if statement is complete (ends with semicolon)
                    if line.endswith(';'):
                        stmt = ' '.join(current_statement)
                        statements.append(stmt)
                        current_statement = []

                # Execute each statement
                executed = 0
                for stmt in statements:
                    if stmt.strip():
                        try:
                            cursor.execute(stmt)
                            executed += 1
                        except pymysql.Error as e:
                            # Ignore certain errors (like DROP TABLE IF NOT EXISTS when table doesn't exist)
                            if 'Unknown table' not in str(e):
                                print_info(f"Note: {e}")

                connection.commit()
                print_success(f"Executed {executed} SQL statements successfully!")

                print_header("Verification")

                # Show tables
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()

                if not tables:
                    print_error("No tables found after schema execution!")
                    sys.exit(1)

                print_success("Tables created:")
                for table_dict in tables:
                    table_name = list(table_dict.values())[0]
                    print(f"  • {table_name}")

                # Get row counts
                print_info("\nTable statistics:")
                for table_dict in tables:
                    table_name = list(table_dict.values())[0]
                    cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`;")
                    result = cursor.fetchone()
                    count = result['count']
                    print(f"  • {table_name}: {count} rows")

                print_header("Setup Complete")
                print_success("Database schema setup completed successfully!")

                print_info("\nNext steps:")
                print("  1. Update your .env file with the database URL")
                print("  2. Test the connection from your application")
                print("  3. Deploy your application to Railway")

                print_info("\nDatabase URL for .env:")
                print(f"  DATABASE_URL=\"mysql+aiomysql://root:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}\"")

    except pymysql.Error as e:
        print_error(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
