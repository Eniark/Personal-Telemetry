# NOTE: move the application-related libraries to their respective directories
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Logs configs
LOGS_FOLDER = PROJECT_ROOT / "server" / "logs"

# Database configs
DB_NAME = "telemetry.db"
DB_PATH = PROJECT_ROOT / "server" / "db" / DB_NAME

# Data Format Settings
TIMESTAMP_FORMAT = "%d-%m-%y %H:%M:%S.%f"
TIMESTAMP_MS_PRECISION = 3


# ambiguous logic:add a comment or make it explicit
if TIMESTAMP_MS_PRECISION is not None:
    TIMESTAMP_MS_PRECISION = -TIMESTAMP_MS_PRECISION
