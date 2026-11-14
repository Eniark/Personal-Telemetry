from shared.configs import DB_PATH
from shared.utils import create_db_connection


def create_os_events_table(cursor):
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
            classified_by TEXT,
            classification_approved BOOL,
            duration_seconds REAL GENERATED ALWAYS AS (
                unixepoch(end_timestamp) - unixepoch(start_timestamp)
            ) VIRTUAL
        )
        """)

def create_browser_events_table(cursor):
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
            class TEXT,
            classified_at TEXT,
            classified_by TEXT,
            classification_approved BOOL,
            duration_seconds REAL GENERATED ALWAYS AS (
                unixepoch(end_timestamp) - unixepoch(start_timestamp)
            ) VIRTUAL,
            FOREIGN KEY (os_event_id) REFERENCES os_events(event_id) 
        )
        """)

def create_last_day_view(cursor, table_name, view_name):
    cursor.execute("DROP VIEW IF EXISTS \"main\".\"browser_events_class_distribution_today\"");
    cursor.execute(
       f"""
            CREATE VIEW {view_name} AS
            SELECT
                class,
                SUM(duration_seconds) AS total_seconds,
                ROUND(
                    100.0 * SUM(duration_seconds)
                    / SUM(SUM(duration_seconds)) OVER (),
                    2
                ) AS percentage
            FROM {table_name}
            WHERE DATE(event_start_time) = DATE('now')
            GROUP BY class
        """
    )


def create_last_month_view(cursor, table_name, view_name):
    cursor.execute("DROP VIEW IF EXISTS \"main\".\"browser_events_class_distribution_month\"");
    cursor.execute(
        """
            CREATE VIEW browser_events_class_distribution_month AS
            SELECT
                class,
                SUM(duration_seconds) AS total_seconds,
                ROUND(
                    100.0 * SUM(duration_seconds)
                    / SUM(SUM(duration_seconds)) OVER (),
                    2
                ) AS percentage
            FROM browser_events
            WHERE DATE(event_start_time) >= DATE('now', 'start of month')
            GROUP BY class
        """
    )


if __name__=='__main__':
    with create_db_connection(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;") # enforces foreign key constraints
        cursor = conn.cursor()
        # === Table Initialization ===
        create_os_events_table(cursor)
        create_browser_events_table(cursor)
        # ============================

        # === Views Initialization ===
        create_last_day_view(cursor, "os_events", view_name="os_events_class_distribution_today")
        create_last_day_view(cursor, "browser_events", view_name="browser_events_class_distribution_today")
        create_last_month_view(cursor, "os_events", view_name="os_class_distribution_month")
        create_last_month_view(cursor, "browser_events", view_name="browser_events_class_distribution_month")
        # ============================
