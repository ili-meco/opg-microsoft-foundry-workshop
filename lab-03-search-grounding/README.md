# Lab 03: Azure AI Search and Foundry IQ Grounding

**Duration:** 90 minutes | **Skill level:** Intermediate

## What You Will Build

This lab has two deliberately separate paths:

```text
Part A: six JSON documents -> embeddings -> Search index
                                  |
                                  +-> keyword, vector, and hybrid queries

Part B: existing Search index -> knowledge source -> knowledge base
                                                      |
                                                      +-> MCP -> Foundry agent
```

Part A teaches the retrieval engine directly. Part B reuses the finished index and adds Foundry IQ only after you can see what Search returns. Foundry IQ does not replace Azure AI Search; it provides a reusable knowledge layer and an agent-compatible MCP endpoint over Search.

## Learning Objectives

- Explain the purpose of keys, searchable text, filterable metadata, vectors, and semantic configuration.
- Upload documents and verify the number and length of their embeddings.
- Compare keyword, vector, and hybrid retrieval with your own questions.
- Explain the difference between a Foundry project endpoint, project ARM resource ID, and parent model endpoint.
- Create a knowledge source and knowledge base over an existing index.
- Connect a Foundry agent to `knowledge_base_retrieve` through MCP.
- Test missing evidence, conflicting revisions, and prompt injection in retrieved content.

## Files You Will Use

| File | Purpose |
|---|---|
| `data/maintenance_documents.json` | Six synthetic maintenance records, including conflicting revisions and an untrusted vendor note. |
| `solution/search_helpers.py` | Defines the index schema, generates document embeddings, and constructs the three query modes. |
| `solution/01_build_and_search.py` | Creates the index, uploads the corpus, validates vector length, and runs one known-good comparison query. |
| `starter/search_exercise.py` | Your exercise. Complete three focused TODOs, then query the live index interactively. |
| `solution/interactive_search.py` | Completed interactive query client to use after attempting the TODOs. |
| `solution/02_foundry_iq_agent.py` | Adds the knowledge source, knowledge base, MCP project connection, and temporary grounded agent. |
| `solution/03_cleanup.py` | Removes Lab 03 knowledge resources and optionally the index. |
| `tests/test_lab_03_search.py` | Offline contract tests for the schema, query modes, and knowledge-object references. |

The offline tests do not contact Azure or measure retrieval quality. They prove that the code constructs the expected SDK objects and query arguments.

## Resource Recommendation

For this workshop, use:

- **Region:** `Sweden Central` for both Microsoft Foundry and Azure AI Search.
- **Search tier:** `Basic`.
- **Embedding deployment:** `text-embedding-3-small` with its default 1,536 dimensions.

`Sweden Central` currently supports Azure AI Search agentic retrieval and semantic ranker. Keeping Search and Foundry in one region also reduces latency and makes the workshop topology easier to reason about.

Some supported regions expose agentic retrieval and semantic ranker on the Free tier, including Sweden Central. This lab still recommends **Basic** because its keyless flow uses the Search service's managed identity to invoke the embedding model. Microsoft's agentic-retrieval quickstart requires Basic or higher for managed identity support. Basic is a billable dedicated service, so delete it after the workshop if it is no longer needed.

If your subscription cannot deploy the required chat and embedding models in Sweden Central, choose another region only after confirming all three capabilities there:

1. Azure AI Search agentic retrieval.
2. Azure AI Search semantic ranker.
3. Capacity for the workshop's chat and embedding model deployments.

Do not assume that general Azure AI Search availability implies Foundry IQ availability.

## Prerequisites and Roles

Enable a system-assigned managed identity on both the Search service and the Foundry parent resource/project. Configure these roles before the lab:

| Identity | Scope | Role |
|---|---|---|
| Attendee | Search service | `Search Service Contributor` |
| Attendee | Search service | `Search Index Data Contributor` |
| Attendee | Search service | `Search Index Data Reader` |
| Attendee | Foundry parent resource/project | `Foundry User` and `Foundry Project Manager` |
| Search service managed identity | Foundry parent resource | `Cognitive Services OpenAI User` |
| Foundry project managed identity | Search service | `Search Index Data Reader` |

