"""Lab 03 starter: compare keyword, vector, and hybrid Search queries."""

from __future__ import annotations

import os
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from dotenv import load_dotenv


SEMANTIC_CONFIGURATION_NAME = "maintenance-semantic"


def build_keyword_query(query: str, top: int = 3) -> dict[str, Any]:
    # TODO 1: Return a dictionary with two arguments for SearchClient.search:
    # - search_text: the user's exact query, which enables lexical term matching.
    # - top: the maximum number of results to return.
    # Do not add vector_queries. This mode is the keyword-only baseline.
    raise NotImplementedError


def build_vector_query(query: str, top: int = 3) -> dict[str, Any]:
    # TODO 2: Return search_text=None, top=top, and one vector_queries item.
    # Construct VectorizableTextQuery with text=query, fields="content_vector",
    # and k_nearest_neighbors=top. Azure AI Search sends the text to the
    # vectorizer configured on the index, then compares the resulting embedding
    # with stored document vectors. search_text=None keeps this vector-only.
    raise NotImplementedError


def build_hybrid_query(query: str, top: int = 3) -> dict[str, Any]:
    # TODO 3: Combine the keyword and vector arguments from TODOs 1 and 2.
    # Also set query_type="semantic" and semantic_configuration_name to the
    # constant above. Search merges lexical and vector candidates, then the
    # semantic ranker reranks the combined result set.
    raise NotImplementedError


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
    if not value or value.startswith("<"):
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
        score = result.get("@search.reranker_score", result.get("@search.score", 0))
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