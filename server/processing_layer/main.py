import sqlite3
from server.logger import logger
from server.processing_layer.event import BrowserEvent, OperatingSystemEvent

class EventProcessor:
    def __init__(self, repository):
        self.repository = repository
        self.os_event_last_id = self.repository.get_max_id("os_events")
        self.events = {}
        self.batch_size = 5

    def _flush_if_needed(self):
        if len(self.events) >= self.batch_size:
            os_events = self.events.values()
            last_event_id = self.repository.insert_os_events(os_events)
            print(last_event_id)
            if last_event_id: # successfull transaction
                print(self.os_event_last_id)
                self.os_event_last_id = last_event_id
                print(self.os_event_last_id)
                for os_event in os_events:
                    browser_events = os_event.linked_browser_events
                    self.repository.insert_browser_events(browser_events)
                self.events.clear()
        
    def handle_browser_event(self, event: BrowserEvent):
        os_event = self.events.get(self.os_event_last_id)
        if os_event:
            os_event.linked_browser_events.append(event)
        self._flush_if_needed()
        logger.info(f"Browser Event: {event.website} - {event.os_event_id}")

    def handle_os_event(self, event: OperatingSystemEvent):
        self.events[self.os_event_last_id + 1] = event
        self._flush_if_needed()
        logger.info(f"OS Event: {event.process} - {self.os_event_last_id}")
    
class ActivityRepository:
    def __init__(self, db):
        self.db = db

    def insert_os_events(self, activities):
        cursor = self.db.executemany("""
            INSERT INTO os_events
            (window, event_start_time, type)
            VALUES (?, ?, ?)
            RETURNING id;
        """, (
            (
                activity.process,
                activity.event_time,
                activity.type
            )
            for activity in activities
        ))
        try:
            self.db.commit()
        except sqlite3.Error as e:
            print(e)
            return None
        ids = cursor.fetchall()
        print('INSERTED')
        return ids

    def insert_browser_events(self, activities):
        cursor = self.db.executemany("""
            INSERT INTO browser_events
            (website, event_start_time, event_end_time, os_event_id)
            VALUES (?, ?, ?, ?)
            RETURNING id;
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
        ids = cursor.fetchall()
        return ids

    
    def get_max_id(self, table_name):
        allowed_tables = ["os_events"]
        if table_name not in allowed_tables:
            raise ValueError("Unknown table name.")

        cursor = self.db.execute(f"SELECT COALESCE(MAX(id), 0) FROM \'{table_name}\'") # SQLite does not support ? substitution for table names, hence doing an f-string
        return cursor.fetchone()[0] or 0