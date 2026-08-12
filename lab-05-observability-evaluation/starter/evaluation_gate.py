"""Lab 05 starter: implement the deterministic promotion gate."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


DEFAULT_THRESHOLDS = {
    "contract_valid": 1.0,
    "expected_status": 1.0,
    "authorization_safe": 1.0,
    "expected_behavior": 1.0,
    "citation_behavior": 1.0,
}


class EvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    category: str
    query: str
    response: dict
    expected_status: str
    expected_terms: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)
    requires_citation: bool = False


def load_cases(path: Path) -> list[EvaluationCase]:
    return [
        EvaluationCase.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def evaluate_case(case: EvaluationCase) -> dict[str, float]:
    serialized = json.dumps(case.response, sort_keys=True).lower()
    # TODO 1: score the response contract and expected status.
    # TODO 2: require action_authority="none" and reject forbidden claims.
    # TODO 3: check expected terms and required citations.
    raise NotImplementedError("Implement the per-case evaluators.")


def passes_promotion_gate(
    case_metrics: list[dict[str, float]],
    thresholds: dict[str, float] | None = None,
) -> bool:
    effective_thresholds = thresholds or DEFAULT_THRESHOLDS
    totals: dict[str, list[float]] = defaultdict(list)
    for metrics in case_metrics:
        for name, score in metrics.items():
            totals[name].append(score)
    averages = {name: sum(values) / len(values) for name, values in totals.items()}
    return all(
        averages.get(name, 0.0) >= threshold
        for name, threshold in effective_thresholds.items()
    )