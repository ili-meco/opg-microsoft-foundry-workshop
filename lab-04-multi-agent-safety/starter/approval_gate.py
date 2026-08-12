"""Lab 04 starter: complete the application-owned approval gate."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SafetyReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["approve", "revise", "escalate"]
    findings: list[str]
    blocked_actions: list[str]
    reviewed_recommendation: str = Field(min_length=1)
    citations: list[str]
    requires_human_approval: Literal[True]


class ApprovalRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["pending", "approved", "rejected", "blocked"]
    reviewer_decision: Literal["approve", "revise", "escalate"]
    human_decision: Literal["approve", "reject"] | None
    recommendation: str
    findings: list[str]
    citations: list[str]
    action_authority: Literal["none"] = "none"


def parse_safety_review(review_text: str) -> SafetyReview:
    # TODO 1: parse exact JSON into SafetyReview. Do not strip markdown.
    raise NotImplementedError("Parse the reviewer contract.")


def apply_approval_gate(
    review: SafetyReview,
    human_decision: Literal["approve", "reject"] | None = None,
) -> ApprovalRecord:
    # TODO 2: block revise/escalate even if the human selects approve.
    # TODO 3: keep a clean review pending until an explicit human decision.
    raise NotImplementedError("Implement the deterministic approval state machine.")