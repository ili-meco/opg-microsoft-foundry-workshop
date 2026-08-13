# Lab 04 Facilitator Guide

## Purpose

Participants build a three-agent workflow in which each agent creates a distinct artifact. The final model output answers one binary question: is the recommendation ready for a human decision?

## Timing

| Activity | Minutes |
|---|---:|
| Review the package and agent roles | 10 |
| Implement strict packet validation | 10 |
| Implement the readiness guard | 10 |
| Compose the MAF workflow | 15 |
| Run unsafe variants and debrief | 15 |

## Key Teaching Points

- The evidence analyst separates facts, current evidence, conflicts, and gaps; it does not recommend actions.
- The planner drafts from the evidence packet; it does not approve its own work.
- The reviewer checks the packet and draft; it returns `ready_for_human`, not a second recommendation workflow.
- `SequentialBuilder` controls order and message flow but grants no authority.
- Reviewer output remains untrusted until Pydantic validates it.
- `ready_for_human=false` means no human decision is accepted for that packet.
- Findings explain whether correction, more evidence, or expert help is needed; those explanations are not application states.
- Human approval records acceptance of a recommendation and still leaves `action_authority="none"`.
- Production systems also need identity, role checks, durable audit records, expiry, and idempotent write APIs outside the model.

## Suggested Debrief

Ask participants to classify each component:

| Component | Classification | Reason |
|---|---|---|
| Evidence analyst | Agent | Uses a model to normalize evidence into a bounded artifact. |
| Maintenance planner | Agent | Uses a model to synthesize an evidence-based draft. |
| Safety reviewer | Agent | Uses a model to assess readiness independently. |
| `SequentialBuilder` | Orchestrator | Controls order and message flow. |
| `HumanReviewPacket` | Validated contract | Constrains the final model output. |
| `record_human_decision()` | Deterministic policy | Rejects human input when readiness is false. |
| Human approver | Accountable decision-maker | Approves or rejects a reviewer-cleared recommendation. |

Emphasize that adding agents is not itself a safety property. The value comes from narrow responsibilities, inspectable artifacts, strict validation, and deterministic policy at the human boundary.

## Recovery Checkpoint

Copy the two files from `solution/`, then run:

```powershell
python -m unittest tests.test_lab_04_approval tests.test_lab_04_workflow -v
```

## Live-Run Troubleshooting

- Incorrect token audience: request `https://ai.azure.com/.default`.
- `/v1` rejects `api-version`: pass the provider through `OpenAIChatClient(api_key=...)`.
- Token string cannot be awaited: return the async wrapper from `foundry_token_provider()`.
- Missing or expired token after checking code: rerun `az login`.
- HTTP 403: confirm access to the Foundry project and deployment.
- Invalid reviewer JSON: inspect the raw final text and reinforce the JSON-only contract.
- Deployment not found: use the deployment name, not the catalog model name.