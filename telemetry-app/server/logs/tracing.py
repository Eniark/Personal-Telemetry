
from pathlib import Path

from opentelemetry import trace
from opentelemetry.exporter.otlp.json.file import FileSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from shared.configs import TRACES_FOLDER, LOGS_FILE_NAME

TRACES_FOLDER.mkdir(parents=True, exist_ok=True)
TRACE_FILE = TRACES_FOLDER / Path(f"{LOGS_FILE_NAME}.jsonl")

provider = TracerProvider(
    resource=Resource.create({
        "service.name": "personal-telemetry-api"
    })
)

exporter = FileSpanExporter(str(TRACE_FILE))
provider.add_span_processor(BatchSpanProcessor(exporter))

trace.set_tracer_provider(provider)
