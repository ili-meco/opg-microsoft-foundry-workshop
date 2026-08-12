"""Run interactive keyword, vector, and hybrid queries against the workshop index."""

from __future__ import annotations

import os

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

from search_helpers import build_query_arguments, print_results


def required_environment(variable: str) -> str:
    value = os.getenv(variable, "").strip()
    if not value or value.startswith("<"):
        raise RuntimeError(f"Set {variable} in the repository .env file.")
    return value


def read_query() -> str | None:
    query = input("\nSearch question (or 'exit'): ").strip()
    if not query or query.lower() in {"exit", "quit"}:
        return None
    return query


def main() -> None:
    load_dotenv()
    search_endpoint = required_environment("AZURE_SEARCH_ENDPOINT")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "opg-maintenance-documents")

    with DefaultAzureCredential() as credential:
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=credential,
        )
        print(f"Connected to Search index '{index_name}'.")
        print("Each question runs in all three modes so you can compare ranking.")
        while query := read_query():
            for mode in ("keyword", "vector", "hybrid"):
                results = list(search_client.search(**build_query_arguments(query, mode)))
                print_results(mode, results)


if __name__ == "__main__":
    main()