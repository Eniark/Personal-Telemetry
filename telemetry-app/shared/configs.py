from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Date Format Settings
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGS_FILENAME_FORMAT = TIMESTAMP_FORMAT.split(" ")[0]

# Logs configs
LOGS_FOLDER = PROJECT_ROOT / "server" / "logs"
EVENTS_FOLDER = LOGS_FOLDER / "events"
TRACES_FOLDER = LOGS_FOLDER / "traces" 
LOGS_FILE_NAME = datetime.now().strftime(LOGS_FILENAME_FORMAT)

# Database configs
DB_NAME = "telemetry.db"
DB_PATH = PROJECT_ROOT / "server" / "db" / DB_NAME



# Connection settings
LISTEN_TO_ALL_DEVICES = True
