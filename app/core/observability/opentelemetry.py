import os
import base64
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def configure_tracing(service_name: str, environment: str) -> None:
    try:
        endpoint = os.getenv("OTLP_TRACES_ENDPOINT")
        user = os.getenv("GRAFANA_OTLP_USER")
        token = os.getenv("GRAFANA_OTLP_TOKEN")
        if not endpoint or not user or not token:
            return
        b64 = base64.b64encode(f"{user}:{token}".encode()).decode()
        resource = Resource.create({
            "service.name": service_name,
            "deployment.environment": environment,
        })
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
        if endpoint.endswith("/otlp"):
            endpoint = endpoint.rstrip("/") + "/v1/traces"
        exporter = OTLPSpanExporter(endpoint=endpoint, headers={"Authorization": f"Basic {b64}"})
        provider.add_span_processor(BatchSpanProcessor(exporter))
    except Exception:
        return

