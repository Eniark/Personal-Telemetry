import datetime
import os
import sqlite3

from shared.configs import TIMESTAMP_FORMAT


def validate_env_variable(REQUIRED_ENV_VARS = ["PORT"]):
    validated_env_vars = []
    
    for var in REQUIRED_ENV_VARS:
        if os.getenv(var) is None:
            raise ValueError(f'"{var}" must be defined in the .env file')
        else:
            try:
                var = int(var) # for port-like variables
            except TypeError:
                pass
            validated_env_vars.append(var)

    return validated_env_vars

def convert_date_to_readable_format(unix_time: int) -> str:
    event_time = (
        datetime.datetime
            .fromtimestamp(unix_time)
            .strftime(TIMESTAMP_FORMAT) # Converts Unix-style timetamp to human-readable format 
    )
    return event_time

def create_db_connection(DB_PATH: str):
    return sqlite3.connect(DB_PATH, check_same_thread=False)