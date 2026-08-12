"""Lab 00 starter: invoke and compare Foundry model deployments."""

from __future__ import annotations

import os
import time

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai import OpenAI


MAINTENANCE_REQUEST = (
    "Pump P-104 has increasing vibration and a small seal leak. "
    "The last inspection was 30 days ago. Recommend the immediate next action "
    "and identify any assumptions."
)
SYSTEM_INSTRUCTIONS = """You are a maintenance-assistant prototype.
Use only facts supplied in the request.
Separate observations, assumptions, and recommended next actions.
Do not claim to update a work order or control equipment.
Escalate when the available evidence is insufficient for a safe recommendation.
"""


def required_environment(variable: str) -> str:
    value = os.getenv(variable, "").strip()
    if not value or value.startswith("<") or "<account>" in value:
        raise RuntimeError(f"Set {variable} in the repository .env file.")
    return value


def request_model_response(client: OpenAI, model_name: str, request: str) -> str:
    """Return one model response for the supplied maintenance request."""
    # TODO 1: Call client.responses.create().
    # TODO 2: Pass model_name as model to select the Foundry deployment.
    # TODO 3: Pass SYSTEM_INSTRUCTIONS as instructions to define model behavior.
    # TODO 4: Pass request as input to supply the maintenance observation.
    # TODO 5: Return response.output_text so the caller can print the generated text.
    raise NotImplementedError("Complete request_model_response() using the TODOs above.")


def main() -> None:
    load_dotenv()
    endpoint = required_environment("FOUNDRY_PROJECT_ENDPOINT")
    primary_model = required_environment("FOUNDRY_MODEL_NAME")
    comparison_model = os.getenv("FOUNDRY_COMPARISON_MODEL_NAME", "").strip()
    models = [primary_model, *([comparison_model] if comparison_model else [])]

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        for model_name in models:
            started = time.perf_counter()
            output = request_model_response(openai_client, model_name, MAINTENANCE_REQUEST)
            elapsed = time.perf_counter() - started
            print(f"\n=== {model_name} ({elapsed:.2f} seconds) ===\n{output}")


if __name__ == "__main__":
    main()
