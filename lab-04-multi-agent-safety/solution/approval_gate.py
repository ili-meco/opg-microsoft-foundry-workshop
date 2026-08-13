"""Validate the human-review packet and enforce its approval boundary."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HumanReviewPacket(BaseModel):
    """Strict contract returned by the safety reviewer agent."""

    model_config = ConfigDict(extra="forbid")

    ready_for_human: bool
    findings: list[str]
    recommendation: str = Field(min_length=1)
    citations: list[str]
    requires_human_decision: Literal[True]
    action_authority: Literal["none"] = "none"


class HumanDecisionRecord(BaseModel):
    """Application-owned record created after an eligible human decision."""

    model_config = ConfigDict(extra="forbid")

    human_decision: Literal["approve", "reject"]
    recommendation: str
    findings: list[str]
    citations: list[str]
    action_authority: Literal["none"] = "none"


def parse_review_packet(review_text: str) -> HumanReviewPacket:
    """Parse exact reviewer JSON and reject markdown or additional fields."""
    return HumanReviewPacket.model_validate_json(review_text)


def record_human_decision(
    review: HumanReviewPacket,
    human_decision: Literal["approve", "reject"],
) -> HumanDecisionRecord:
    """Record a decision only for a recommendation cleared for human review."""
    if not review.ready_for_human:
        raise ValueError("This recommendation is not ready for a human decision.")

    return HumanDecisionRecord(
        human_decision=human_decision,
        recommendation=review.recommendation,
        findings=review.findings,
        citations=review.citations,
    )