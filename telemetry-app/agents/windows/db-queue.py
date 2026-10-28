import sqlite3
from shared.configs import QUEUE_DB_PATH


with sqlite3.connect(QUEUE_DB_PATH, check_same_thread=False) as conn:

    cursor = conn.cursor()
    
    # The table for events fo
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS events
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT,
            title TEXT,
            executable TEXT,
            publisher TEXT,
            description TEXT,
            event_start_time TEXT,
            event_end_time TEXT,
            type TEXT,
            processing_time TEXT,
            previous_events TEXT,
            acknowledged BOOL,
            browser_events TEXT
        )
        """)