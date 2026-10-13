from enum import Enum

class EventType(Enum):
    BROWSER = 'browser'
    OS = 'os'
    PHONE_OS = 'phone_os'

class EventCategory(Enum):
    STUDYING = "studying"
    GAMING = "gaming"
    SOCIAL_MEDIA = "social_media"
    ENTERTAINMENT = 'entertainment'
    MUSIC = "music"
    SHOPPING = "shopping"
    NEWS = "news"
    OTHER = "other"