"""Run the Lab 01 baseline and structured-output comparison."""

from __future__ import annotations

import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from maintenance_assessment import ASSESSMENT_INSTRUCTIONS, request_structured_assessment


SAMPLE_REQUEST = (
    "Asset ASSET-104 has increasing vibration and a small seal leak. "
    "The last inspection was 30 days ago. Tell me what the planner should do next."
)


def required_environment(variable: str) -> str:
    value = os.getenv(variable, "").strip()
    if not value or value.startswith("<") or "<account>" in value:
        raise RuntimeError(f"Set {variable} in the repository .env file.")
    return value


def main() -> None:
    load_dotenv()
    endpoint = required_environment("FOUNDRY_PROJECT_ENDPOINT")
    model_name = required_environment("FOUNDRY_MODEL_NAME")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        baseline = openai_client.responses.create(model=model_name, input=SAMPLE_REQUEST)
        assessment = request_structured_assessment(
            openai_client,
            model_name,
            SAMPLE_REQUEST,
        )

    print("\n=== Baseline response ===")
    print(baseline.output_text)
    print("\n=== Structured response ===")
    print(assessment.model_dump_json(indent=2))
    print("\n=== Instructions used ===")
    print(ASSESSMENT_INSTRUCTIONS.strip())


if __name__ == "__main__":
    main()