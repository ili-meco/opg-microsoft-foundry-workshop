"""Create the workshop index, upload documents, and compare retrieval modes."""

from __future__ import annotations

import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from dotenv import load_dotenv

from search_helpers import (
    add_embeddings,
    build_search_index,
    load_documents,
    print_results,
    run_search,
)


DATA_PATH = Path(__file__).parents[1] / "data" / "maintenance_documents.json"
DEFAULT_QUERY = "What should happen when pump vibration rises and the seal starts leaking?"


def required_environment(variable: str) -> str:
    value = os.getenv(variable, "").strip()
    if not value or value.startswith("<"):
        raise RuntimeError(f"Set {variable} in the repository .env file.")
    return value


def main() -> None:
    load_dotenv()
    project_endpoint = required_environment("FOUNDRY_PROJECT_ENDPOINT")
    search_endpoint = required_environment("AZURE_SEARCH_ENDPOINT")
    azure_openai_endpoint = required_environment("AZURE_OPENAI_ENDPOINT")
    embedding_deployment = required_environment("FOUNDRY_EMBEDDING_MODEL_NAME")
    embedding_model = os.getenv("FOUNDRY_EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dimensions = int(os.getenv("FOUNDRY_EMBEDDING_DIMENSIONS", "1536"))
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "opg-maintenance-documents")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
        index = build_search_index(
            index_name,
            azure_openai_endpoint,
            embedding_deployment,
            embedding_model,
            embedding_dimensions,
        )
        index_client.create_or_update_index(index)
        print(f"Created or updated index '{index_name}'.")

        documents = add_embeddings(load_documents(DATA_PATH), openai_client, embedding_deployment)
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=credential,
        )
        results = search_client.upload_documents(documents=documents)
        failed = [result.key for result in results if not result.succeeded]
        if failed:
            raise RuntimeError(f"Document upload failed for: {', '.join(failed)}")
        print(f"Uploaded {len(documents)} synthetic documents.")

        for mode in ("keyword", "vector", "hybrid"):
            print_results(mode, run_search(search_client, DEFAULT_QUERY, mode))


if __name__ == "__main__":
    main()