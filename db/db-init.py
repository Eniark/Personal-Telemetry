import sqlite3
from configs import DB_PATH

# FIXME: Manual commit() and close() leave the database prone to locking if an exception occurs mid-execution.
# SUGGESTION: Use a context manager: `with sqlite3.connect(DB_PATH) as conn:` which handles commits and rollbacks safely.
conn = sqlite3.connect(DB_PATH)

# FIXME: SQLite ignores foreign key constraints by default.
# SUGGESTION: `conn.execute("PRAGMA foreign_keys = ON;")` after establishing the connection, both here and in main.
cursor = conn.cursor()

# The table for OS processes
cursor.execute(
    # FIXME: CRITICAL SCHEMA MISMATCH. You define `event_time` here, but in `main.py` your INSERT query uses `started_at`. This will immediately crash with an OperationalError.
    # SUGGESTION: Rename.
    """
    CREATE TABLE IF NOT EXISTS os_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        window TEXT,
        event_time INTEGER,
        type TEXT
    )
    """)

# The table for browser events
cursor.execute(
    # FIXME: CRITICAL SCHEMA MISMATCH again. `main.py` expects `started_at`, not `event_time`.
    # SUGGESTION: Rename

    # FIXME: `duration_ms` is defined here but completely ignored in the `main.py` INSERT query. It will always be NULL.
    # SUGGESTION: Either calculate and insert it in `main.py`, or drop it and define it as a generated column: `duration_ms INTEGER GENERATED ALWAYS AS (ended_at - started_at) VIRTUAL`.
    """
    CREATE TABLE IF NOT EXISTS browser_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        website TEXT,
        event_time INTEGER,
        ended_at INTEGER,
        duration_ms INTEGER,
        activity_id INTEGER,
        -- FIXME: Missing index on the Foreign Key. When querying child records by parent ID, this will cause a full table scan.
        -- DIRECTION: Add a separate statement below: `CREATE INDEX IF NOT EXISTS idx_browser_activity_id ON browser_activity(activity_id);`
        FOREIGN KEY (activity_id) REFERENCES os_activity(id) 
    )
    """)



conn.commit()
conn.close()