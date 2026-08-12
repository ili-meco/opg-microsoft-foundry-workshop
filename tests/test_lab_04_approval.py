from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from pydantic import ValidationError


SOLUTION_FILE = (
    Path(__file__).parents[1]
    / "lab-04-multi-agent-safety"
    / "solution"
    / "approval_gate.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


approval_gate = load_module("approval_gate", SOLUTION_FILE)


def review(decision: str = "approve"):
    return approval_gate.SafetyReview(
        decision=decision,
        findings=[] if decision == "approve" else ["Current vibration evidence is missing."],
        blocked_actions=["start equipment"],
        reviewed_recommendation="Inspect and collect current measurements.",
        citations=["Centrifugal Pump Inspection Procedure, R3"],
        requires_human_approval=True,
    )


class ApprovalGateTests(unittest.TestCase):
    def test_exact_json_review_is_parsed(self) -> None:
        parsed = approval_gate.parse_safety_review(review().model_dump_json())

        self.assertEqual(parsed.decision, "approve")
        self.assertTrue(parsed.requires_human_approval)

    def test_extra_reviewer_fields_fail_closed(self) -> None:
        payload = review().model_dump()
        payload["execute_work_order"] = True

        with self.assertRaises(ValidationError):
            approval_gate.SafetyReview.model_validate(payload)

    def test_clean_review_remains_pending_without_human_decision(self) -> None:
        record = approval_gate.apply_approval_gate(review())

        self.assertEqual(record.status, "pending")
        self.assertEqual(record.action_authority, "none")

    def test_human_cannot_override_revise_or_escalate(self) -> None:
        for reviewer_decision in ("revise", "escalate"):
            with self.subTest(reviewer_decision=reviewer_decision):
                record = approval_gate.apply_approval_gate(
                    review(reviewer_decision),
                    "approve",
                )
                self.assertEqual(record.status, "blocked")
                self.assertEqual(record.action_authority, "none")

    def test_human_can_approve_or_reject_a_clean_recommendation(self) -> None:
        approved = approval_gate.apply_approval_gate(review(), "approve")
        rejected = approval_gate.apply_approval_gate(review(), "reject")

        self.assertEqual(approved.status, "approved")
        self.assertEqual(rejected.status, "rejected")
        self.assertEqual(approved.action_authority, "none")


if __name__ == "__main__":
    unittest.main()