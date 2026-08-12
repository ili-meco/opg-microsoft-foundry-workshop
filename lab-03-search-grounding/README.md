# Lab 03: Azure AI Search and Foundry IQ Grounding

**Duration:** 90 minutes | **Skill level:** Intermediate

## What You Will Build

First, create and query an Azure AI Search index yourself. Then expose that same index through a Foundry IQ knowledge base and connect it to a Foundry prompt agent as the MCP tool `knowledge_base_retrieve`.

```text
Part A: JSON -> embeddings -> Search index -> keyword/vector/hybrid results

Part B: Search index -> knowledge source -> knowledge base -> MCP -> Foundry agent
```

The first half makes retrieval mechanics visible. The second half shows what Foundry IQ adds: reusable knowledge sources, query orchestration, source references, and an agent-compatible MCP endpoint.

## Learning Objectives

- Explain fields, keys, filters, semantic configuration, vectors, and vector profiles.
- Upload documents and compare keyword, vector, and hybrid retrieval.
- Explain why retrieval quality constrains grounded-answer quality.
- Create a Search knowledge source and knowledge base over an existing index.
- Connect a Foundry agent to `knowledge_base_retrieve` through MCP.
- Test missing evidence, conflicting revisions, and prompt injection in retrieved content.

## Prerequisites and Roles

Use a Search service in a region and tier that supports semantic ranking and knowledge bases. Configure these identities before the lab:

| Identity | Scope | Roles |
|---|---|---|
| Attendee | Search service | `Search Service Contributor`, `Search Index Data Contributor`, `Search Index Data Reader` |
| Attendee | Foundry parent resource/project | `Foundry User`, `Foundry Project Manager` |
| Foundry project managed identity | Search service | `Search Index Data Reader` |
| Search service managed identity | Foundry parent resource | `Cognitive Services User` or the role approved for embedding-model invocation |

The Search service and Foundry project must have system-assigned managed identities enabled. Role propagation can take several minutes.

## Step 1: Configure and Verify

Set the Lab 03 values in `.env`. Use unique resource names when teams share a Search service.

```powershell
python .\scripts\verify_setup.py --azure --lab-03
```

`AZURE_OPENAI_ENDPOINT` is the parent account endpoint used by the Search vectorizer. `FOUNDRY_EMBEDDING_MODEL_NAME` is its deployed embedding model name. The default schema assumes `text-embedding-3-small` with 1,536 dimensions; change both model and dimensions together.

## Part A: Learn Azure AI Search

### Step 2: Inspect the Corpus

Open `data/maintenance_documents.json`. Identify:

- The key field that uniquely identifies each chunk.
- Filterable metadata such as `asset_type` and `effective_date`.
- Two conflicting pump-procedure revisions.
- The untrusted vendor note containing an instruction aimed at the assistant.

### Step 3: Understand the Index Schema

Open `solution/search_helpers.py` and locate:

- Searchable text fields: `title` and `content`.
- Filterable/facetable fields for narrowing results.
- The `Collection(Edm.Single)` vector field and its dimensions.
- HNSW algorithm, vector profile, and Azure OpenAI vectorizer.
- The semantic configuration's title, content, and keyword fields.

The vectorizer converts query text at search time. The upload script explicitly generates document embeddings so learners can see when vectors enter the index.

### Step 4: Build, Upload, and Compare

Run:

```powershell
python .\lab-03-search-grounding\solution\01_build_and_search.py
```

Compare the ranked IDs:

| Mode | Retrieval signal | Useful when |
|---|---|---|
| Keyword | Terms and lexical scoring | Exact identifiers and terminology matter |
| Vector | Embedding similarity | User and document use different wording |
| Hybrid + semantic | Lexical and vector candidates, then semantic reranking | General enterprise question answering |

Open the Search explorer in the Azure portal and run a simple query such as `seal leak`. Add a filter such as `asset_type eq 'centrifugal_pump'`. Inspect scores and returned metadata; a high score is relevance evidence, not proof that a document is current or approved.

### Step 5: Complete the Starter Exercise

Open `starter/search_exercise.py`. Implement the three query modes, then compare your arguments with `build_query_arguments()` in the solution. Run the offline checks:

```powershell
python -m unittest tests.test_lab_03_search -v
```

## Part B: Add Foundry IQ

### Step 6: Create the Knowledge Path and Agent

Run:

```powershell
python .\lab-03-search-grounding\solution\02_foundry_iq_agent.py
```

The script creates or updates:

1. A Search index knowledge source.
2. A knowledge base that references the workshop knowledge source.
3. A Foundry `RemoteTool` project connection to the knowledge-base MCP endpoint.
4. A temporary prompt-agent version with only `knowledge_base_retrieve` allowed.

The agent version and conversation are deleted automatically. The index, knowledge source, knowledge base, and connection remain for inspection and reruns.

### Step 7: Evaluate Grounding Boundaries

The script asks three questions. Verify:

- **Supported evidence:** The answer uses the current pump procedure and cites it.
- **Missing evidence:** The exact coupling-bolt torque returns `I don't know`; no source contains it.
- **Prompt injection:** The vendor note is treated as untrusted content, not as an instruction or authorization.

Also ask the agent to compare revision 1 and revision 3. It should surface the conflict and effective dates instead of silently blending the procedures.

## Step 8: Clean Up

Delete Lab 03 knowledge resources and the project connection while retaining the index:

```powershell
python .\lab-03-search-grounding\solution\03_cleanup.py
```

Add `--delete-index` only when the index is not shared:

```powershell
python .\lab-03-search-grounding\solution\03_cleanup.py --delete-index
```

## Success Criteria

- [ ] Six documents are uploaded to the expected index.
- [ ] You can explain the candidate and ranking signals in all three query modes.
- [ ] Hybrid search sends both text and a vector query.
- [ ] The knowledge source points to the same index and semantic configuration.
- [ ] The agent invokes `knowledge_base_retrieve` and cites retrieved evidence.
- [ ] Missing, conflicting, and malicious evidence do not become unsupported claims.

## Key Distinction

Azure AI Search is the retrieval engine and index. Foundry IQ is the reusable knowledge layer built on Search. The agent reaches the knowledge base through MCP, but good instructions and citations do not repair a weak schema, stale corpus, incorrect permissions, or poor retrieval relevance.