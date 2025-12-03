#!/usr/bin/env python3
"""Verify database schema structure."""
import pymysql

MYSQL_CONFIG = {
    'host': 'shortline.proxy.rlwy.net',
    'port': 52538,
    'user': 'root',
    'password': 'tTAhOqSOcqIFcTUygPFvaRJowmMPadgn',
    'database': 'railway',
    'charset': 'utf8mb4',
}

connection = pymysql.connect(**MYSQL_CONFIG)
with connection.cursor() as cursor:
    print("\n" + "="*80)
    print("DATABASE SCHEMA VERIFICATION")
    print("="*80)

    # Check users table
    print("\n📋 USERS TABLE:")
    print("-" * 80)
    cursor.execute("DESCRIBE users;")
    for row in cursor.fetchall():
        print(f"  {row[0]:20} {row[1]:30} {row[2]:8} {row[3]:8}")

    # Check interview_sessions table
    print("\n📋 INTERVIEW_SESSIONS TABLE:")
    print("-" * 80)
    cursor.execute("DESCRIBE interview_sessions;")
    for row in cursor.fetchall():
        print(f"  {row[0]:25} {row[1]:30} {row[2]:8} {row[3]:8}")

    # Check uploads table
    print("\n📋 UPLOADS TABLE:")
    print("-" * 80)
    cursor.execute("DESCRIBE uploads;")
    for row in cursor.fetchall():
        print(f"  {row[0]:20} {row[1]:30} {row[2]:8} {row[3]:8}")

    # Show indexes
    print("\n🔑 INDEXES:")
    print("-" * 80)
    for table in ['users', 'interview_sessions', 'uploads']:
        cursor.execute(f"SHOW INDEX FROM {table};")
        indexes = cursor.fetchall()
        print(f"\n  {table.upper()}:")
        for idx in indexes:
            print(f"    - {idx[2]:30} on column: {idx[4]}")

    print("\n" + "="*80)
    print("✓ Schema verification complete!")
    print("="*80 + "\n")

connection.close()
