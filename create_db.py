import sqlite3

conn = sqlite3.connect('database.db')
conn.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    role TEXT,
    skills TEXT
)
''')
conn.close()
