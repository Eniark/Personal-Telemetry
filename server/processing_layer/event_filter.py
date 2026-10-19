


from .event import EventType


class EventFilter:
    IGNORED_PROCESSES = [
        "explorer.exe",

    ]
    IGRNORED_URLS = [
        "newtab",
        "chrome://newtab",
    ]
    
    def is_valid_event(self, event):
        if event.category == EventType.OS:
            return event.process not in EventFilter.IGNORED_PROCESSES
        else:
            return event.url not in EventFilter.IGRNORED_URLS