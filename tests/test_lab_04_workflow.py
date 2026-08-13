from __future__ import annotations

import asyncio
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


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

    def test_foundry_token_provider_uses_foundry_data_plane_scope(self) -> None:
        credential = object()
        sync_provider = unittest.mock.Mock(return_value="foundry-token")

        with patch.object(
            safety_workflow,
            "get_bearer_token_provider",
            return_value=sync_provider,
        ) as mock_get_provider:
            provider = safety_workflow.foundry_token_provider(credential)
            token = asyncio.run(provider())

        self.assertEqual(token, "foundry-token")
        sync_provider.assert_called_once_with()
        mock_get_provider.assert_called_once_with(
            credential,
            "https://ai.azure.com/.default",
        )

    def test_foundry_chat_client_uses_openai_compatible_auth_surface(self) -> None:
        credential = object()
        provider = object()
        client = object()

        with (
            patch.object(
                safety_workflow,
                "foundry_token_provider",
                return_value=provider,
            ),
            patch.object(
                safety_workflow,
                "OpenAIChatClient",
                return_value=client,
            ) as mock_client,
        ):
            result = safety_workflow.build_foundry_chat_client(
                "https://example.services.ai.azure.com/api/projects/team-01",
                "gpt-4.1-mini",
                credential,
            )

        self.assertIs(result, client)
        mock_client.assert_called_once_with(
            model="gpt-4.1-mini",
            api_key=provider,
            base_url=(
                "https://example.services.ai.azure.com/api/projects/team-01/openai/v1/"
            ),
        )

    def test_human_input_is_closed_to_two_decisions(self) -> None:
        self.assertEqual(safety_workflow.parse_human_decision(" A "), "approve")
        self.assertEqual(safety_workflow.parse_human_decision("reject"), "reject")
        with self.assertRaises(ValueError):
            safety_workflow.parse_human_decision("execute")

    def test_reviewer_instructions_require_exact_json_and_human_decision(self) -> None:
        instructions = safety_workflow.REVIEWER_INSTRUCTIONS

        self.assertIn("Return only one JSON object", instructions)
        self.assertIn('"ready_for_human": true | false', instructions)
        self.assertIn('"requires_human_decision": true', instructions)
        self.assertIn('"action_authority": "none"', instructions)
        self.assertIn("Never wrap the JSON in markdown", instructions)

    def test_workflow_defines_three_distinct_agent_roles(self) -> None:
        self.assertIn("evidence analyst", safety_workflow.EVIDENCE_ANALYST_INSTRUCTIONS)
        self.assertIn("maintenance planner", safety_workflow.PLANNER_INSTRUCTIONS)
        self.assertIn("safety reviewer", safety_workflow.REVIEWER_INSTRUCTIONS)
        self.assertIn("PLANNER_DRAFT", safety_workflow.PLANNER_INSTRUCTIONS)
        self.assertIn("PLANNER_DRAFT", safety_workflow.REVIEWER_INSTRUCTIONS)
        self.assertIn("[Source: title, revision]", safety_workflow.PLANNER_INSTRUCTIONS)


if __name__ == "__main__":
    unittest.main()