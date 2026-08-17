"""Lab 03 solution: compare keyword, vector, and hybrid Search queries."""

from __future__ import annotations

import os
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from dotenv import load_dotenv


SEMANTIC_CONFIGURATION_NAME = "maintenance-semantic"


def build_keyword_query(query: str, top: int = 3) -> dict[str, Any]:
    return {
        "search_text": query,
        "top": top,
    }


def build_vector_query(query: str, top: int = 3) -> dict[str, Any]:
    return {
        "search_text": None,
        "vector_queries": [
            VectorizableTextQuery(
                text=query,
                fields="content_vector",
                k_nearest_neighbors=top,
            )
        ],
        "top": top,
    }


def build_hybrid_query(query: str, top: int = 3) -> dict[str, Any]:
    return {
        "search_text": query,
        "vector_queries": [
            VectorizableTextQuery(
                text=query,
                fields="content_vector",
                k_nearest_neighbors=top,
            )
        ],
        "query_type": "semantic",
        "semantic_configuration_name": SEMANTIC_CONFIGURATION_NAME,
        "top": top,
    }


QUERY_BUILDERS = {
    "keyword": build_keyword_query,
    "vector": build_vector_query,
    "hybrid": build_hybrid_query,
}
SELECT_FIELDS = [
    "id",
    "title",
    "document_type",
    "asset_type",
    "effective_date",
    "revision",
]


def required_environment(variable: str) -> str:
    value = os.getenv(variable, "").strip()
    if not value or "<" in value or ">" in value:
        raise RuntimeError(f"Set {variable} in the repository .env file.")
    return value


def read_query() -> str | None:
    query = input("\nSearch question (or 'exit'): ").strip()
    if not query or query.lower() in {"exit", "quit"}:
        return None
    return query


def print_results(mode: str, results: list[dict[str, Any]]) -> None:
    print(f"\n=== {mode.upper()} ===")
    for rank, result in enumerate(results, start=1):
        score = result.get("@search.reranker_score")
        if score is None:
            score = result.get("@search.score") or 0.0
        print(
            f"{rank}. {result['id']} | score={score:.4f} | "
            f"revision={result['revision']} | {result['title']}"
        )


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
            for mode, build_query in QUERY_BUILDERS.items():
                arguments = build_query(query)
                arguments["select"] = SELECT_FIELDS
                results = list(search_client.search(**arguments))
                print_results(mode, results)


if __name__ == "__main__":
    main()