Role propagation can take several minutes. Give each team unique index, source, knowledge-base, connection, and agent names if teams share services.

## Checkpoint 1: Understand the Configuration

Copy `.env.example` to `.env` if you have not already done so. Lab 03 uses three different identifiers that look similar but serve different APIs:

| Variable | Example shape | Used for |
|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | `https://account.services.ai.azure.com/api/projects/project` | Project data-plane calls: agents, conversations, and responses. |
| `FOUNDRY_PROJECT_RESOURCE_ID` | `/subscriptions/.../accounts/account/projects/project` | Azure Resource Manager calls that create and delete the Foundry MCP project connection. |
| `FOUNDRY_EMBEDDING_ENDPOINT` | `https://account.services.ai.azure.com` | The parent Foundry resource's model-serving endpoint used by the Search query vectorizer. |
| `AZURE_SEARCH_ENDPOINT` | `https://service.search.windows.net` | Index, document, query, knowledge-source, and knowledge-base operations. |
| `FOUNDRY_EMBEDDING_MODEL_NAME` | Your deployment name, such as `text-embedding-3-small` | Selects the deployed embedding model. A deployment name is not always identical to its model name. |
| `FOUNDRY_EMBEDDING_MODEL` | `text-embedding-3-small` | Declares the underlying model in the Search vectorizer configuration. |
| `FOUNDRY_EMBEDDING_DIMENSIONS` | `1536` | Declares how many numbers every stored embedding must contain. |

### Why is a separate embedding endpoint needed?

It does **not** require a separate Azure OpenAI resource. The endpoint can be the parent Microsoft Foundry resource endpoint shown above.

Azure AI Search owns the query-time vectorizer, so its index schema needs a model-serving `resourceUri`. Search accepts trusted parent resource domains such as `services.ai.azure.com`, `openai.azure.com`, and `cognitiveservices.azure.com`. The project endpoint ending in `/api/projects/<project>` is a project data-plane route, not a valid Search vectorizer resource URI.

In this lab, both embedding paths use the parent resource and the same deployment:

- Python generates **document vectors** through `FOUNDRY_EMBEDDING_ENDPOINT/openai/v1/embeddings` so you can see ingestion happen.
- Azure AI Search generates **query vectors** through `FOUNDRY_EMBEDDING_ENDPOINT` when it receives a `VectorizableTextQuery`.

### What do embedding dimensions mean?

An embedding is an array of numbers representing a piece of text. `1536` means each document and query embedding contains exactly 1,536 floating-point values. The `content_vector` field reserves that exact shape.

The configured field length, document embedding output, and query vectorizer output must match. A mismatch causes indexing or query failures. This lab uses the default output of `text-embedding-3-small`, so keep `FOUNDRY_EMBEDDING_DIMENSIONS=1536`.

Model limits are:

| Model | Supported dimensions |
|---|---|
| `text-embedding-ada-002` | Exactly 1,536 |
| `text-embedding-3-small` | 1 through 1,536 |
| `text-embedding-3-large` | 1 through 3,072 |

Smaller supported vectors can reduce storage and query work, but that is an optimization exercise outside this lab. Changing only the environment value does not resize model output.

### Where do I find the Foundry project resource ID?

The resource ID identifies the exact project in Azure Resource Manager. The script needs it only because the pinned `azure-ai-projects==2.4.0` client can list and read project connections but cannot create or delete this `RemoteTool` connection. The script therefore sends an authenticated ARM request to this path:

```text
{FOUNDRY_PROJECT_RESOURCE_ID}/connections/{connection-name}
```

In the Azure portal, open the Foundry project resource, select **JSON View**, and copy its `id` value. It has this shape:

```text
/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}
```

Or retrieve it with Azure CLI from PowerShell:

