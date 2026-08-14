from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "create_participant_workspaces.py"
SPEC = importlib.util.spec_from_file_location("create_participant_workspaces", SCRIPT_PATH)
assert SPEC and SPEC.loader
workspace_generator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = workspace_generator
SPEC.loader.exec_module(workspace_generator)


class ParticipantWorkspaceTests(unittest.TestCase):
    def test_packaged_copy_uses_filtered_filesystem_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            packaged_root = Path(temporary_directory) / "opg26a-mt"
            lab_file = packaged_root / "lab-03-search-grounding" / "README.md"
            lab_file.parent.mkdir(parents=True)
            lab_file.write_text("lab", encoding="utf-8")
            (packaged_root / "AGENTS.md").write_text("internal", encoding="utf-8")
            (packaged_root / ".env").write_text("local", encoding="utf-8")
            nested_file = (
                packaged_root
                / "participant-workspaces"
                / "opg26a-rj"
                / "README.md"
            )
            nested_file.parent.mkdir(parents=True)
            nested_file.write_text("nested", encoding="utf-8")

            with patch.object(
                workspace_generator.subprocess,
                "run",
                return_value=SimpleNamespace(stdout=str(packaged_root.parent)),
            ):
                files = workspace_generator.tracked_workshop_files(packaged_root)

        self.assertEqual(files, [Path("lab-03-search-grounding/README.md")])

    def test_roster_has_expected_unique_opg26a_participants(self) -> None:
        cohort, participants = workspace_generator.load_roster(
            REPO_ROOT / "config" / "workshop-participants.json"
        )

        self.assertEqual(cohort, "opg26a")
        self.assertEqual(
            participants,
            [
                "mt",
                "rj",
                "ys",
                "mm",
                "ms",
                "pg",
                "ts",
                "kp",
                "ds",
                "mv",
                "ap",
                "ha",
                "zk",
                "dc",
                "rr",
            ],
        )
        prefixes = {
            workspace_generator.participant_assignments(cohort, participant)[
                "RESOURCE_PREFIX"
            ]
            for participant in participants
        }
        self.assertEqual(len(prefixes), len(participants))

    def test_environment_uses_the_participant_prefix(self) -> None:
        assignments = workspace_generator.participant_assignments("opg26a", "mt")
        rendered = workspace_generator.render_environment(
            (REPO_ROOT / ".env.example").read_text(encoding="utf-8"),
            assignments,
            {"FOUNDRY_MODEL_NAME": "shared-workshop-model"},
        )

        self.assertIn("RESOURCE_PREFIX=opg26a-mt", rendered)
        self.assertIn(
            "AZURE_SEARCH_INDEX_NAME=opg26a-mt-maintenance-documents",
            rendered,
        )
        self.assertIn(
            "HOSTED_AGENT_NAME=opg26a-mt-maintenance-agent",
            rendered,
        )
        self.assertIn("FOUNDRY_MODEL_NAME=shared-workshop-model", rendered)
        self.assertNotIn("<initials>", rendered)

    def test_generated_workspace_excludes_instructor_files_and_refuses_overwrite(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_root = Path(temporary_directory)
            shared_environment = output_root / "shared.env"
            shared_environment.write_text(
                "FOUNDRY_MODEL_NAME=shared-workshop-model\n",
                encoding="utf-8",
            )
            created = workspace_generator.create_workspaces(
                REPO_ROOT,
                output_root,
                "opg26a",
                ["mt"],
                REPO_ROOT / ".env.example",
                shared_environment,
            )
            workspace = output_root / "opg26a-mt"

            self.assertEqual(created, [workspace])
            self.assertTrue((workspace / "lab-03-search-grounding" / "README.md").is_file())
            self.assertTrue((workspace / "tests" / "test_lab_03_search.py").is_file())
            self.assertTrue((workspace / ".env").is_file())
            environment_example = (workspace / ".env.example").read_text(
                encoding="utf-8"
            )
            self.assertIn("RESOURCE_PREFIX=opg26a-mt", environment_example)
            self.assertNotIn("<initials>", environment_example)
            self.assertNotIn("shared-workshop-model", environment_example)
            self.assertIn(
                "FOUNDRY_MODEL_NAME=shared-workshop-model",
                (workspace / ".env").read_text(encoding="utf-8"),
            )
            self.assertTrue((workspace / "PARTICIPANT.md").is_file())
            self.assertTrue(
                (workspace / "config" / "workshop-participants.json").is_file()
            )
            self.assertTrue(
                (workspace / "scripts" / "create_participant_workspaces.py").is_file()
            )
            self.assertFalse((workspace / "AGENTS.md").exists())
            self.assertFalse(
                (workspace / "lab-03-search-grounding" / "FACILITATOR.md").exists()
            )
            self.assertFalse((workspace / ".git").exists())

            with self.assertRaises(FileExistsError):
                workspace_generator.create_workspaces(
                    REPO_ROOT,
                    output_root,
                    "opg26a",
                    ["mt"],
                    REPO_ROOT / ".env.example",
                )


if __name__ == "__main__":
    unittest.main()