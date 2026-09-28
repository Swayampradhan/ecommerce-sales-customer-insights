"""
Quick MySQL connection tester — run this to confirm your password works.
Usage: python mysql/test_connection.py <your_password>
"""
import sys
import mysql.connector

password = sys.argv[1] if len(sys.argv) > 1 else input("Enter MySQL root password: ")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=password
    )
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()[0]
    print(f"Connected successfully! MySQL version: {version}")
    conn.close()
except mysql.connector.Error as e:
    print(f"Connection failed: {e}")
