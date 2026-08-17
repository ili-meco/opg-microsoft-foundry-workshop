from __future__ import annotations

import importlib.util
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
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
        self.assertTrue(all(result.fix for result in results))

    def test_lab_03_resource_names_must_match_the_participant_prefix(self) -> None:
        environment = {
            "RESOURCE_PREFIX": "opg26a-ap",
            "AZURE_SEARCH_INDEX_NAME": "opg26a-ap-maintenance-documents",
            "AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME": "opg26a-ap-maintenance-source",
            "AZURE_SEARCH_KNOWLEDGE_BASE_NAME": "opg-maintenance-knowledge",
            "FOUNDRY_IQ_CONNECTION_NAME": "opg26a-ap-maintenance-iq",
            "FOUNDRY_GROUNDED_AGENT_NAME": "opg26a-ap-grounded-maintenance-agent",
        }
        with patch.dict(os.environ, environment, clear=True):
            result = verify_setup.participant_resource_name_check()

        self.assertEqual(result.status, "WARN")
        self.assertIn("AZURE_SEARCH_KNOWLEDGE_BASE_NAME", result.detail)
        self.assertIn("opg26a-ap-maintenance-knowledge", result.fix or "")

    def test_lab_03_resource_names_pass_with_the_participant_prefix(self) -> None:
        environment = {
            "RESOURCE_PREFIX": "opg26a-ap",
            "AZURE_SEARCH_INDEX_NAME": "opg26a-ap-maintenance-documents",
            "AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME": "opg26a-ap-maintenance-source",
            "AZURE_SEARCH_KNOWLEDGE_BASE_NAME": "opg26a-ap-maintenance-knowledge",
            "FOUNDRY_IQ_CONNECTION_NAME": "opg26a-ap-maintenance-iq",
            "FOUNDRY_GROUNDED_AGENT_NAME": "opg26a-ap-grounded-maintenance-agent",
        }
        with patch.dict(os.environ, environment, clear=True):
            result = verify_setup.participant_resource_name_check()

        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.detail, "all start with opg26a-ap-")

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

    def test_every_local_failure_has_a_fix(self) -> None:
        with (
            patch.object(verify_setup, "MINIMUM_PYTHON", (99, 0)),
            patch.object(verify_setup.sys, "prefix", "same-prefix"),
            patch.object(verify_setup.sys, "base_prefix", "same-prefix"),
            patch.object(verify_setup.shutil, "which", return_value=None),
            patch.object(verify_setup, "module_available", return_value=False),
        ):
            results = verify_setup.local_checks()

        self.assertTrue(all(result.status != "PASS" for result in results))
        self.assertTrue(all(result.fix for result in results))


class RemediationCoverageTests(unittest.TestCase):
    def test_every_environment_warning_has_a_fix(self) -> None:
        variables = verify_setup.REQUIRED_ENVIRONMENT + verify_setup.LAB_03_ENVIRONMENT
        with patch.dict(os.environ, {}, clear=True):
            results = verify_setup.configuration_checks(variables)

        self.assertTrue(all(result.status == "WARN" for result in results))
        self.assertTrue(all(result.fix for result in results))

    def test_azure_sign_in_failure_has_a_fix(self) -> None:
        with patch.object(
            verify_setup.subprocess,
            "run",
            side_effect=FileNotFoundError("az not found"),
        ):
            result = verify_setup.azure_login_check()

        self.assertEqual(result.status, "FAIL")
        self.assertIn("az login", result.fix or "")


class ResultOutputTests(unittest.TestCase):
    def test_non_passing_check_prints_its_fix(self) -> None:
        results = [
            verify_setup.CheckResult(
                "Azure CLI",
                "FAIL",
                "not found on PATH",
                "Install Azure CLI, then restart the terminal.",
            )
        ]
        output = io.StringIO()

        with redirect_stdout(output):
            verify_setup.print_results(results)

        self.assertEqual(
            output.getvalue().splitlines(),
            [
                "[FAIL] Azure CLI: not found on PATH",
                "       [FIX] Install Azure CLI, then restart the terminal.",
            ],
        )

    def test_warning_prints_fix_but_pass_does_not(self) -> None:
        results = [
            verify_setup.CheckResult("Python", "PASS", "3.12.10", "Reinstall Python."),
            verify_setup.CheckResult(
                "FOUNDRY_MODEL_NAME",
                "WARN",
                "not configured yet",
                "Set FOUNDRY_MODEL_NAME in .env.",
            ),
        ]
        output = io.StringIO()

        with redirect_stdout(output):
            verify_setup.print_results(results)

        self.assertEqual(output.getvalue().count("[FIX]"), 1)
        self.assertNotIn("Reinstall Python", output.getvalue())
        self.assertIn("Set FOUNDRY_MODEL_NAME in .env.", output.getvalue())


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
