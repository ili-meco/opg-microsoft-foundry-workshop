"""Configure Microsoft Agent Framework tracing for Foundry Toolkit."""

from __future__ import annotations

from agent_framework.observability import configure_otel_providers


def configure_workshop_tracing(
    *,
    port: int = 4317,
    capture_sensitive_data: bool = False,
) -> None:
    """Enable MAF's built-in OpenTelemetry instrumentation."""
    configure_otel_providers(
        vs_code_extension_port=port,
        enable_sensitive_data=capture_sensitive_data,
    )