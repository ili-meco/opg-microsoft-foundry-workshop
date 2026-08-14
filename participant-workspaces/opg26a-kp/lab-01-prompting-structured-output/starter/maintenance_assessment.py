"""Lab 01 starter: complete the structured maintenance contract."""

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
    model_config = ConfigDict(extra="forbid")


class MaintenanceAssessment(StrictModel):
    """TODO: complete the fields described in the participant guide."""

    asset_id: str | None = Field(description="Asset identifier when supplied.")
    summary: str = Field(min_length=1)
    observations: list[str] = Field(min_length=1)
    assumptions: list[str]
    risk_level: Literal["low", "medium", "high", "critical", "unknown"]
    # TODO 1: add recommended_actions and missing_evidence lists.
    # TODO 2: add requires_escalation as a boolean.
    # TODO 3: add authorization constrained to "recommendation_only".


def request_structured_assessment(
    client: OpenAI,
    model_name: str,
    request: str,
) -> MaintenanceAssessment:
    """TODO: call client.responses.parse with MaintenanceAssessment."""
    raise NotImplementedError("Complete the Lab 01 structured-output request.")