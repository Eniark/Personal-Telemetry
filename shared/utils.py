from dotenv import load_dotenv
import os


def get_env_variables():
    REQUIRED_ENV_VARS = ["PORT"]
    
    for var in REQUIRED_ENV_VARS:
        if os.getenv(var) is None:
            raise ValueError(f'"{var}" must be defined in the .env file')

    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))

    return host, port