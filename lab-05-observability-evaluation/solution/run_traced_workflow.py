"""Run the Lab 04 MAF workflow with OpenTelemetry configured first."""

from __future__ import annotations

import asyncio
import json
import socket
import sys
from pathlib import Path

from dotenv import load_dotenv

from tracing_setup import configure_workshop_tracing


def trace_receiver_is_running(
    host: str = "localhost",
    port: int = 4317,
    timeout_seconds: float = 1.0,
) -> bool:
    """Return whether the Foundry Toolkit OTLP receiver is accepting traces."""
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except OSError:
        return False


async def main() -> None:
    load_dotenv()
    if not trace_receiver_is_running():
        raise SystemExit(
            "Foundry Toolkit tracing is not listening on localhost:4317. "
            "Press Ctrl+Shift+P, run 'Foundry Toolkit: Open Tracing', wait for "
            "the tracing view to load, and then run this command again."
        )
    configure_workshop_tracing(capture_sensitive_data=False)

    repository_root = Path(__file__).parents[2]
    lab04_solution = repository_root / "lab-04-multi-agent-safety" / "solution"
    sys.path.insert(0, str(lab04_solution))
    from safety_workflow import run_safety_workflow

    package_path = (
        repository_root
        / "lab-04-multi-agent-safety"
        / "data"
        / "assessment_package.json"
    )
    assessment_package = json.loads(package_path.read_text(encoding="utf-8"))
    review_packet = await run_safety_workflow(assessment_package)
    print(review_packet.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())