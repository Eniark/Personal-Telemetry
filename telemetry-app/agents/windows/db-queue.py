from shared.configs import QUEUE_DB_PATH
from shared.utils import create_db_connection

print(QUEUE_DB_PATH)
with create_db_connection(QUEUE_DB_PATH) as conn:

    cursor = conn.cursor()
    
    # The table for events will act as a durable storage queue
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
            browser_events TEXT,
            inserted_at TEXT
        )
        """)