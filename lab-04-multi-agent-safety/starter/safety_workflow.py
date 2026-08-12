"""Lab 04 starter: compose planner and reviewer agents with MAF."""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import DefaultAzureCredential


PLANNER_INSTRUCTIONS = """Draft a maintenance recommendation from supplied facts and evidence.
Never claim authority to control equipment, approve work, or reserve inventory.
"""
REVIEWER_INSTRUCTIONS = """Independently review the planner draft for unsupported or unsafe claims.
Return only the strict SafetyReview JSON described in the participant guide.
"""


def foundry_openai_base_url(project_endpoint: str) -> str:
    return f"{project_endpoint.rstrip('/')}/openai/v1/"


def build_workflow(
    project_endpoint: str,
    model_name: str,
    credential: DefaultAzureCredential,
):
    client = OpenAIChatClient(
        model=model_name,
        credential=credential,
        base_url=foundry_openai_base_url(project_endpoint),
    )
    planner = Agent(client=client, name="maintenance_planner", instructions=PLANNER_INSTRUCTIONS)
    reviewer = Agent(client=client, name="safety_reviewer", instructions=REVIEWER_INSTRUCTIONS)

    # TODO: return SequentialBuilder(participants=[planner, reviewer],
    # output_from=[reviewer]).build().as_agent(...)
    raise NotImplementedError("Compose the MAF workflow.")