"""Lab 02 starter: define strict tools and resolve Foundry function calls."""

from __future__ import annotations

import json
from typing import Any

from azure.ai.projects.models import FunctionTool, Tool
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

from maintenance_tools import execute_tool


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
    # TODO: return FunctionTool objects with strict object schemas.
    raise NotImplementedError


def resolve_function_calls(response_output: list[Any]) -> ResponseInputParam:
    outputs: ResponseInputParam = []
    for item in response_output:
        if getattr(item, "type", None) != "function_call":
            continue
        # TODO: parse arguments, execute the tool, and append FunctionCallOutput.
        _ = (json, FunctionCallOutput, execute_tool, item)
    return outputs


if __name__ == "__main__":
    print("Complete the TODOs, then compare with solution/maintenance_agent.py.")