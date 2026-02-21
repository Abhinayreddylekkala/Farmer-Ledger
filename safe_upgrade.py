import sqlite3
import os
from werkzeug.security import generate_password_hash

# 1. Locate the database safely
db_path = 'instance/farmers.db'
if not os.path.exists(db_path):
    db_path = 'farmers.db'

print(f"Upgrading your database safely at: {db_path}...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. Fix the User table (Since this is new, it's safe to drop and recreate)
cursor.execute('DROP TABLE IF EXISTS user')
cursor.execute('''
    CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL
    )
''')

# 3. Create the default admin account
hashed_pw = generate_password_hash("password123")
cursor.execute("INSERT INTO user (username, password_hash) VALUES (?, ?)", ("admin", hashed_pw))

# 4. Add the username connection to all old data
tables = ['bill', 'payment', 'businessman_sale']
for table in tables:
    try:
        # Try to add the column if it's missing
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN username VARCHAR(50) DEFAULT 'admin'")
        print(f"✅ Upgraded {table} table.")
    except sqlite3.OperationalError:
        # If it already exists, just make sure old rows belong to admin
        print(f"⚡ {table} already has the column, linking old records to admin...")
        
    cursor.execute(f"UPDATE {table} SET username='admin' WHERE username IS NULL")

conn.commit()
conn.close()
print("🎉 Upgrade complete! Your father's old data is SAFE.")