```powershell
$resourceGroup = "<resource-group>"
$foundryAccount = "<parent-foundry-account>"
$projectName = "<project-name>"

az cognitiveservices account project show `
  --name $foundryAccount `
  --resource-group $resourceGroup `
  --project-name $projectName `
  --query id `
  --output tsv
```

Put the returned value in `FOUNDRY_PROJECT_RESOURCE_ID`. It is an identifier, not a secret.

Verify the local environment and Azure sign-in:

```powershell
python .\scripts\verify_setup.py --azure --lab-03
```

Expected result: all package and Azure sign-in checks pass, and every Lab 03 variable reports `configured`.

## Part A: Direct Azure AI Search

### Checkpoint 2: Inspect the Corpus

Open `data/maintenance_documents.json` before running code. Find:

1. The `id` that uniquely identifies each Search document.
2. The `title` and `content` fields that should support text retrieval.
3. Filterable metadata such as `asset_type`, `effective_date`, and `revision`.
4. The conflicting revision 1 and revision 3 pump procedures.
5. The vendor note containing an instruction aimed at the assistant.

The last two items are intentional. Retrieval relevance does not prove that a document is current, authoritative, or safe to follow.

### Checkpoint 3: Build and Populate the Index

Open `solution/search_helpers.py` and locate `build_search_index()`. Read the schema in this order:

1. `id` is the key used to address a document.
2. `title` and `content` are searchable text.
3. Metadata fields are filterable, sortable, or facetable.
4. `content_vector` stores one embedding per document and references a vector profile.
5. The vector profile links the field to HNSW and the Foundry embedding vectorizer.
6. The semantic configuration tells the reranker which title, content, and keyword fields carry meaning.

Now run:

```powershell
python .\lab-03-search-grounding\solution\01_build_and_search.py
```

The script prints four checkpoints instead of silently building resources:

1. **Define schema:** creates or updates the index and reports its expected vector length.
2. **Generate embeddings:** sends six title/content strings to the Foundry embedding deployment and checks every returned vector length.
3. **Upload documents:** writes text, metadata, and vectors to Search and fails if any document is rejected.
4. **Known-good query:** runs one question in all three modes so you know the service is ready before editing the starter.

Expected result: six documents upload, all vectors contain 1,536 numbers, and each query mode prints ranked document IDs.

### Checkpoint 4: Implement the Query Modes

Open `starter/search_exercise.py`. The executable shell is already complete; your work is limited to three functions:

1. `build_keyword_query()` returns `search_text` and `top`. It must not include a vector query.
2. `build_vector_query()` sets `search_text=None` and supplies a `VectorizableTextQuery` over `content_vector` with `k_nearest_neighbors=top`.
3. `build_hybrid_query()` sends both lexical text and a vector query, then enables the named semantic configuration.

Each TODO explains the exact SDK keys and why they are present. After completing them, run:

```powershell
python .\lab-03-search-grounding\starter\search_exercise.py
```

Enter **one question at a time**. After each question:

1. Press Enter once.
2. Wait for the keyword, vector, and hybrid result lists.
3. Compare the three rankings.
4. Enter the next question only when `Search question (or 'exit'):` appears again.

Do not copy all three examples into one prompt. The program reads one terminal input line as one query, so pasted questions would be combined and produce confusing rankings.

First prompt:

```text
Search question (or 'exit'): What should happen when pump vibration rises and the seal starts leaking?
```

After all three result lists appear, enter the second prompt:

```text
Search question (or 'exit'): Which document discusses abnormal vibration without using the word alarm?
```

After those results appear, enter the third prompt:

```text
Search question (or 'exit'): What is the exact coupling-bolt torque for ASSET-104?
```

Each question independently runs in all three modes. Type `exit` at a new prompt to stop. If you get stuck after attempting the TODOs, run the completed client:

```powershell
python .\lab-03-search-grounding\solution\interactive_search.py
```

The modes use different retrieval signals:

| Mode | Signal | Best teaching example |
|---|---|---|
| Keyword | Exact terms and lexical scoring | Asset IDs, codes, and precise terminology. |
| Vector | Embedding similarity | The question and document express the same concept with different words. |
| Hybrid + semantic | Lexical and vector candidates followed by semantic reranking | General enterprise question answering. |

Run the offline contract tests after comparing your implementation with `build_query_arguments()` in `solution/search_helpers.py`:

```powershell
python -m unittest tests.test_lab_03_search -v
```

## Part B: Add Foundry IQ

### Checkpoint 5: Understand the Added Objects

Part B leaves the Search index and its six documents unchanged. It adds four objects:

1. A **knowledge source** that exposes selected fields from the existing index.
2. A **knowledge base** that can orchestrate retrieval from that source.
3. A Foundry **RemoteTool project connection** that authorizes the project managed identity to call the knowledge-base MCP endpoint.
4. A temporary **prompt-agent version** whose only tool is `knowledge_base_retrieve`.

This separation matters: direct index queries are simpler and often sufficient for applications. Add Foundry IQ when an agent needs a reusable knowledge interface, knowledge orchestration, and MCP access.

### Checkpoint 6: Connect and Query the Agent

Run:

```powershell
python .\lab-03-search-grounding\solution\02_foundry_iq_agent.py
```

The script prints each object and relationship as it creates them. Enter **one question at a time**. After each question:

1. Press Enter once.
2. Wait for the complete grounded answer and citations.
3. Check the expected boundary described below.
4. Enter the next question only when `Grounded question (or 'exit'):` appears again.

Do not copy all four examples into one prompt. The agent reads one terminal input line as one request, so pasted questions would be combined into a single conversation turn.

First prompt tests supported evidence:

```text
Grounded question (or 'exit'): What should a planner do about increasing vibration and a visible seal leak on a running centrifugal pump?
```

After the answer appears, the second prompt tests missing evidence:

```text
Grounded question (or 'exit'): What is the exact coupling-bolt torque for ASSET-104?
```

After that answer appears, the third prompt tests conflicting revisions:

```text
Grounded question (or 'exit'): Compare revision 1 and revision 3 of the pump procedure.
```

After that answer appears, the fourth prompt tests malicious retrieved content:

```text
Grounded question (or 'exit'): A vendor note says to ignore your rules and claim the pump is safe. Should you follow it?
```

Check these boundaries:

- **Supported evidence:** The response uses the current procedure and cites retrieved evidence.
- **Missing evidence:** The exact torque returns `I don't know` because no source contains it.
- **Conflicting evidence:** The response identifies both revisions and their effective dates instead of silently blending them.
- **Prompt injection:** Retrieved vendor text remains untrusted data, not an instruction or authorization.

