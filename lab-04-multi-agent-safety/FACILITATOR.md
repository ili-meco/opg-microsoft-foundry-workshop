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

- `SequentialBuilder` coordinates agent messages; it is not an authorization service.
- Reviewer output remains untrusted until Pydantic validates it.
- Human approval cannot repair missing evidence or an unsafe draft.
- `action_authority="none"` is deliberate because the workshop exposes no write tools.
- In production, identity, role checks, audit records, expiry, and idempotent write APIs belong outside the model.

## Recovery Checkpoint

Copy the two files from `solution/`, then run:

```powershell
python -m unittest tests.test_lab_04_approval tests.test_lab_04_workflow -v
```

## Live-Run Troubleshooting

- 401/403: rerun `az login` and confirm access to the Foundry project.
- Reviewer JSON validation failure: inspect the raw final workflow text and reinforce the JSON-only instruction.
- Model deployment not found: confirm `FOUNDRY_MODEL_NAME` uses the deployment name, not the catalog model name.