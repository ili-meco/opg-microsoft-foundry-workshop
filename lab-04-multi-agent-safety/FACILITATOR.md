# Lab 04 Facilitator Guide

## Purpose

Participants learn that adding another agent is useful only when roles and control boundaries are explicit. The reviewer supplies a safety opinion; Python owns the approval state machine.

## Timing

| Activity | Minutes |
|---|---:|
| Review the package and roles | 10 |
| Implement the approval gate | 15 |
| Compose the MAF workflow | 15 |
| Run unsafe variants | 15 |
| Debrief | 5 |

## Key Teaching Points

- The planner exists to synthesize evidence into a draft; it does not review or approve its own recommendation.
- The reviewer exists to challenge the draft against evidence, safety, and authority boundaries; it does not redo the planning task.
- Ask participants to name the distinct objective before proposing another agent. A new agent without a separate objective or boundary adds cost without adding a meaningful control.
- `SequentialBuilder` coordinates agent messages; it is not an authorization service.
- `.as_agent(...)` exposes the composed workflow through an agent interface; it does not create a third specialist role.
- Reviewer output remains untrusted until Pydantic validates it.
- Human approval cannot repair missing evidence or an unsafe draft.
- `action_authority="none"` is deliberate because the workshop exposes no write tools.
- In production, identity, role checks, audit records, expiry, and idempotent write APIs belong outside the model.

## Suggested Role Debrief

Ask the room to classify each component before showing the answer:

| Component | Classification | Reason |
|---|---|---|
| Maintenance planner | Agent | Uses a model to synthesize an evidence-based draft. |
| Safety reviewer | Agent | Uses a model with an independent critique objective. |
| `SequentialBuilder` workflow | Orchestrator | Controls order and message flow but does not authorize outcomes. |
| Pydantic review model | Validator | Rejects malformed or incomplete model output. |
| Approval gate | Deterministic policy | Owns allowed state transitions and fails closed. |
| Human approver | Accountable decision-maker | May approve a clean pending recommendation but cannot override a block. |

Emphasize that multi-agent is an architectural choice, not a safety property. Safety comes from narrow roles plus deterministic validation, policy enforcement, identity, and audit controls.

## Recovery Checkpoint

Copy the two files from `solution/`, then run:

```powershell
python -m unittest tests.test_lab_04_approval tests.test_lab_04_workflow -v
```

## Live-Run Troubleshooting

- 401/403: rerun `az login` and confirm access to the Foundry project.
- Reviewer JSON validation failure: inspect the raw final workflow text and reinforce the JSON-only instruction.
- Model deployment not found: confirm `FOUNDRY_MODEL_NAME` uses the deployment name, not the catalog model name.