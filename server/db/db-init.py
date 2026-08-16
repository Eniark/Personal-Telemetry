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
            event_id TEXT,
            title TEXT,
            executable TEXT,
            publisher TEXT,
            description TEXT,
            event_start_time TEXT,
            event_end_time TEXT,
            type TEXT,
            processing_time TEXT
        )
        """)

    # The table for browser events
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS browser_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            event_start_time TEXT,
            event_end_time TEXT,
            processing_time TEXT,
            os_event_id TEXT,
            FOREIGN KEY (os_event_id) REFERENCES os_event(event_id) 
        )
        """)
    # cursor.execute(
    #     """
    #         CREATE INDEX IF NOT EXISTS idx_browser_event_id ON browser_events(os_event_id);
    #     """)
    