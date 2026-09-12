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

SELECT_ALL_EVENTS_QUERY = """
    SELECT os.title, os.executable, os.event_start_time AS os_event_start_time, os.event_end_time AS os_event_end_time,
            browser.url, browser.title AS browser_tab_title FROM os_events
        AS os LEFT JOIN browser_events AS browser
        ON os.id=browser.os_event_id;
"""