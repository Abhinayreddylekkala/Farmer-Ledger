import sqlite3
import os

# We will look for the database in both possible locations
possible_files = ['farmers.db', 'instance/farmers.db']
found = False

for db_path in possible_files:
    if os.path.exists(db_path):
        found = True
        print(f"🔍 Found database at: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 1. Fix Payment Table (Add Status)
            try:
                cursor.execute("ALTER TABLE payment ADD COLUMN status VARCHAR(20) DEFAULT 'Pending'")
                print(f"   ✅ Fixed: Added 'status' to payment in {db_path}")
            except Exception as e:
                print(f"   ⚠️  Note: {e} (This likely means it was already fixed)")

            # 2. Fix Businessman Table (Add Status)
            try:
                cursor.execute("ALTER TABLE businessman_sale ADD COLUMN status VARCHAR(20) DEFAULT 'Pending'")
                print(f"   ✅ Fixed: Added 'status' to businessman_sale in {db_path}")
            except Exception as e:
                print(f"   ⚠️  Note: {e}")

            conn.commit()
            conn.close()
            print("------------------------------------------------")
        except Exception as e:
            print(f"❌ Error opening {db_path}: {e}")

if not found:
    print("❌ I could not find any 'farmers.db' file. Run app.py once to create it.")
else:
    print("🎉 DIAGNOSIS COMPLETE. Try running your app now.")