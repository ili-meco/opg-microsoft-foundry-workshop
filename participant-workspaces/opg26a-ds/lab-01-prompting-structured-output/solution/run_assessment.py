"""Run the Lab 01 baseline and structured-output comparison."""

from __future__ import annotations

import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from maintenance_assessment import ASSESSMENT_INSTRUCTIONS, request_structured_assessment


def required_environment(variable: str) -> str:
    value = os.getenv(variable, "").strip()
    if not value or value.startswith("<") or "<account>" in value:
        raise RuntimeError(f"Set {variable} in the repository .env file.")
    return value


def read_request() -> str | None:
    while True:
        try:
            request = input("\nMaintenance request (or type 'exit'): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if request.lower() in {"exit", "quit"}:
            return None
        if request:
            return request
        print("Enter a maintenance request, or type 'exit' to stop.")


def main() -> None:
    load_dotenv()
    endpoint = required_environment("FOUNDRY_PROJECT_ENDPOINT")
    model_name = required_environment("FOUNDRY_MODEL_NAME")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        print("Enter one maintenance scenario at a time. Each request is independent.")
        while request := read_request():
            baseline = openai_client.responses.create(model=model_name, input=request)
            assessment = request_structured_assessment(
                openai_client,
                model_name,
                request,
            )

            print("\n=== Baseline response ===")
            print(baseline.output_text)
            print("\n=== Structured response ===")
            print(assessment.model_dump_json(indent=2))
            print("\n=== Instructions used ===")
            print(ASSESSMENT_INSTRUCTIONS.strip())


if __name__ == "__main__":
    main()