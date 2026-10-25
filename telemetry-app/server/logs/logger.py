import logging
from shared.configs import EVENTS_FOLDER, LOGS_FILE_NAME


from opentelemetry import trace
import logging

# This class provides additional info about the trace_id and span_id
class TraceFilter(logging.Filter):
    def filter(self, record):
        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            record.trace_id = format(span_context.trace_id, "032x")
            record.span_id = format(span_context.span_id, "016x")
        else:
            record.trace_id = "-"
            record.span_id = "-"

        return True

logger: logging.Logger = logging.getLogger("tracker")
logger.setLevel(logging.INFO)
logger.addFilter(TraceFilter())
# Console logger
console_handler:logging.StreamHandler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File logger
EVENTS_FOLDER.mkdir(parents=True, exist_ok=True)
file_handler = logging.FileHandler(EVENTS_FOLDER / f"{LOGS_FILE_NAME}.log", encoding='utf-8')
file_handler.setLevel(logging.INFO)

logFormatter: logging.Formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - trace_id=%(trace_id)s - span_id=%(span_id)s - %(message)s"
)

console_handler.setFormatter(logFormatter)
file_handler.setFormatter(logFormatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)