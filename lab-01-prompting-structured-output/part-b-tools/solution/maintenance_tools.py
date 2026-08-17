from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable, Mapping


DATA_DIRECTORY = Path(__file__).parents[1] / "data"
ASSET_ID_PATTERN = re.compile(r"^ASSET-[0-9]{3}$")
PART_NUMBER_PATTERN = re.compile(r"^PART-[0-9]{3}$")


def _load_records(file_name: str, key: str) -> dict[str, dict[str, Any]]:
    with (DATA_DIRECTORY / file_name).open(encoding="utf-8") as data_file:
        records = json.load(data_file)
    return {record[key]: record for record in records}


def _invalid_argument(argument: str, expected_format: str) -> dict[str, Any]:
    return {
        "status": "error",
        "error": {
            "code": "invalid_argument",
            "message": f"{argument} must match {expected_format}.",
        },
    }


def get_asset(asset_id: str) -> dict[str, Any]:
    if not isinstance(asset_id, str) or not ASSET_ID_PATTERN.fullmatch(asset_id):
        return _invalid_argument("asset_id", "ASSET-###")

    asset = _load_records("assets.json", "asset_id").get(asset_id)
    if asset is None:
        return {"status": "not_found", "asset_id": asset_id}
    return {"status": "ok", "asset": asset}


def get_parts_inventory(part_number: str) -> dict[str, Any]:
    if not isinstance(part_number, str) or not PART_NUMBER_PATTERN.fullmatch(part_number):
        return _invalid_argument("part_number", "PART-###")

    inventory = _load_records("inventory.json", "part_number").get(part_number)
    if inventory is None:
        return {"status": "not_found", "part_number": part_number}
    return {"status": "ok", "inventory": inventory}


ToolFunction = Callable[..., dict[str, Any]]
TOOL_FUNCTIONS: dict[str, ToolFunction] = {
    "get_asset": get_asset,
    "get_parts_inventory": get_parts_inventory,
}


def execute_tool(tool_name: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
    tool = TOOL_FUNCTIONS.get(tool_name)
    if tool is None:
        return {
            "status": "error",
            "error": {
                "code": "unknown_tool",
                "message": f"Tool '{tool_name}' is not allowed.",
            },
        }
    if not isinstance(arguments, Mapping):
        return _invalid_argument("arguments", "a JSON object")

    try:
        return tool(**dict(arguments))
    except TypeError:
        return {
            "status": "error",
            "error": {
                "code": "invalid_arguments",
                "message": f"Arguments do not match the schema for '{tool_name}'.",
            },
        }