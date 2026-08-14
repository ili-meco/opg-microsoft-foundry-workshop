"""Create and validate a structured maintenance assessment."""

from __future__ import annotations

from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field


ASSESSMENT_INSTRUCTIONS = """You are an OPG maintenance-planning assistant.
Use only facts in the request. Separate observations from assumptions.
State missing evidence and escalate when the evidence is insufficient.
Recommend planner actions only. Never claim to control equipment, approve work,
reserve inventory, or update a work order.
"""


class StrictModel(BaseModel):
    """Reject fields that are not part of the workshop response contract."""

    model_config = ConfigDict(extra="forbid")


class MaintenanceAssessment(StrictModel):
    """Validated output contract shared by the later workshop labs."""

    asset_id: str | None = Field(description="Asset identifier when supplied.")
    summary: str = Field(min_length=1)
    observations: list[str] = Field(min_length=1)
    assumptions: list[str]
    risk_level: Literal["low", "medium", "high", "critical", "unknown"]
    recommended_actions: list[str] = Field(min_length=1)
    missing_evidence: list[str]
    requires_escalation: bool
    authorization: Literal["recommendation_only"]


def request_structured_assessment(
    client: OpenAI,
    model_name: str,
    request: str,
) -> MaintenanceAssessment:
    """Ask the model for an assessment parsed into the strict contract."""
    response = client.responses.parse(
        model=model_name,
        instructions=ASSESSMENT_INSTRUCTIONS,
        input=request,
        text_format=MaintenanceAssessment,
    )
    if response.output_parsed is None:
        raise RuntimeError("The model did not return a structured maintenance assessment.")
    return response.output_parsed