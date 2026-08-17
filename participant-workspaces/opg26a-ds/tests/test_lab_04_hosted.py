from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, call, patch


HOSTED_FILE = (
    Path(__file__).parents[1]
    / "lab-04-multi-agent-safety"
    / "part-b-hosted-agent"
    / "main.py"
)


def load_hosted_module():
    hosting = ModuleType("agent_framework_foundry_hosting")
    hosting.ResponsesHostServer = Mock  # type: ignore[attr-defined]
    with patch.dict(sys.modules, {"agent_framework_foundry_hosting": hosting}):
        spec = importlib.util.spec_from_file_location("lab04_hosted_main", HOSTED_FILE)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


hosted_main = load_hosted_module()


class HostedWorkflowTests(unittest.TestCase):
    def test_workflow_preserves_full_context_and_reviewer_only_output(self) -> None:
        client = object()
        agents = [object(), object(), object()]
        executors = [object(), object(), object()]
        workflow_agent = object()
        built_workflow = Mock()
        built_workflow.as_agent.return_value = workflow_agent
        builder = Mock()
        builder.add_edge.return_value = builder
        builder.build.return_value = built_workflow

        environment = {
            "FOUNDRY_PROJECT_ENDPOINT": (
                "https://example.services.ai.azure.com/api/projects/team-01"
            ),
            "AZURE_AI_MODEL_DEPLOYMENT_NAME": "gpt-5.4-mini",
        }
        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(hosted_main, "DefaultAzureCredential") as credential_type,
            patch.object(
                hosted_main,
                "FoundryChatClient",
                return_value=client,
            ) as client_type,
            patch.object(hosted_main, "Agent", side_effect=agents) as agent_type,
            patch.object(
                hosted_main,
                "AgentExecutor",
                side_effect=executors,
            ) as executor_type,
            patch.object(
                hosted_main,
                "WorkflowBuilder",
                return_value=builder,
            ) as builder_type,
        ):
            result = hosted_main.build_workflow_agent()

        self.assertIs(result, workflow_agent)
        client_type.assert_called_once_with(
            project_endpoint=environment["FOUNDRY_PROJECT_ENDPOINT"],
            model=environment["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            credential=credential_type.return_value,
        )
        self.assertEqual(
            executor_type.call_args_list,
            [
                call(agents[0], context_mode="full"),
                call(agents[1], context_mode="full"),
                call(agents[2], context_mode="full"),
            ],
        )
        self.assertEqual(
            agent_type.call_args_list[0].kwargs["tools"],
            [
                hosted_main.get_asset,
                hosted_main.get_parts_inventory,
                hosted_main.search_maintenance_knowledge,
            ],
        )
        self.assertIn(
            "ordinary conversational maintenance questions",
            agent_type.call_args_list[0].kwargs["instructions"],
        )
        builder_type.assert_called_once_with(
            start_executor=executors[0],
            output_executors=[executors[2]],
        )
        self.assertEqual(
            builder.add_edge.call_args_list,
            [call(executors[0], executors[1]), call(executors[1], executors[2])],
        )
        built_workflow.as_agent.assert_called_once_with(
            name="opg_maintenance_safety_workflow"
        )

    def test_host_starts_without_owning_the_human_decision(self) -> None:
        workflow_agent = object()
        server = Mock()

        with (
            patch.object(hosted_main, "load_dotenv") as load_dotenv,
            patch.object(
                hosted_main,
                "build_workflow_agent",
                return_value=workflow_agent,
            ),
            patch.object(
                hosted_main,
                "ResponsesHostServer",
                return_value=server,
            ) as server_type,
        ):
            hosted_main.main()

        load_dotenv.assert_called_once_with()
        server_type.assert_called_once_with(workflow_agent)
        server.run.assert_called_once_with()
        source = HOSTED_FILE.read_text(encoding="utf-8")
        self.assertNotIn("input(", source)
        self.assertNotIn("record_human_decision", source)


class HostedKnowledgeToolTests(unittest.TestCase):
    def test_asset_and_inventory_tools_return_grounded_records(self) -> None:
        asset_result = hosted_main.get_asset("asset-104")
        inventory_result = hosted_main.get_parts_inventory("part-310")

        self.assertEqual(asset_result["status"], "ok")
        self.assertEqual(
            asset_result["asset"]["installed_part_numbers"],
            ["PART-200", "PART-310"],
        )
        self.assertEqual(inventory_result["status"], "ok")
        self.assertEqual(inventory_result["inventory"]["stock_status"], "low_stock")

    def test_unknown_and_malformed_identifiers_fail_safely(self) -> None:
        self.assertEqual(hosted_main.get_asset("ASSET-999")["status"], "not_found")
        self.assertEqual(hosted_main.get_asset("../../asset.json")["status"], "error")
        self.assertEqual(
            hosted_main.get_parts_inventory("PART-999")["status"],
            "not_found",
        )

    def test_knowledge_search_is_scoped_to_the_asset_type(self) -> None:
        results = hosted_main.search_maintenance_knowledge(
            "vibration seal leakage condition assessment",
            "centrifugal_pump",
        )

        self.assertTrue(any(result["revision"] == "R3" for result in results))
        self.assertTrue(
            all(
                result["asset_type"] in {"all", "centrifugal_pump"}
                for result in results
            )
        )
        self.assertFalse(
            any(result["asset_type"] == "rotary_screw_compressor" for result in results)
        )


if __name__ == "__main__":
    unittest.main()