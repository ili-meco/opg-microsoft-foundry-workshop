# Lab 03 Facilitator Guide

## Teaching Flow

| Time | Activity |
|---|---|
| 0-15 minutes | Explain the three endpoint/ID values and verify configuration |
| 15-25 minutes | Inspect the six-document corpus and identify trust problems |
| 25-40 minutes | Create the index, validate embeddings, and upload documents |
| 40-60 minutes | Complete the query TODOs and compare interactive results |
| 60-72 minutes | Explain and create the Foundry IQ knowledge path |
| 72-87 minutes | Test supported, missing, conflicting, and malicious evidence |
| 87-90 minutes | Clean up and connect retrieval quality to evaluation |

For a portal-led delivery, use `02_foundry_iq_agent.py --setup-only` at 60 minutes. Learners then inspect **Build** > **Knowledge**, create an agent under **Build** > **Agents**, paste the workshop instructions, connect their knowledge base, and test in the playground. Allow an additional 10-15 minutes if every participant completes both the Python and portal paths.

## Workshop Resource Standard

- Use `Sweden Central` for Search and Foundry unless model capacity requires another region.
- Use the Search `Basic` tier because this lab depends on managed identity.
- Predeploy `text-embedding-3-small` and confirm its default 1,536 dimensions.
- Enable system-assigned identities on Search and Foundry.
- Assign all roles with a non-admin test identity before the workshop.
- Give teams unique suffixes for index, source, base, connection, and agent names.
- Run index setup, interactive Search, Foundry IQ, and cleanup end to end.

Do not describe `FOUNDRY_EMBEDDING_ENDPOINT` as a separate Azure OpenAI resource. It is the parent Foundry resource's model-serving endpoint. Python uses its OpenAI v1 route for document embeddings, and Search uses it for query vectorization. Keep the project-scoped endpoint, parent endpoint, and ARM resource ID visible together while explaining their different API surfaces.

## Expected Retrieval Pattern

For the default pump question, the current `PROC-PUMP-017-R3` document should rank near the top. Exact ordering can vary. Ask learners why the obsolete R1 record can still rank highly: retrieval relevance and document authority are separate concerns.

## Recovery Paths

- If model capacity blocks Sweden Central, use another region only after confirming agentic retrieval, semantic ranker, and both model deployments.
- If embedding upload is blocked, provide a prebuilt per-team index and begin with direct queries.
- If query vectorization returns 403, verify the Search managed identity can invoke the embedding model on the Foundry parent resource.
- If document upload reports a dimension mismatch, restore `text-embedding-3-small` and `FOUNDRY_EMBEDDING_DIMENSIONS=1536`.
- If MCP retrieval returns 403, verify the Foundry project managed identity has `Search Index Data Reader`.
- If the portal asks for a knowledge-base chat model, set retrieval reasoning to `Minimal` and output to `Extracted data`. The workshop agent model produces the final answer.
- If a portal-created agent does not retrieve, confirm its Knowledge section points to the participant's suffixed knowledge base and that `knowledge_base_retrieve` is available.
- If project connection creation returns 403, verify the attendee has `Foundry Project Manager`.
- If semantic search fails, verify semantic ranker is enabled and the configured name is `maintenance-semantic`.
- If the service does not support knowledge bases, complete Part A and demonstrate Part B from an instructor service.

## Safety Discussion

The corpus intentionally contains superseded and malicious content. Metadata, ingestion governance, approval state, access control, and agent instructions all matter. Prompt text alone is not a security boundary.