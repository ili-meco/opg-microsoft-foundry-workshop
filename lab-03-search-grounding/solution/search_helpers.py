from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from azure.search.documents.indexes.models import (
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    HnswAlgorithmConfiguration,
    SearchField,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizableTextQuery
from openai import OpenAI


SEMANTIC_CONFIGURATION_NAME = "maintenance-semantic"
VECTOR_PROFILE_NAME = "maintenance-vector-profile"
VECTOR_ALGORITHM_NAME = "maintenance-hnsw"
VECTORIZER_NAME = "maintenance-openai-vectorizer"


def load_documents(data_path: Path) -> list[dict[str, Any]]:
    with data_path.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def build_search_index(
    index_name: str,
    azure_openai_endpoint: str,
    embedding_deployment: str,
    embedding_model: str,
    embedding_dimensions: int,
) -> SearchIndex:
    return SearchIndex(
        name=index_name,
        description="Synthetic OPG maintenance procedures for the workshop.",
        fields=[
            SearchField(name="id", type="Edm.String", key=True, filterable=True),
            SearchField(name="title", type="Edm.String", searchable=True),
            SearchField(name="content", type="Edm.String", searchable=True),
            SearchField(
                name="document_type",
                type="Edm.String",
                searchable=True,
                filterable=True,
                facetable=True,
            ),
            SearchField(
                name="asset_type",
                type="Edm.String",
                searchable=True,
                filterable=True,
                facetable=True,
            ),
            SearchField(
                name="effective_date",
                type="Edm.String",
                filterable=True,
                sortable=True,
            ),
            SearchField(name="revision", type="Edm.Int32", filterable=True, sortable=True),
            SearchField(name="source_url", type="Edm.String", filterable=True),
            SearchField(
                name="content_vector",
                type="Collection(Edm.Single)",
                searchable=True,
                stored=False,
                vector_search_dimensions=embedding_dimensions,
                vector_search_profile_name=VECTOR_PROFILE_NAME,
            ),
        ],
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name=VECTOR_ALGORITHM_NAME)],
            profiles=[
                VectorSearchProfile(
                    name=VECTOR_PROFILE_NAME,
                    algorithm_configuration_name=VECTOR_ALGORITHM_NAME,
                    vectorizer_name=VECTORIZER_NAME,
                )
            ],
            vectorizers=[
                AzureOpenAIVectorizer(
                    vectorizer_name=VECTORIZER_NAME,
                    parameters=AzureOpenAIVectorizerParameters(
                        resource_url=azure_openai_endpoint,
                        deployment_name=embedding_deployment,
                        model_name=embedding_model,
                    ),
                )
            ],
        ),
        semantic_search=SemanticSearch(
            default_configuration_name=SEMANTIC_CONFIGURATION_NAME,
            configurations=[
                SemanticConfiguration(
                    name=SEMANTIC_CONFIGURATION_NAME,
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                        keywords_fields=[
                            SemanticField(field_name="document_type"),
                            SemanticField(field_name="asset_type"),
                        ],
                    ),
                )
            ],
        ),
    )


def add_embeddings(
    documents: Iterable[dict[str, Any]],
    openai_client: OpenAI,
    embedding_deployment: str,
) -> list[dict[str, Any]]:
    prepared = [dict(document) for document in documents]
    response = openai_client.embeddings.create(
        model=embedding_deployment,
        input=[f"{document['title']}\n{document['content']}" for document in prepared],
    )
    if len(response.data) != len(prepared):
        raise RuntimeError("Embedding response count did not match the document count.")

    for document, embedding in zip(prepared, response.data, strict=True):
        document["content_vector"] = embedding.embedding
    return prepared


def build_query_arguments(query: str, mode: str, top: int = 3) -> dict[str, Any]:
    if mode not in {"keyword", "vector", "hybrid"}:
        raise ValueError("mode must be keyword, vector, or hybrid")

    arguments: dict[str, Any] = {
        "search_text": query if mode in {"keyword", "hybrid"} else None,
        "select": [
            "id",
            "title",
            "content",
            "document_type",
            "asset_type",
            "effective_date",
            "revision",
            "source_url",
        ],
        "top": top,
    }
    if mode in {"vector", "hybrid"}:
        arguments["vector_queries"] = [
            VectorizableTextQuery(text=query, k=top, fields="content_vector")
        ]
    if mode == "hybrid":
        arguments.update(
            query_type="semantic",
            semantic_configuration_name=SEMANTIC_CONFIGURATION_NAME,
        )
    return arguments


def run_search(search_client: Any, query: str, mode: str, top: int = 3) -> list[dict[str, Any]]:
    return list(search_client.search(**build_query_arguments(query, mode, top)))


def print_results(mode: str, results: list[dict[str, Any]]) -> None:
    print(f"\n=== {mode.upper()} ===")
    for rank, result in enumerate(results, start=1):
        score = result.get("@search.reranker_score", result.get("@search.score", 0))
        print(
            f"{rank}. {result['id']} | score={score:.4f} | "
            f"revision={result['revision']} | {result['title']}"
        )