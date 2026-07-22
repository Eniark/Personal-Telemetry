from logger import logger
from processing_layer.event import BrowserEvent, OperatingSystemEvent

class EventProcessor:
    def __init__(self, repository):
        self.repository = repository
        self.os_activity_last_row_id = self.repository.get_max_id("os_activity")
        self.os_activities = []
        self.browser_activities = []
        self.batch_size = 5

    def handle_browser_event(self, event: BrowserEvent):
        self.browser_activities.append(event)
        
        # FIXME: Using '>' instead of '>=' means you store batch_size + 1 items before flushing (e.g. 6 items for batch_size=5). Use '>=' or fix the batch threshold.
        # SUGGESTION: Change to `>= self.batch_size` to strictly honor the exact batch limit.
        if len(self.browser_activities) > self.batch_size:  # fix data sync issue
            self.repository.insert_browser_activities(self.browser_activities)
            self.browser_activities = []
        logger.info(f"Browser Event: {event.website} - {event.os_event_id}")

    def handle_os_event(self, event: OperatingSystemEvent):
        self.os_activities.append(event)
        # FIXME: Incrementing this ID in-memory before DB commit guarantees your state will drift if a DB insert fails. 
        # DIRSUGGESTIONECTION: Only update `os_activity_last_row_id` AFTER a successful DB batch insert, or use UUIDs for events instead of auto-incrementing DB integers.
        self.os_activity_last_row_id += 1
        
        # FIXME: Fatal logic bug. Checking 'len(self.browser_activities)' inside an OS event handler creates cross-domain coupling and race conditions. 
        # Also, you flush browser activities and reset the list, but then immediately try to flush it again inside the block.
        # SUGGESTION: Extract flushing into a dedicated `_flush_all()` method. Call it when either list hits the threshold. Ensure OS events are inserted *before* browser events to satisfy foreign keys.
        if len(self.browser_activities) > self.batch_size: # for case when user is stuck in browser
            self.repository.insert_os_activities(self.os_activities)
            self.os_activities = []

            self.repository.insert_browser_activities(self.browser_activities)
            self.browser_activities = []
        
        elif len(self.os_activities) > self.batch_size:
            self.repository.insert_os_activities(self.os_activities)
            self.os_activities = []
        logger.info(f"OS Event: {event.process} - {self.os_activity_last_row_id}")
    
class ActivityRepository:
    def __init__(self, db):
        self.db = db

    def insert_os_activities(self, activities):
        # FIXME: Redundant parentheses around the list comprehension: `( [ ... ] )`.
        # SUGGESTION: Remove outer parentheses. Just pass the list `[ ... ]` or use a generator expression `( ... for ... )` to save memory.
        cursor = self.db.executemany("""
            INSERT INTO os_activity
            (window, started_at, type)
            VALUES (?, ?, ?)
        """, (
            [
                (
                    activity.process,
                    activity.event_time,
                    activity.type
                )
                for activity in activities
            ]
        ))
        # FIXME: Remove print - Prefer logging instead for more control?
        print(activities)
        self.db.commit()
        # FIXME: executemany() in sqlite3 returns None for cursor.lastrowid. Returning this will break or return incorrect batch ID tracking.
        # FYI: SQLite `RETURNING id` clause with `fetchall()` if you need IDs of batch-inserted rows.
        return cursor.lastrowid

    def insert_browser_activities(self, activities): # not working properly
        # FIXME: "not working properly"??
        self.db.executemany("""
            INSERT INTO browser_activity
            (website, started_at, ended_at, activity_id)
            VALUES (?, ?, ?, ?)
        """, (
            [
                (
                    activity.website,
                    activity.event_time,
                    activity.ended_at,
                    activity.os_event_id
                )
                for activity in activities
            ] 
            
        ))

        self.db.commit()
    
    def get_max_id(self, table_name):
        allowed_tables = ["os_activity"]
        if table_name not in allowed_tables:
            raise ValueError("Unknown table name.")

        # FIXME: Fragile table-driven ID lookup. Relying strictly on sqlite_sequence breaks if the table has no autoincrement or hasn't initialized yet. Fall back to SELECT MAX(id) FROM table.
        # SUGGESTION: Change query to standard aggregate `SELECT COALESCE(MAX(id), 0) FROM ?`. sqlite_seq contains largest EVER, not largest CURRENT. 
        # HACK: Never use f-strings for SQL query values, even with allowlists.
        cursor = self.db.execute(f"SELECT MAX(seq) FROM sqlite_sequence WHERE name=\'{table_name}\'")
        return cursor.fetchone()[0] or 0