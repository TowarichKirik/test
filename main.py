import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
id INT PRIMARY KEY AUTOINCREMENT,
name TEXT,
login TEXT,
password TEXT
""")
cursor.execute("""
""")