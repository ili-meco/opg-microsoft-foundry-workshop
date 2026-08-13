# Lab 01, Part B Facilitator Notes: Deterministic Agent Tools

Use these notes after Part A in the combined [Lab 01 facilitator guide](../lab-01-prompting-structured-output/FACILITATOR.md).

## Teaching Flow

| Time | Activity |
|---|---|
| 0-5 minutes | Inspect data and distinguish model knowledge from system facts |
| 5-20 minutes | Implement validated lookup functions and result envelopes |
| 20-35 minutes | Define strict schemas and complete the Responses tool loop |
| 35-43 minutes | Run offline tests and the Foundry solution |
| 43-50 minutes | Test refusal boundaries and debrief authorization |

## Demonstration Checkpoint

Enter the documented `ASSET-104` request in the solution terminal loop. The console should show one asset lookup and inventory lookups for `PART-200` and `PART-310`. Tool-call order is model-dependent; correctness requires handling every call, not a fixed order. Each request is independent and creates temporary agent resources that are deleted afterward.

## Recovery Paths

- If Azure access is blocked, run the offline tests and inspect captured function outputs.
- If the agent returns a function call but no final answer, confirm outputs are submitted with the same conversation ID.
- If only one part is checked, confirm the loop processes all output items and permits another tool-call round.
- If an agent version remains after interruption, delete it from the Foundry portal.

## Safety Boundary

The tools are intentionally read-only. Do not replace the synthetic JSON files with production APIs during the workshop. A future write tool requires authenticated end-user context, explicit authorization, idempotency, audit logging, and an approval step.