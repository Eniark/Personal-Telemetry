


from .event import OperatingSystemEvent


class EventFilter:
    IGNORED_PROCESSES = [
        "explorer.exe",

    ]
    IGRNORED_URLS = [
        "newtab",
        "chrome://newtab",
    ]
    
    def is_valid_event(self, event):
        if isinstance(event, OperatingSystemEvent):
            return event.process not in EventFilter.IGNORED_PROCESSES
        else:
            return event.url not in EventFilter.IGRNORED_URLS