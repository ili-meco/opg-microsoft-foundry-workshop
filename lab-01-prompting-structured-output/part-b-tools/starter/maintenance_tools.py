"""Lab 01 Part B starter: complete the read-only maintenance tools."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable, Mapping


DATA_DIRECTORY = Path(__file__).parents[1] / "data"
ASSET_ID_PATTERN = re.compile(r"^ASSET-[0-9]{3}$")
PART_NUMBER_PATTERN = re.compile(r"^PART-[0-9]{3}$")


def load_records(file_name: str, key: str) -> dict[str, dict[str, Any]]:
    with (DATA_DIRECTORY / file_name).open(encoding="utf-8") as data_file:
        records = json.load(data_file)
    return {record[key]: record for record in records}


def get_asset(asset_id: str) -> dict[str, Any]:
    # TODO 1: Reject values that do not match ASSET-### with status="error".
    # TODO 2: Load assets.json and return status="not_found" when the ID is absent.
    # TODO 3: Return only the matching asset in a status="ok" result.
    raise NotImplementedError


def get_parts_inventory(part_number: str) -> dict[str, Any]:
    # TODO 4: Reject values that do not match PART-### with status="error".
    # TODO 5: Load inventory.json and return status="not_found" when the part is absent.
    # TODO 6: Return only the matching inventory record in a status="ok" result.
    raise NotImplementedError


ToolFunction = Callable[..., dict[str, Any]]
TOOL_FUNCTIONS: dict[str, ToolFunction] = {
    "get_asset": get_asset,
    "get_parts_inventory": get_parts_inventory,
}


def execute_tool(tool_name: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
    # TODO 7: Resolve tool_name only through TOOL_FUNCTIONS; reject unknown names.
    # TODO 8: Call the selected function with the supplied arguments and convert
    # argument-shape errors into a structured status="error" result.
    raise NotImplementedError