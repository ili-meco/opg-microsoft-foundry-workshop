"""Run the Lab 04 MAF workflow with OpenTelemetry configured first."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from tracing_setup import configure_workshop_tracing


async def main() -> None:
    load_dotenv()
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
    record = await run_safety_workflow(assessment_package)
    print(record.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())