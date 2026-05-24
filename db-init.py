import sqlite3

conn = sqlite3.connect("activity.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT,
    started_at INTEGER,
    ended_at INTEGER,
    duration_ms INTEGER
)
""")

conn.commit()
conn.close()