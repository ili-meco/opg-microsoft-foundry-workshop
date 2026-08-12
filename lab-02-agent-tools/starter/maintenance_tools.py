"""Lab 02 starter: complete the read-only maintenance tools."""

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
    # TODO: validate the ID, look up one asset, and return ok/not_found/error.
    raise NotImplementedError


def get_parts_inventory(part_number: str) -> dict[str, Any]:
    # TODO: validate the part number, look up one record, and return ok/not_found/error.
    raise NotImplementedError


ToolFunction = Callable[..., dict[str, Any]]
TOOL_FUNCTIONS: dict[str, ToolFunction] = {
    "get_asset": get_asset,
    "get_parts_inventory": get_parts_inventory,
}


def execute_tool(tool_name: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
    # TODO: use the closed dispatch table and safely handle invalid arguments.
    raise NotImplementedError