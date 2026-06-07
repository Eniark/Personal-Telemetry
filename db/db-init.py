import sqlite3

conn = sqlite3.connect("activity.db")
cursor = conn.cursor()

# The main activity table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        window TEXT,
        started_at INTEGER
    )
    """)

# The table for "browser" events
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS browser_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        website TEXT,
        started_at INTEGER,
        ended_at INTEGER,
        duration_ms INTEGER,
        activity_id INTEGER,
        FOREIGN KEY (activity_id) REFERENCES activity(id) 
    )
    """)



conn.commit()
conn.close()