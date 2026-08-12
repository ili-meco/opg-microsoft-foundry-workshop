"""Lab 03 starter: construct direct Azure AI Search query arguments."""

from __future__ import annotations

from typing import Any

from azure.search.documents.models import VectorizableTextQuery


SEMANTIC_CONFIGURATION_NAME = "maintenance-semantic"


def build_keyword_query(query: str, top: int = 3) -> dict[str, Any]:
    # TODO: return search_text and top for lexical retrieval.
    raise NotImplementedError


def build_vector_query(query: str, top: int = 3) -> dict[str, Any]:
    # TODO: omit lexical text and add a VectorizableTextQuery over content_vector.
    raise NotImplementedError


def build_hybrid_query(query: str, top: int = 3) -> dict[str, Any]:
    # TODO: combine lexical and vector retrieval, then enable semantic ranking.
    raise NotImplementedError


if __name__ == "__main__":
    question = "What should happen when pump vibration rises and the seal starts leaking?"
    print(build_keyword_query(question))
    print(build_vector_query(question))
    print(build_hybrid_query(question))