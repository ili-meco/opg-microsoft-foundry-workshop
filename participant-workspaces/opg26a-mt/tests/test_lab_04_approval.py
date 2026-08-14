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


def review(ready_for_human: bool = True):
    return approval_gate.HumanReviewPacket(
        ready_for_human=ready_for_human,
        findings=[] if ready_for_human else ["Current vibration evidence is missing."],
        recommendation="Inspect and collect current measurements.",
        citations=["Centrifugal Pump Inspection Procedure, R3"],
        requires_human_decision=True,
    )


class ApprovalGateTests(unittest.TestCase):
    def test_exact_json_review_is_parsed(self) -> None:
        parsed = approval_gate.parse_review_packet(review().model_dump_json())

        self.assertTrue(parsed.ready_for_human)
        self.assertTrue(parsed.requires_human_decision)

    def test_extra_reviewer_fields_fail_closed(self) -> None:
        payload = review().model_dump()
        payload["execute_work_order"] = True

        with self.assertRaises(ValidationError):
            approval_gate.HumanReviewPacket.model_validate(payload)

    def test_human_decision_is_rejected_when_review_is_not_ready(self) -> None:
        with self.assertRaises(ValueError):
            approval_gate.record_human_decision(review(False), "approve")

    def test_human_can_approve_or_reject_a_ready_recommendation(self) -> None:
        approved = approval_gate.record_human_decision(review(), "approve")
        rejected = approval_gate.record_human_decision(review(), "reject")

        self.assertEqual(approved.human_decision, "approve")
        self.assertEqual(rejected.human_decision, "reject")
        self.assertEqual(approved.action_authority, "none")


if __name__ == "__main__":
    unittest.main()