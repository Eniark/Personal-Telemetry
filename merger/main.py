

class Activity:
    _instance = None

    def __init__(self, window:str, started_at:int, ended_at:int, category:str = None):
        self.window: str = window
        self.started_at: int = started_at
        self.ended_at: int = ended_at
        self.category: str = category
    
    def __new__(cls, *args, **kwargs):
        if cls()._instance is None:
            return super().__new__(cls)
        return cls._instance


class BrowserActivity(Activity):
    def __init__(self, window:str, started_at:int, ended_at:int, tab_name: str, category:str = None):
        super().___init___(self, window, started_at, ended_at, category)
        self.tab_name = tab_name


