from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Logs configs
LOGS_FOLDER = PROJECT_ROOT / "logs"

# Database configs
DB_NAME = "activity.db"
DB_PATH = PROJECT_ROOT / "db" / DB_NAME
