from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SOLUTION_DIRECTORY = (
    Path(__file__).parents[1]
    / "lab-03-search-grounding"
    / "solution"
)
SPEC = importlib.util.spec_from_file_location(
    "search_helpers", SOLUTION_DIRECTORY / "search_helpers.py"
)
assert SPEC and SPEC.loader
search_helpers = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = search_helpers
SPEC.loader.exec_module(search_helpers)

IQ_SPEC = importlib.util.spec_from_file_location(
    "foundry_iq_agent", SOLUTION_DIRECTORY / "02_foundry_iq_agent.py"
)
assert IQ_SPEC and IQ_SPEC.loader
foundry_iq_agent = importlib.util.module_from_spec(IQ_SPEC)
sys.modules[IQ_SPEC.name] = foundry_iq_agent
IQ_SPEC.loader.exec_module(foundry_iq_agent)

EXERCISE_SPEC = importlib.util.spec_from_file_location(
    "search_exercise_solution", SOLUTION_DIRECTORY / "search_exercise.py"
)
assert EXERCISE_SPEC and EXERCISE_SPEC.loader
search_exercise_solution = importlib.util.module_from_spec(EXERCISE_SPEC)
sys.modules[EXERCISE_SPEC.name] = search_exercise_solution
EXERCISE_SPEC.loader.exec_module(search_exercise_solution)

BUILD_SPEC = importlib.util.spec_from_file_location(
    "build_and_search", SOLUTION_DIRECTORY / "01_build_and_search.py"
)
assert BUILD_SPEC and BUILD_SPEC.loader
build_and_search = importlib.util.module_from_spec(BUILD_SPEC)
sys.modules[BUILD_SPEC.name] = build_and_search
BUILD_SPEC.loader.exec_module(build_and_search)

CLEANUP_SPEC = importlib.util.spec_from_file_location(
    "search_cleanup", SOLUTION_DIRECTORY / "03_cleanup.py"
)
assert CLEANUP_SPEC and CLEANUP_SPEC.loader
search_cleanup = importlib.util.module_from_spec(CLEANUP_SPEC)
sys.modules[CLEANUP_SPEC.name] = search_cleanup
CLEANUP_SPEC.loader.exec_module(search_cleanup)


class SearchSchemaTests(unittest.TestCase):
    def test_index_has_key_searchable_content_vector_and_semantic_config(self) -> None:
        index = search_helpers.build_search_index(
            "maintenance-index",
            "https://example.openai.azure.com",
            "embedding-deployment",
            "text-embedding-3-small",
            1536,
        )
        fields = {field.name: field for field in index.fields}

        self.assertTrue(fields["id"].key)
        self.assertTrue(fields["content"].searchable)
        self.assertEqual(fields["content_vector"].vector_search_dimensions, 1536)
        self.assertEqual(
            index.semantic_search.default_configuration_name,
            search_helpers.SEMANTIC_CONFIGURATION_NAME,
        )
        self.assertEqual(
            index.vector_search.vectorizers[0].parameters.resource_url,
            "https://example.openai.azure.com",
        )

    def test_embedding_results_are_attached_without_mutating_source(self) -> None:
        source = [{"id": "1", "title": "Title", "content": "Body"}]
        fake_client = SimpleNamespace(
            embeddings=SimpleNamespace(
                create=lambda **_: SimpleNamespace(
                    data=[SimpleNamespace(embedding=[0.1, 0.2, 0.3])]
                )
            )
        )

        prepared = search_helpers.add_embeddings(source, fake_client, "embedding-deployment")

        self.assertNotIn("content_vector", source[0])
        self.assertEqual(prepared[0]["content_vector"], [0.1, 0.2, 0.3])

    def test_knowledge_objects_reference_the_workshop_index(self) -> None:
        captured = {}

        class FakeIndexClient:
            def create_or_update_knowledge_source(self, knowledge_source):
                captured["source"] = knowledge_source

            def create_or_update_knowledge_base(self, knowledge_base):
                captured["base"] = knowledge_base

        foundry_iq_agent.create_knowledge_objects(
            FakeIndexClient(),
            "maintenance-index",
            "maintenance-source",
            "maintenance-base",
        )

        source_payload = captured["source"].as_dict()
        base_payload = captured["base"].as_dict()
        self.assertEqual(
            source_payload["searchIndexParameters"]["searchIndexName"],
            "maintenance-index",
        )
        self.assertEqual(
            source_payload["searchIndexParameters"]["semanticConfigurationName"],
            search_helpers.SEMANTIC_CONFIGURATION_NAME,
        )
        self.assertEqual(base_payload["knowledgeSources"][0]["name"], "maintenance-source")
        self.assertNotIn("output_mode", base_payload)


