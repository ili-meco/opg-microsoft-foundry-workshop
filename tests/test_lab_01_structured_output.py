from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SOLUTION_FILE = (
    Path(__file__).parents[1]
    / "lab-01-prompting-structured-output"
    / "solution"
    / "maintenance_assessment.py"
)
SOLUTION_RUNNER_FILE = SOLUTION_FILE.with_name("run_assessment.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


maintenance_assessment = load_module("maintenance_assessment", SOLUTION_FILE)
run_assessment = load_module("lab_01_run_assessment", SOLUTION_RUNNER_FILE)


class FakeResponses:
    def __init__(self, output_parsed):
        self.output_parsed = output_parsed
        self.arguments = None

    def parse(self, **kwargs):
        self.arguments = kwargs
        return SimpleNamespace(output_parsed=self.output_parsed)


class StructuredAssessmentTests(unittest.TestCase):
    def test_contract_is_closed_and_preserves_authorization_boundary(self) -> None:
        schema = maintenance_assessment.MaintenanceAssessment.model_json_schema()

        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            schema["properties"]["authorization"]["const"],
            "recommendation_only",
        )
        self.assertEqual(
            set(schema["properties"]["risk_level"]["enum"]),
            {"low", "medium", "high", "critical", "unknown"},
        )

    def test_requests_and_returns_a_parsed_assessment(self) -> None:
        expected = maintenance_assessment.MaintenanceAssessment(
            asset_id="ASSET-104",
            summary="Inspection required before planning work.",
            observations=["Increasing vibration was reported."],
            assumptions=[],
            risk_level="high",
            recommended_actions=["Escalate to the maintenance planner."],
            missing_evidence=["Current vibration measurement"],
            requires_escalation=True,
            authorization="recommendation_only",
        )
        responses = FakeResponses(expected)
        client = SimpleNamespace(responses=responses)

        actual = maintenance_assessment.request_structured_assessment(
            client,
            "gpt-4.1-mini",
            "Assess ASSET-104.",
        )

        self.assertIs(actual, expected)
        self.assertEqual(responses.arguments["model"], "gpt-4.1-mini")
        self.assertEqual(responses.arguments["input"], "Assess ASSET-104.")
        self.assertIs(
            responses.arguments["text_format"],
            maintenance_assessment.MaintenanceAssessment,
        )

    def test_missing_parsed_output_fails_closed(self) -> None:
        client = SimpleNamespace(responses=FakeResponses(None))

        with self.assertRaisesRegex(RuntimeError, "did not return"):
            maintenance_assessment.request_structured_assessment(
                client,
                "gpt-4.1-mini",
                "Assess an asset.",
            )

    def test_terminal_input_retries_blank_and_accepts_exit(self) -> None:
        with (
            patch("builtins.input", side_effect=[" ", "Assess ASSET-104."]),
            patch("builtins.print"),
        ):
            self.assertEqual(run_assessment.read_request(), "Assess ASSET-104.")

        with patch("builtins.input", return_value="exit"):
            self.assertIsNone(run_assessment.read_request())


if __name__ == "__main__":
    unittest.main()