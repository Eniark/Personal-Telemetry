import datetime
from dotenv import load_dotenv
import os

from shared.configs import TIMESTAMP_FORMAT


def get_env_variables():
    REQUIRED_ENV_VARS = ["PORT"]
    
    for var in REQUIRED_ENV_VARS:
        if os.getenv(var) is None:
            raise ValueError(f'"{var}" must be defined in the .env file')

    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))

    return host, port

def convert_date_to_readable_format(unix_time: int) -> str:
    event_time = (
        datetime.datetime
            .fromtimestamp(unix_time)
            .strftime(TIMESTAMP_FORMAT) # Converts Unix-style timetamp to human-readable format 
    )
    return event_time