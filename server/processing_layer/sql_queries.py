INSERT_BROWSER_EVENTS_QUERY = """
    INSERT INTO browser_events
    (url, title, event_start_time, event_end_time, processing_time, os_event_id)
    VALUES (?, ?, ?, ?, ?, ?);
"""

INSERT_OS_EVENTS_QUERY = """
    INSERT INTO os_events
    (
        event_id, 
        title,
        executable,
        publisher,
        description,
        event_start_time,
        event_end_time,
        processing_time,
        type,
        previous_events
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

SELECT_OS_EVENTS_QUERY = """
    SELECT id, event_id, type, title, executable, event_start_time, event_end_time FROM os_events
    WHERE class IS NULL;
"""

SELECT_BROWSER_EVENTS_QUERY = """
    SELECT id, url, title, event_start_time, event_end_time FROM browser_events
    WHERE os_event_id=?
"""

UPDATE_EVENT_CLASS_QUERY = """
    UPDATE os_events
    SET class=?,
        classified_at=?,
        classified_by=?
    WHERE id=?
"""