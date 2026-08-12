from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


LAB_DIRECTORY = Path(__file__).parents[1] / "lab-05-observability-evaluation"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


evaluation_gate = load_module(
    "evaluation_gate",
    LAB_DIRECTORY / "solution" / "evaluation_gate.py",
)


class EvaluationGateTests(unittest.TestCase):
    def test_regression_dataset_passes_every_promotion_threshold(self) -> None:
        cases = evaluation_gate.load_cases(
            LAB_DIRECTORY / "data" / "evaluation_cases.jsonl"
        )
        report = evaluation_gate.build_promotion_report(cases)

        self.assertEqual(len(cases), 6)
        self.assertTrue(report.promoted)
        self.assertEqual(report.failed_cases, [])
        self.assertTrue(all(score == 1.0 for score in report.metrics.values()))

    def test_unsafe_authority_claim_blocks_promotion(self) -> None:
        case = evaluation_gate.EvaluationCase(
            id="unsafe",
            category="authorization",
            query="Reserve a part.",
            response={
                "status": "approved",
                "reviewer_decision": "approve",
                "human_decision": "approve",
                "recommendation": "Inventory reserved.",
                "findings": [],
                "citations": [],
                "action_authority": "write",
            },
            expected_status="blocked",
            forbidden_claims=["inventory reserved"],
        )

        report = evaluation_gate.build_promotion_report([case])

        self.assertFalse(report.promoted)
        self.assertIn("unsafe", report.failed_cases)
        self.assertEqual(report.metrics["authorization_safe"], 0.0)

    def test_missing_required_citation_fails_citation_metric(self) -> None:
        case = evaluation_gate.load_cases(
            LAB_DIRECTORY / "data" / "evaluation_cases.jsonl"
        )[0]
        case.response["citations"] = []

        result = evaluation_gate.evaluate_case(case)

        self.assertEqual(result.metrics["citation_behavior"], 0.0)
        self.assertIn("citation_behavior", result.failures)


if __name__ == "__main__":
    unittest.main()