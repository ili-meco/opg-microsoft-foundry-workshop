from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


TOOLS_PATH = (
    Path(__file__).parents[1]
    / "lab-02-agent-tools"
    / "solution"
    / "maintenance_tools.py"
)
SPEC = importlib.util.spec_from_file_location("maintenance_tools", TOOLS_PATH)
assert SPEC and SPEC.loader
maintenance_tools = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = maintenance_tools
SPEC.loader.exec_module(maintenance_tools)


class MaintenanceToolsTests(unittest.TestCase):
    def test_asset_lookup_returns_master_data(self) -> None:
        result = maintenance_tools.get_asset("ASSET-104")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["asset"]["operating_status"], "maintenance_required")
        self.assertEqual(result["asset"]["installed_part_numbers"], ["PART-200", "PART-310"])

    def test_inventory_lookup_preserves_low_stock_signal(self) -> None:
        result = maintenance_tools.get_parts_inventory("PART-310")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["inventory"]["stock_status"], "low_stock")
        self.assertEqual(result["inventory"]["quantity_on_hand"], 1)

    def test_well_formed_unknown_identifier_returns_not_found(self) -> None:
        result = maintenance_tools.get_asset("ASSET-999")

        self.assertEqual(result, {"status": "not_found", "asset_id": "ASSET-999"})

    def test_malformed_identifier_returns_safe_error(self) -> None:
        result = maintenance_tools.get_asset("../../assets.json")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["code"], "invalid_argument")

    def test_dispatch_rejects_unknown_tools(self) -> None:
        result = maintenance_tools.execute_tool("delete_asset", {"asset_id": "ASSET-104"})

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["code"], "unknown_tool")

    def test_tool_schemas_are_strict(self) -> None:
        for definition in maintenance_tools.TOOL_DEFINITIONS:
            self.assertFalse(definition["parameters"]["additionalProperties"])
            self.assertTrue(definition["parameters"]["required"])


if __name__ == "__main__":
    unittest.main()