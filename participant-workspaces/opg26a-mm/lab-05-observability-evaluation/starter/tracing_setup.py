"""Lab 05 starter: configure MAF OpenTelemetry instrumentation."""

from __future__ import annotations

from agent_framework.observability import configure_otel_providers


def configure_workshop_tracing(
    *,
    port: int = 4317,
    capture_sensitive_data: bool = False,
) -> None:
    # TODO: call configure_otel_providers with the VS Code extension port and
    # the sensitive-data choice. Keep sensitive capture off unless using only
    # approved synthetic workshop data.
    raise NotImplementedError("Configure the OpenTelemetry providers.")