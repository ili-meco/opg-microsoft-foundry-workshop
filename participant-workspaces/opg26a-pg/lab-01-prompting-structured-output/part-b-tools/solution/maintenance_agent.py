"""Lab 01 Part B solution: give a Foundry agent deterministic maintenance tools."""

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

from maintenance_tools import TOOL_DEFINITIONS, execute_tool


AGENT_NAME = "opg-maintenance-tool-agent"
AGENT_INSTRUCTIONS = """You are an OPG maintenance planning assistant working with synthetic data.
Use get_asset for asset facts and get_parts_inventory for current stock facts.
Do not invent identifiers, records, quantities, or maintenance history.
Treat not_found and error tool results as missing evidence and say what could not be verified.
You have read-only tools: never claim to update a work order, reserve stock, or control equipment.
State the evidence you found and give a cautious planner recommendation.
"""


def required_environment(variable: str) -> str:
    value = os.getenv(variable, "").strip()
    if not value or value.startswith("<") or "<account>" in value:
        raise RuntimeError(f"Set {variable} in the repository .env file.")
    return value


def build_function_tools() -> list[Tool]:
    return [
        FunctionTool(
            name=definition["name"],
            description=definition["description"],
            parameters=definition["parameters"],
            strict=True,
        )
        for definition in TOOL_DEFINITIONS
    ]


def resolve_function_calls(response_output: list[Any]) -> ResponseInputParam:
    tool_outputs: ResponseInputParam = []
    for item in response_output:
        if getattr(item, "type", None) != "function_call":
            continue

        try:
            arguments = json.loads(item.arguments)
        except (json.JSONDecodeError, TypeError):
            result = {
                "status": "error",
                "error": {
                    "code": "invalid_json",
                    "message": "The tool arguments were not valid JSON.",
                },
            }
        else:
            result = execute_tool(item.name, arguments)

        print(f"Tool call: {item.name}({item.arguments}) -> {result['status']}")
        tool_outputs.append(
            FunctionCallOutput(
                type="function_call_output",
                call_id=item.call_id,
                output=json.dumps(result),
            )
        )
    return tool_outputs


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