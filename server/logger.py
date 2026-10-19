import logging
from shared.configs import LOGS_FOLDER
from contextvars import ContextVar
import datetime

trace_id_var = ContextVar("trace_id", default=None)

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = trace_id_var.get()
        return True

logger: logging.Logger = logging.getLogger("tracker")
logger.setLevel(logging.INFO)
logger.addFilter(TraceIdFilter())
# Console logger
console_handler:logging.StreamHandler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File logger
timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
log_filename = f"{timestamp}.log"
file_handler = logging.FileHandler(LOGS_FOLDER / log_filename, encoding='utf-8')
file_handler.setLevel(logging.INFO)

logFormatter: logging.Formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - trace_id=%(trace_id)s - %(message)s"
)

console_handler.setFormatter(logFormatter)
file_handler.setFormatter(logFormatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)