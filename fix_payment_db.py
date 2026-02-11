import sqlite3
import os

# Check common locations for the database
if os.path.exists('instance/farmers.db'):
    db_path = 'instance/farmers.db'
elif os.path.exists('farmers.db'):
    db_path = 'farmers.db'
else:
    print("❌ Error: Could not find farmers.db")
    print(f"   Current folder: {os.getcwd()}")
    exit()

print(f"✅ Found database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add the missing 'status' column
    print("⏳ Adding 'status' column to 'payment' table...")
    cursor.execute("ALTER TABLE payment ADD COLUMN status VARCHAR(20) DEFAULT 'Pending'")
    
    conn.commit()
    conn.close()
    print("🎉 Success! The database is now fixed.")

except Exception as e:
    print(f"⚠️ Note: {e}")
    print("If it says 'duplicate column', that is good! It means you are already fixed.")