class QueryModeTests(unittest.TestCase):
    def test_completed_exercise_builds_all_three_query_modes(self) -> None:
        keyword = search_exercise_solution.build_keyword_query("seal leak", top=5)
        vector = search_exercise_solution.build_vector_query("seal leak", top=5)
        hybrid = search_exercise_solution.build_hybrid_query("seal leak", top=5)

        self.assertEqual(keyword, {"search_text": "seal leak", "top": 5})
        self.assertIsNone(vector["search_text"])
        self.assertEqual(vector["vector_queries"][0].k_nearest_neighbors, 5)
        self.assertEqual(hybrid["search_text"], "seal leak")
        self.assertEqual(hybrid["query_type"], "semantic")
        self.assertEqual(
            hybrid["semantic_configuration_name"],
            search_exercise_solution.SEMANTIC_CONFIGURATION_NAME,
        )

    def test_keyword_query_has_no_vector(self) -> None:
        arguments = search_helpers.build_query_arguments("seal leak", "keyword")

        self.assertEqual(arguments["search_text"], "seal leak")
        self.assertNotIn("vector_queries", arguments)

    def test_vector_query_has_no_lexical_text(self) -> None:
        arguments = search_helpers.build_query_arguments("seal leak", "vector")

        self.assertIsNone(arguments["search_text"])
        self.assertEqual(arguments["vector_queries"][0].fields, "content_vector")
        self.assertEqual(arguments["vector_queries"][0].k_nearest_neighbors, 3)

    def test_hybrid_query_combines_text_vector_and_semantic_ranking(self) -> None:
        arguments = search_helpers.build_query_arguments("seal leak", "hybrid")

        self.assertEqual(arguments["search_text"], "seal leak")
        self.assertEqual(arguments["vector_queries"][0].text, "seal leak")
        self.assertEqual(arguments["query_type"], "semantic")
        self.assertEqual(
            arguments["semantic_configuration_name"],
            search_helpers.SEMANTIC_CONFIGURATION_NAME,
        )

    def test_unknown_query_mode_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            search_helpers.build_query_arguments("seal leak", "magic")

    @patch("builtins.print")
    def test_keyword_results_fall_back_to_search_score(self, mock_print) -> None:
        search_helpers.print_results(
            "keyword",
            [
                {
                    "id": "DOC-1",
                    "revision": 1,
                    "title": "Pump procedure",
                    "@search.score": 2.5,
                    "@search.reranker_score": None,
                }
            ],
        )

        self.assertIn("score=2.5000", mock_print.call_args_list[-1].args[0])


class InteractiveAgentTests(unittest.TestCase):
    def test_all_mutating_scripts_reject_generic_resource_names(self) -> None:
        environment = {
            "RESOURCE_PREFIX": "opg26a-ap",
            "AZURE_SEARCH_INDEX_NAME": "opg-maintenance-documents",
            "AZURE_SEARCH_KNOWLEDGE_BASE_NAME": "opg-maintenance-knowledge",
        }
        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaisesRegex(RuntimeError, "must start with 'opg26a-ap-'"):
                build_and_search.required_participant_resource("AZURE_SEARCH_INDEX_NAME")
            with self.assertRaisesRegex(RuntimeError, "must start with 'opg26a-ap-'"):
                foundry_iq_agent.required_participant_resource(
                    "AZURE_SEARCH_KNOWLEDGE_BASE_NAME"
                )
            with self.assertRaisesRegex(RuntimeError, "must start with 'opg26a-ap-'"):
                search_cleanup.required_participant_resource(
                    "AZURE_SEARCH_KNOWLEDGE_BASE_NAME"
                )

    def test_foundry_iq_resources_require_the_participant_prefix(self) -> None:
        environment = {
            "RESOURCE_PREFIX": "opg26a-ap",
            "AZURE_SEARCH_KNOWLEDGE_BASE_NAME": "opg26a-ap-maintenance-knowledge",
        }
        with patch.dict(os.environ, environment, clear=True):
            self.assertEqual(
                foundry_iq_agent.required_participant_resource(
                    "AZURE_SEARCH_KNOWLEDGE_BASE_NAME"
                ),
                "opg26a-ap-maintenance-knowledge",
            )

            os.environ["AZURE_SEARCH_KNOWLEDGE_BASE_NAME"] = "opg-maintenance-knowledge"
            with self.assertRaisesRegex(RuntimeError, "must start with 'opg26a-ap-'"):
                foundry_iq_agent.required_participant_resource(
                    "AZURE_SEARCH_KNOWLEDGE_BASE_NAME"
                )

    def test_mcp_endpoint_uses_ga_minimal_retrieval(self) -> None:
        endpoint = foundry_iq_agent.build_mcp_endpoint(
            "https://workshop.search.windows.net/",
            "maintenance-base",
        )

        self.assertEqual(
            endpoint,
            "https://workshop.search.windows.net/knowledgebases/maintenance-base/mcp"
            "?api-version=2026-04-01",
        )

    @patch("builtins.input", return_value="Compare revision 1 and revision 3")
    def test_grounded_agent_reads_terminal_question(self, _mock_input) -> None:
        self.assertEqual(
            foundry_iq_agent.read_question(),
            "Compare revision 1 and revision 3",
        )

    @patch("builtins.input", return_value="exit")
    def test_grounded_agent_exit_stops_prompt_loop(self, _mock_input) -> None:
        self.assertIsNone(foundry_iq_agent.read_question())


if __name__ == "__main__":
    unittest.main()