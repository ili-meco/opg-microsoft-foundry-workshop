"""Lab 01 Part B starter: define strict tools and resolve Foundry function calls."""

from __future__ import annotations

import json
import os
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition, Tool
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

from maintenance_tools import execute_tool


AGENT_NAME = "opg-maintenance-tool-agent"
AGENT_INSTRUCTIONS = """You are an OPG maintenance planning assistant working with synthetic data.
Use get_asset for asset facts and get_parts_inventory for current stock facts.
Do not invent identifiers, records, quantities, or maintenance history.
Treat not_found and error tool results as missing evidence and say what could not be verified.
You have read-only tools: never claim to update a work order, reserve stock, or control equipment.
State the evidence you found and give a cautious planner recommendation.
"""
TOOL_DEFINITIONS = [
    {
        "name": "get_asset",
        "description": "Look up one maintenance asset by asset ID. Read-only.",
        "parameter_name": "asset_id",
        "pattern": "^ASSET-[0-9]{3}$",
    },
    {
        "name": "get_parts_inventory",
        "description": "Look up stock information for one part number. Read-only.",
        "parameter_name": "part_number",
        "pattern": "^PART-[0-9]{3}$",
    },
]


def build_function_tools() -> list[Tool]:
    # TODO 1: Create one FunctionTool for every TOOL_DEFINITIONS entry.
    # TODO 2: Give each tool an object schema with one required string property,
    # the supplied identifier pattern, and additionalProperties=False.
    # TODO 3: Set strict=True so Foundry constrains generated tool arguments.
    raise NotImplementedError


def resolve_function_calls(response_output: list[Any]) -> ResponseInputParam:
    outputs: ResponseInputParam = []
    for item in response_output:
        if getattr(item, "type", None) != "function_call":
            continue
        # TODO 4: Parse item.arguments as untrusted JSON. Convert malformed JSON
        # into a structured error result instead of crashing the application.
        # TODO 5: Pass the name and parsed object to the closed execute_tool dispatcher.
        # TODO 6: Append a FunctionCallOutput that preserves item.call_id and
        # serializes the result as JSON so Foundry can match output to request.
        _ = (json, FunctionCallOutput, execute_tool, item)
    return outputs


def required_environment(variable: str) -> str:
    value = os.getenv(variable, "").strip()
    if not value or value.startswith("<") or "<account>" in value:
        raise RuntimeError(f"Set {variable} in the repository .env file.")
    return value


def invoke_agent(
    project_client: AIProjectClient,
    openai_client: OpenAI,
    model_name: str,
    request: str,
    max_tool_rounds: int = 4,
) -> str:
    agent = project_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=model_name,
            instructions=AGENT_INSTRUCTIONS,
            tools=build_function_tools(),
        ),
    )
    conversation = openai_client.conversations.create()
    agent_reference = {"agent_reference": {"name": agent.name, "type": "agent_reference"}}

    try:
        response = openai_client.responses.create(
            input=request,
            conversation=conversation.id,
            extra_body=agent_reference,
        )
        for _ in range(max_tool_rounds):
            tool_outputs = resolve_function_calls(response.output)
            if not tool_outputs:
                return response.output_text
            response = openai_client.responses.create(
                input=tool_outputs,
                conversation=conversation.id,
                extra_body=agent_reference,
            )
        raise RuntimeError("Agent exceeded the allowed tool-call rounds.")
    finally:
        openai_client.conversations.delete(conversation_id=conversation.id)
        project_client.agents.delete_version(
            agent_name=agent.name,
            agent_version=agent.version,
        )


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
            answer = invoke_agent(project_client, openai_client, model_name, request)
            print(f"\nAgent response:\n{answer}")


if __name__ == "__main__":
    main()