"""Lab 04 starter: compose planner and reviewer agents with MAF."""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


FOUNDRY_TOKEN_SCOPE = "https://ai.azure.com/.default"

PLANNER_INSTRUCTIONS = """Draft a maintenance recommendation from supplied facts and evidence.
Never claim authority to control equipment, approve work, or reserve inventory.
"""
REVIEWER_INSTRUCTIONS = """Independently review the planner draft for unsupported or unsafe claims.
Return only the strict SafetyReview JSON described in the participant guide.
"""


def foundry_openai_base_url(project_endpoint: str) -> str:
    return f"{project_endpoint.rstrip('/')}/openai/v1/"


def foundry_token_provider(credential: DefaultAzureCredential):
    sync_provider = get_bearer_token_provider(credential, FOUNDRY_TOKEN_SCOPE)

    async def get_token() -> str:
        return sync_provider()

    return get_token


def build_foundry_chat_client(
    project_endpoint: str,
    model_name: str,
    credential: DefaultAzureCredential,
) -> OpenAIChatClient:
    return OpenAIChatClient(
        model=model_name,
        api_key=foundry_token_provider(credential),
        base_url=foundry_openai_base_url(project_endpoint),
    )


def build_workflow(
    project_endpoint: str,
    model_name: str,
    credential: DefaultAzureCredential,
):
    client = build_foundry_chat_client(project_endpoint, model_name, credential)
    planner = Agent(client=client, name="maintenance_planner", instructions=PLANNER_INSTRUCTIONS)
    reviewer = Agent(client=client, name="safety_reviewer", instructions=REVIEWER_INSTRUCTIONS)

    # TODO 1: Create a SequentialBuilder with the two agents in execution order.
    #
    # Put `planner` first so it drafts from the assessment package. Put
    # `reviewer` second so it receives the shared workflow context and critiques
    # the draft under a different instruction set.
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