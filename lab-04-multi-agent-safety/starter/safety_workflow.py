"""Lab 04 starter: compose evidence, planning, and review agents with MAF."""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import DefaultAzureCredential

EVIDENCE_ANALYST_INSTRUCTIONS = """Extract facts, current evidence, conflicts, and gaps.
Return an EvidencePacket for the planner. Do not recommend or authorize actions.
"""
PLANNER_INSTRUCTIONS = """Draft a maintenance recommendation from the EvidencePacket.
Never claim authority to control equipment, approve work, or reserve inventory.
Attach a [Source: title, revision] citation to every consequential recommendation.
Preserve uncertainty about continued operation and whether a listed part is needed.
Begin the response with the exact line PLANNER_DRAFT.
"""
REVIEWER_INSTRUCTIONS = """Independently review the planner draft for unsupported or unsafe claims.
The assistant message beginning with PLANNER_DRAFT is the planner artifact.
Return only the strict HumanReviewPacket JSON described in the participant guide.
"""


def build_foundry_chat_client(
    project_endpoint: str,
    model_name: str,
    credential: DefaultAzureCredential,
) -> FoundryChatClient:
    return FoundryChatClient(
        project_endpoint=project_endpoint,
        model=model_name,
        credential=credential,
    )


def build_workflow(
    project_endpoint: str,
    model_name: str,
    credential: DefaultAzureCredential,
):
    client = build_foundry_chat_client(project_endpoint, model_name, credential)
    analyst = Agent(
        client=client,
        name="evidence_analyst",
        instructions=EVIDENCE_ANALYST_INSTRUCTIONS,
    )
    planner = Agent(client=client, name="maintenance_planner", instructions=PLANNER_INSTRUCTIONS)
    reviewer = Agent(client=client, name="safety_reviewer", instructions=REVIEWER_INSTRUCTIONS)

    # TODO 1: Create a SequentialBuilder with the three agents in execution order.
    #
    # Put `analyst` first to separate evidence from gaps, `planner` second to
    # draft from that packet, and `reviewer` last to decide whether the draft is
    # ready for a human decision.
    #
    # TODO 2: Select only the reviewer as the workflow output.
    #
    # Configure `output_from` with the reviewer. This prevents the unreviewed
    # planner draft from becoming the application's final response.
    #
    # TODO 3: Build the workflow and expose it through an agent interface.
    #
    # Call build(), then as_agent(...) with the workflow name from the
    # participant guide. This wrapper is not a third specialist agent; it gives
    # the composed workflow the interface used by `workflow.run(...)`.
    raise NotImplementedError("Compose the MAF workflow.")