import sqlite3

conn = sqlite3.connect('data/TrabalhoPCII.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

for t in tables:
    tname = t[0]
    print(f"\n--- {tname} ---")
    cursor.execute(f"PRAGMA table_info({tname})")
    print("Columns:", cursor.fetchall())
    cursor.execute(f"SELECT COUNT(*) FROM {tname}")
    print("Row count:", cursor.fetchone()[0])
    cursor.execute(f"SELECT * FROM {tname} LIMIT 5")
    print("Sample rows:")
    for row in cursor.fetchall():
        print("  ", row)

conn.close()
