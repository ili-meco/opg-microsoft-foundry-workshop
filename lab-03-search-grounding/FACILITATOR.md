# Lab 03 Facilitator Guide

## Teaching Flow

| Time | Activity |
|---|---|
| 0-10 minutes | Verify Search, model, identities, and role assignments |
| 10-25 minutes | Inspect the corpus and design the index schema |
| 25-45 minutes | Create the index, upload vectors, and compare retrieval modes |
| 45-55 minutes | Use Search explorer and discuss relevance versus authority |
| 55-70 minutes | Create the knowledge source, knowledge base, and MCP connection |
| 70-85 minutes | Test supported, missing, conflicting, and malicious evidence |
| 85-90 minutes | Clean up and connect retrieval quality to evaluation |

## Preflight

- Predeploy a `text-embedding-3-small` deployment and confirm its 1,536 dimensions.
- Enable semantic ranker and system-assigned identities on Search and Foundry.
- Assign all roles with a non-admin test identity before the workshop.
- Give teams unique suffixes for index, source, base, connection, and agent names.
- Run both solution scripts end to end in the workshop region.

## Expected Retrieval Pattern

For the default pump question, the current `PROC-PUMP-017-R3` document should rank near the top. Exact ordering can vary. Ask learners why the obsolete R1 record can still rank highly: retrieval relevance and document authority are separate concerns.

## Recovery Paths

- If embedding upload is blocked, provide a prebuilt index and begin with direct queries.
- If query vectorization returns 403, verify the Search managed identity can invoke the embedding model on the Foundry parent resource.
- If MCP retrieval returns 403, verify the Foundry project managed identity has `Search Index Data Reader`.
- If project connection creation returns 403, verify the attendee has `Foundry Project Manager`.
- If semantic search fails, verify semantic ranker is enabled and the configured name is `maintenance-semantic`.
- If the service does not support knowledge bases, complete Part A and demonstrate Part B from an instructor service.

## Safety Discussion

The corpus intentionally contains superseded and malicious content. Metadata, ingestion governance, approval state, access control, and agent instructions all matter. Prompt text alone is not a security boundary.