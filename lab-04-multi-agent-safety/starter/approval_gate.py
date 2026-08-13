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
    # TODO 1: Validate the reviewer's raw response as the SafetyReview contract.
    #
    # Context:
    # - `review_text` is untrusted model output, even though the reviewer was
    #   instructed to return JSON.
    # - Parse the original string directly with Pydantic's JSON validation API.
    #   Do not remove ``` fences, extract a substring, or silently repair JSON.
    # - SafetyReview forbids extra fields and requires
    #   `requires_human_approval` to be exactly true. Validation should raise if
    #   the response is malformed, contains an unknown field, or omits a field.
    #
    # Expected result:
    # - Valid exact JSON returns a SafetyReview instance.
    # - Invalid or embellished output fails closed with a validation error.
    raise NotImplementedError("Parse the reviewer contract.")


def apply_approval_gate(
    review: SafetyReview,
    human_decision: Literal["approve", "reject"] | None = None,
) -> ApprovalRecord:
    # TODO 2: Compute status with an application-owned state machine.
    #
    # Evaluate the reviewer decision before the human decision:
    # - review.decision is `revise` or `escalate` -> `blocked`, even when the
    #   human_decision argument is `approve`.
    # - review.decision is `approve` and human_decision is None -> `pending`.
    # - review.decision is `approve` and the human approves -> `approved`.
    # - review.decision is `approve` and the human rejects -> `rejected`.
    #
    # This ordering is the safety boundary: human approval can accept a clean
    # recommendation, but it cannot repair missing evidence or override a block.
    #
    # TODO 3: Return an ApprovalRecord that preserves the audit evidence.
    #
    # Copy the reviewer decision, reviewed recommendation, findings, citations,
    # and supplied human decision into the record. Do not add tool execution or
    # action logic. Leave `action_authority` at its model default of `none` for
    # every status, including `approved`.
    raise NotImplementedError("Implement the deterministic approval state machine.")