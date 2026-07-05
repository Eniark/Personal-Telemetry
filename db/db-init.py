import sqlite3
from configs import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# The table for OS processes
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS os_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        window TEXT,
        started_at INTEGER,
        type TEXT
    )
    """)

# The table for browser events
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS browser_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        website TEXT,
        started_at INTEGER,
        ended_at INTEGER,
        duration_ms INTEGER,
        activity_id INTEGER,
        FOREIGN KEY (activity_id) REFERENCES os_activity(id) 
    )
    """)



conn.commit()
conn.close()