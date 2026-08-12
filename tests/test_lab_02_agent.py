from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SOLUTION_DIRECTORY = (
    Path(__file__).parents[1]
    / "lab-02-agent-tools"
    / "solution"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


load_module("maintenance_tools", SOLUTION_DIRECTORY / "maintenance_tools.py")
maintenance_agent = load_module("maintenance_agent", SOLUTION_DIRECTORY / "maintenance_agent.py")


class FunctionCallResolutionTests(unittest.TestCase):
    def test_resolves_every_function_call_in_one_response(self) -> None:
        output = [
            SimpleNamespace(
                type="function_call",
                name="get_asset",
                arguments='{"asset_id":"ASSET-104"}',
                call_id="call-asset",
            ),
            SimpleNamespace(
                type="function_call",
                name="get_parts_inventory",
                arguments='{"part_number":"PART-310"}',
                call_id="call-part",
            ),
        ]

        results = maintenance_agent.resolve_function_calls(output)

        self.assertEqual([result["call_id"] for result in results], ["call-asset", "call-part"])
        self.assertEqual(json.loads(results[0]["output"])["status"], "ok")
        self.assertEqual(json.loads(results[1]["output"])["inventory"]["stock_status"], "low_stock")

    def test_invalid_json_becomes_tool_output_instead_of_crashing(self) -> None:
        output = [
            SimpleNamespace(
                type="function_call",
                name="get_asset",
                arguments="not-json",
                call_id="call-invalid",
            )
        ]

        results = maintenance_agent.resolve_function_calls(output)

        result = json.loads(results[0]["output"])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["code"], "invalid_json")

    def test_non_function_output_is_ignored(self) -> None:
        output = [SimpleNamespace(type="message", content="done")]

        self.assertEqual(maintenance_agent.resolve_function_calls(output), [])

    def test_sdk_tools_use_strict_schemas(self) -> None:
        tools = maintenance_agent.build_function_tools()

        self.assertEqual([tool.name for tool in tools], ["get_asset", "get_parts_inventory"])
        self.assertTrue(all(tool.strict for tool in tools))
        self.assertTrue(all(tool.parameters["additionalProperties"] is False for tool in tools))

    def test_terminal_input_retries_blank_and_accepts_exit(self) -> None:
        with (
            patch("builtins.input", side_effect=[" ", "Check ASSET-104."]),
            patch("builtins.print"),
        ):
            self.assertEqual(maintenance_agent.read_request(), "Check ASSET-104.")

        with patch("builtins.input", return_value="exit"):
            self.assertIsNone(maintenance_agent.read_request())


if __name__ == "__main__":
    unittest.main()