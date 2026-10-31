
INSERT_EVENTS_QUERY = """
    INSERT INTO events(
        event_id,
        title,
        executable,
        publisher,
        description,
        event_start_time,
        event_end_time,
        type,
        processing_time,
        previous_events,
        acknowledged,
        browser_events,
        sent_at,
        inserted_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
""" 
