from shared.configs import DB_PATH

from .db_connect import create_db_connection
with create_db_connection(DB_PATH) as conn:

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
            processing_time TEXT,
            previous_events TEXT,
            class TEXT,
            classified_at TEXT,
            classified_by TEXT
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