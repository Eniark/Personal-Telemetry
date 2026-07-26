import sqlite3
from shared.configs import DB_PATH

with sqlite3.connect(DB_PATH) as conn:

    conn.execute("PRAGMA foreign_keys = ON;") # enforces foreign key constraints
    cursor = conn.cursor()

    # The table for OS processes
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS os_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            window TEXT,
            event_start_time INTEGER,
            type TEXT
        )
        """)

    # The table for browser events
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS browser_event (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT,
            event_start_time INTEGER,
            event_end_time INTEGER,
            event_id INTEGER,
            FOREIGN KEY (event_id) REFERENCES os_event(id) 
        )
        """)
    # The table for browser events
    cursor.execute(
        """
            CREATE INDEX IF NOT EXISTS idx_browser_event_id ON browser_event(event_id);
        """)
    