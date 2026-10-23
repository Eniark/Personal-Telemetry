


from .event import OperatingSystemEvent, BrowserEvent


class EventFilter:
    IGNORED_PROCESSES = [
        "explorer.exe",

    ]
    IGNORED_URLS = [
        "newtab",
        "chrome://newtab",
        "",
    ]
    
    def is_valid_event(self, event):
        if isinstance(event, OperatingSystemEvent):
            return event.process not in EventFilter.IGNORED_PROCESSES
        else:
            return event.url.strip() not in EventFilter.IGNORED_URLS