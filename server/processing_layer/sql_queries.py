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