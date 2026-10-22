@echo off

start "Server" cmd /k "call telemetryEnv/Scripts/activate && python -m server.api.main"
start "Windows Agent" cmd /k "call telemetryEnv/Scripts/activate && python -m agents.windows.main"
start "UI" cmd /k "call telemetryEnv/Scripts/activate && python -m server.event_classifier.frontend.screen"
start "Database" cmd /k "sqlite3 server/db/telemetry.db"

exit