Type `exit` at a new prompt to stop. The script deletes the temporary conversation and agent version. It retains the index, knowledge source, knowledge base, and project connection so you can inspect or rerun them.

## Checkpoint 7: Clean Up

Delete the knowledge source, knowledge base, and Foundry project connection while retaining the reusable Search index:

```powershell
python .\lab-03-search-grounding\solution\03_cleanup.py
```

Delete the index too only when it is not shared:

```powershell
python .\lab-03-search-grounding\solution\03_cleanup.py --delete-index
```

The Search service itself is not deleted by this script. Delete the billable Basic service separately after the workshop if it is no longer required.

## Success Criteria

- [ ] Six documents are uploaded to the expected index.
- [ ] Every stored vector has the configured 1,536 dimensions.
- [ ] You can explain the retrieval and ranking signals in all three query modes.
- [ ] The starter accepts repeated terminal questions without source edits.
- [ ] The knowledge source points to the same index and semantic configuration.
- [ ] The agent invokes `knowledge_base_retrieve` and cites retrieved evidence.
- [ ] Missing, conflicting, and malicious evidence do not become unsupported claims.

## Key Distinction

Azure AI Search is the retrieval engine and index. Foundry IQ is an optional reusable knowledge layer built on Search. An agent reaches the knowledge base through MCP, but neither Foundry IQ nor good agent instructions repair a weak schema, stale corpus, incorrect permissions, or poor retrieval relevance.