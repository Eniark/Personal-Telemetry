# NOTE: move the application-related libraries to their respective directories
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Logs configs
LOGS_FOLDER = PROJECT_ROOT / "server" / "logs"

# Database configs
DB_NAME = "telemetry.db"
DB_PATH = PROJECT_ROOT / "server" / "db" / DB_NAME

# Data Format Settings
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

# connection settings
LISTEN_TO_ALL_DEVICES = True
