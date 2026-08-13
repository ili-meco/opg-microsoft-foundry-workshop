from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "verify_setup.py"
SPEC = importlib.util.spec_from_file_location("verify_setup", SCRIPT_PATH)
assert SPEC and SPEC.loader
verify_setup = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verify_setup
SPEC.loader.exec_module(verify_setup)

SOLUTION_PATH = (
    Path(__file__).parents[1]
    / "lab-00-foundry-foundations"
    / "solution"
    / "foundry_model_check.py"
)
SOLUTION_SPEC = importlib.util.spec_from_file_location("foundry_model_check", SOLUTION_PATH)
assert SOLUTION_SPEC and SOLUTION_SPEC.loader
foundry_model_check = importlib.util.module_from_spec(SOLUTION_SPEC)
sys.modules[SOLUTION_SPEC.name] = foundry_model_check
SOLUTION_SPEC.loader.exec_module(foundry_model_check)


class ConfigurationChecksTests(unittest.TestCase):
    def test_missing_configuration_is_a_warning(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            results = verify_setup.configuration_checks()

        self.assertEqual([result.status for result in results], ["WARN", "WARN"])

    def test_complete_configuration_passes(self) -> None:
        environment = {
            "FOUNDRY_PROJECT_ENDPOINT": "https://example.services.ai.azure.com/api/projects/team-01",
            "FOUNDRY_MODEL_NAME": "workshop-model",
        }
        with patch.dict(os.environ, environment, clear=True):
            results = verify_setup.configuration_checks()

        self.assertEqual([result.status for result in results], ["PASS", "PASS"])

    def test_embedded_placeholder_is_not_configured(self) -> None:
        environment = {
            "FOUNDRY_PROJECT_ENDPOINT": (
                "https://<account>.services.ai.azure.com/api/projects/<project>"
            ),
            "FOUNDRY_MODEL_NAME": "<deployment-name>",
        }
        with patch.dict(os.environ, environment, clear=True):
            results = verify_setup.configuration_checks()

        self.assertEqual([result.status for result in results], ["WARN", "WARN"])


class ModuleChecksTests(unittest.TestCase):
    def test_missing_parent_package_is_reported_as_unavailable(self) -> None:
        self.assertFalse(verify_setup.module_available("package_that_does_not_exist.child"))


class ModelRequestTests(unittest.TestCase):
    def test_request_uses_deployment_instructions_and_input(self) -> None:
        captured: dict[str, str] = {}

        class FakeResponses:
            def create(self, **kwargs: str) -> SimpleNamespace:
                captured.update(kwargs)
                return SimpleNamespace(output_text="assessment")

        client = SimpleNamespace(responses=FakeResponses())
        output = foundry_model_check.request_model_response(
            client,
            "primary-deployment",
            "synthetic maintenance request",
        )

        self.assertEqual(output, "assessment")
        self.assertEqual(captured["model"], "primary-deployment")
        self.assertEqual(captured["instructions"], foundry_model_check.SYSTEM_INSTRUCTIONS)
        self.assertEqual(captured["input"], "synthetic maintenance request")


if __name__ == "__main__":
    unittest.main()
