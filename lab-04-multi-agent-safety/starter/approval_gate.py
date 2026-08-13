"""Lab 04 starter: validate review output and record a human decision."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HumanReviewPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ready_for_human: bool
    findings: list[str]
    recommendation: str = Field(min_length=1)
    citations: list[str]
    requires_human_decision: Literal[True]
    action_authority: Literal["none"] = "none"


class HumanDecisionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    human_decision: Literal["approve", "reject"]
    recommendation: str
    findings: list[str]
    citations: list[str]
    action_authority: Literal["none"] = "none"


def parse_review_packet(review_text: str) -> HumanReviewPacket:
    # TODO 1: Validate the raw response as the HumanReviewPacket contract.
    #
    # Context:
    # - `review_text` is untrusted model output, even though the reviewer was
    #   instructed to return JSON.
    # - Parse the original string directly with Pydantic's JSON validation API.
    #   Do not remove ``` fences, extract a substring, or silently repair JSON.
    # - HumanReviewPacket forbids extra fields and requires
    #   `requires_human_decision` to be exactly true. Validation should raise if
    #   the response is malformed, contains an unknown field, or omits a field.
    #
    # Expected result:
    # - Valid exact JSON returns a HumanReviewPacket instance.
    # - Invalid or embellished output fails closed with a validation error.
    raise NotImplementedError("Parse the reviewer contract.")


def record_human_decision(
    review: HumanReviewPacket,
    human_decision: Literal["approve", "reject"],
) -> HumanDecisionRecord:
    # TODO 2: Reject the decision when `review.ready_for_human` is false.
    #
    # There is no status translation. The review packet answers one question:
    # may this recommendation be shown to a human for a decision? If the answer
    # is false, raise ValueError and preserve the review findings for rework.
    #
    # TODO 3: Return a HumanDecisionRecord that preserves the audit evidence.
    #
    # Copy the recommendation, findings, citations, and supplied human decision
    # into the record. Do not add tool execution or action logic. Leave
    # `action_authority` at its model default of `none`, including when the
    # human decision is `approve`.
    raise NotImplementedError("Enforce readiness and record the human decision.")