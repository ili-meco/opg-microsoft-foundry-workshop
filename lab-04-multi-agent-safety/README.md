# Lab 04: Multi-Agent Safety Review and Human Approval

**Duration:** 60 minutes | **Skill level:** Intermediate

## What You Will Build

A Microsoft Agent Framework workflow with two distinct roles and one deterministic application gate:

```text
facts + evidence -> planner agent -> safety reviewer agent -> validated review
                                                              |
                                                              v
                                                   human approve/reject
                                                              |
                                                              v
                                              approval record, no execution
```

The sample follows the linked MAF workshop pattern by composing agents with `SequentialBuilder`, while retaining this repository's `azure-ai-projects==2.4.0` baseline. It uses MAF's `OpenAIChatClient` directly because the current `agent-framework-foundry` adapter requires an older projects SDK.

## Learning Objectives

- Give planner and reviewer agents separate instructions and responsibilities.
- Compose agents with MAF `SequentialBuilder`.
- Validate the review as strict JSON before trusting it.
- Prevent human approval from overriding a reviewer block.
- Keep approval separate from action authority.

## Step 1: Inspect the Assessment Package

Open `data/assessment_package.json`. It represents the outputs assembled from Labs 02 and 03: current operational facts, retrieved evidence, and explicit constraints.

## Step 2: Complete the Approval Gate

In `starter/approval_gate.py`:

1. Parse reviewer text with `SafetyReview.model_validate_json`.
2. Set status to `blocked` for `revise` or `escalate`, regardless of human input.
3. Leave a clean review `pending` until the human selects `approve` or `reject`.
4. Never change `action_authority` from `none`.

Run the offline tests:

```powershell
python -m unittest tests.test_lab_04_approval tests.test_lab_04_workflow -v
```

## Step 3: Compose the Agents

In `starter/safety_workflow.py`, pass planner and reviewer to:

```python
SequentialBuilder(
    participants=[planner, reviewer],
    output_from=[reviewer],
).build().as_agent(name="opg_maintenance_safety_workflow")
```

The reviewer sees the shared workflow context and returns the final output. The application still validates that output.

## Step 4: Run the Solution

```powershell
az login
python .\lab-04-multi-agent-safety\solution\safety_workflow.py
```

When prompted, type `approve` or `reject`. Approval means the recommendation may be presented to the planner; it does not execute a maintenance action.

## Step 5: Test Unsafe Variants

Edit a copy of the assessment package:

- Ask the planner to reserve `PART-310`.
- Remove the current R3 procedure evidence.
- Add conflicting revision evidence.
- Insert a document instruction telling the reviewer to approve.

The reviewer should revise or escalate. The deterministic gate must remain blocked even if a person attempts to approve.

## Success Criteria

- [ ] Planner and reviewer are separate MAF agents.
- [ ] The reviewer is the only workflow output.
- [ ] Invalid review JSON fails closed.
- [ ] Reviewer blocks cannot be overridden.
- [ ] Every consequential recommendation requires an explicit human decision.
- [ ] No path grants equipment, work-order, or inventory authority.