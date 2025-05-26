import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()


cursor.execute("""CREATE TABLE IF NOT EXISTS users(
id INT PRIMARY KEY AUTOINCREMENT,
name TEXT,
login TEXT,
password TEXT,
Account REAL
)
""")


cursor.execute("""CREATE TABLE IF NOT EXISTS credit(
id INT PRIMARY KEY AUTOINCREMENT,
userId INT,
Amount REAL,
PPY REAL,
AdInfo TEXT
)
""")

