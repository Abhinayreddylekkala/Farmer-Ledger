import sqlite3
import os

# Find the database
if os.path.exists('instance/farmers.db'):
    db_path = 'instance/farmers.db'
elif os.path.exists('farmers.db'):
    db_path = 'farmers.db'
else:
    print("❌ Error: Database not found!")
    exit()

print(f"✅ Found database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the new Payment table
    print("⏳ Creating 'payment' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            farmer_name TEXT,
            date TEXT,
            amount INTEGER,
            method TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("🎉 Success! Payment table added.")

except Exception as e:
    print(f"⚠️ Error: {e}")