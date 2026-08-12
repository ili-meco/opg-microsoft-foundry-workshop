"""Validate safety-review output and enforce the human approval boundary."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SafetyReview(BaseModel):
    """Strict contract returned by the safety reviewer agent."""

    model_config = ConfigDict(extra="forbid")

    decision: Literal["approve", "revise", "escalate"]
    findings: list[str]
    blocked_actions: list[str]
    reviewed_recommendation: str = Field(min_length=1)
    citations: list[str]
    requires_human_approval: Literal[True]


class ApprovalRecord(BaseModel):
    """Application-owned record of the review and human decision."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["pending", "approved", "rejected", "blocked"]
    reviewer_decision: Literal["approve", "revise", "escalate"]
    human_decision: Literal["approve", "reject"] | None
    recommendation: str
    findings: list[str]
    citations: list[str]
    action_authority: Literal["none"] = "none"


def parse_safety_review(review_text: str) -> SafetyReview:
    """Parse exact reviewer JSON and reject markdown or additional fields."""
    return SafetyReview.model_validate_json(review_text)


def apply_approval_gate(
    review: SafetyReview,
    human_decision: Literal["approve", "reject"] | None = None,
) -> ApprovalRecord:
    """Allow approval only after a clean reviewer decision and explicit consent."""
    if review.decision != "approve":
        status = "blocked"
    elif human_decision is None:
        status = "pending"
    elif human_decision == "approve":
        status = "approved"
    else:
        status = "rejected"

    return ApprovalRecord(
        status=status,
        reviewer_decision=review.decision,
        human_decision=human_decision,
        recommendation=review.reviewed_recommendation,
        findings=review.findings,
        citations=review.citations,
    )