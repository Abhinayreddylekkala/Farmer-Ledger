import sqlite3
import os

# Check where the database file is
if os.path.exists('instance/farmers.db'):
    db_path = 'instance/farmers.db'
elif os.path.exists('farmers.db'):
    db_path = 'farmers.db'
else:
    print("❌ Could not find farmers.db! Are you in the right folder?")
    exit()

print(f"✅ Found database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Run the command to add the missing 'status' column
    print("⏳ Adding 'status' column to 'businessman_sale' table...")
    cursor.execute("ALTER TABLE businessman_sale ADD COLUMN status VARCHAR(20) DEFAULT 'Pending'")
    
    conn.commit()
    conn.close()
    print("🎉 Success! Column added. Your data is safe.")

except Exception as e:
    print(f"⚠️ Error: {e}")
    print("This usually means the column already exists or the database is locked.")