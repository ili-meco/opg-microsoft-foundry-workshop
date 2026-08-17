"""Remove Lab 03 knowledge resources and optionally the Search index."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents.indexes import SearchIndexClient
from dotenv import load_dotenv


WORKSPACE_ROOT = Path(__file__).parents[2]


def required_environment(variable: str) -> str:
    value = os.getenv(variable, "").strip()
    if not value or "<" in value or ">" in value:
        raise RuntimeError(f"Set {variable} in the repository .env file.")
    return value


def required_participant_resource(variable: str) -> str:
    prefix = required_environment("RESOURCE_PREFIX")
    value = required_environment(variable)
    if not value.startswith(f"{prefix}-"):
        raise RuntimeError(
            f"{variable} must start with '{prefix}-' to avoid changing another "
            "participant's resources."
        )
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delete-index", action="store_true")
    args = parser.parse_args()
    load_dotenv(WORKSPACE_ROOT / ".env", override=True)

    search_endpoint = required_environment("AZURE_SEARCH_ENDPOINT")
    project_resource_id = required_environment("FOUNDRY_PROJECT_RESOURCE_ID")
    index_name = required_participant_resource("AZURE_SEARCH_INDEX_NAME")
    source_name = required_participant_resource("AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME")
    base_name = required_participant_resource("AZURE_SEARCH_KNOWLEDGE_BASE_NAME")
    connection_name = required_participant_resource("FOUNDRY_IQ_CONNECTION_NAME")

    with DefaultAzureCredential() as credential:
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
        index_client.delete_knowledge_base(base_name)
        index_client.delete_knowledge_source(source_name)
        if args.delete_index:
            index_client.delete_index(index_name)

        token_provider = get_bearer_token_provider(
            credential, "https://management.azure.com/.default"
        )
        response = requests.delete(
            (
                f"https://management.azure.com{project_resource_id}/connections/"
                f"{connection_name}?api-version=2025-10-01-preview"
            ),
            headers={"Authorization": f"Bearer {token_provider()}"},
            timeout=30,
        )
        if response.status_code != 404:
            response.raise_for_status()

    retained = "nothing" if args.delete_index else f"index '{index_name}'"
    print(f"Lab 03 cleanup complete; retained {retained}.")


if __name__ == "__main__":
    main()