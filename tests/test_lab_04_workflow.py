from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOLUTION_DIRECTORY = Path(__file__).parents[1] / "lab-04-multi-agent-safety" / "solution"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


load_module("approval_gate", SOLUTION_DIRECTORY / "approval_gate.py")
safety_workflow = load_module("safety_workflow", SOLUTION_DIRECTORY / "safety_workflow.py")


class SafetyWorkflowTests(unittest.TestCase):
    def test_foundry_project_endpoint_maps_to_openai_v1(self) -> None:
        self.assertEqual(
            safety_workflow.foundry_openai_base_url(
                "https://example.services.ai.azure.com/api/projects/team-01/"
            ),
            "https://example.services.ai.azure.com/api/projects/team-01/openai/v1/",
        )

    def test_human_input_is_closed_to_two_decisions(self) -> None:
        self.assertEqual(safety_workflow.parse_human_decision(" A "), "approve")
        self.assertEqual(safety_workflow.parse_human_decision("reject"), "reject")
        with self.assertRaises(ValueError):
            safety_workflow.parse_human_decision("execute")

    def test_reviewer_instructions_require_exact_json_and_human_approval(self) -> None:
        instructions = safety_workflow.REVIEWER_INSTRUCTIONS

        self.assertIn("Return only one JSON object", instructions)
        self.assertIn('"requires_human_approval": true', instructions)
        self.assertIn("Never wrap the JSON in markdown", instructions)


if __name__ == "__main__":
    unittest.main()