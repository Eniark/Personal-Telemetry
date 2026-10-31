
UPSERT_EVENTS_QUERY = """
    INSERT INTO events(
        event_id,
        title,
        executable,
        publisher,
        event_start_time,
        event_end_time,
        type,
        previous_events,
        acknowledged,
        browser_events,
        sent_at,
        inserted_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ON CONFLICT(event_id)
    DO UPDATE SET
        acknowledged=excluded.acknowledged
""" 

SELECT_EVENTS_QUERY = """
    SELECT
        id,  
        event_id,
        title,
        executable,
        publisher,
        event_start_time,
        event_end_time,
        type,
        previous_events,
        browser_events,
        sent_at
    FROM events
    WHERE acknowledged=false
"""