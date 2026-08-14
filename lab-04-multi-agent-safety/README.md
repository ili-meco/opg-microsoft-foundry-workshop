# Lab 04: Multi-Agent Evidence, Planning, and Safety Review

**Duration:** 60 minutes | **Skill level:** Intermediate

## Your Part In The User Story

> As the authorized OPG reviewer, I want to see the evidence, proposed next steps, missing information, and safety concerns in one clear package so that I can make an informed decision about the recommendation.

**You build:** A three-step workflow in which the evidence analyst organizes what is known and missing, the maintenance planner uses that evidence to propose next steps, and the safety reviewer checks whether the package is complete and safe enough to show to a person.

**Why it matters:** The AI agents prepare and check the recommendation, but they cannot approve it. Only an authorized person can approve or reject a complete package, and that decision does not itself start or authorize maintenance work.

The human title is intentionally generic for the workshop and must be mapped to OPG's actual accountable role and process before production use. This is the human-review increment of the [complete workshop user story](../docs/WORKSHOP-USER-STORY.md).

## What You Will Build

A Microsoft Agent Framework workflow in which each agent creates one distinct artifact:

```text
assessment package
       |
       v
evidence analyst -> EvidencePacket
       |
       v
maintenance planner -> draft recommendation
       |
       v
safety reviewer -> HumanReviewPacket
                         |
                  ready_for_human?
                    no       yes
                    |         |
             show findings   human approve/reject
                              |
                              v
                    HumanDecisionRecord
```

There is no model-owned approval state machine. The reviewer answers one question:

> Is this recommendation ready to be shown to a human for a decision?

If `ready_for_human` is `false`, the application displays the findings and stops. If it is `true`, a person may record `approve` or `reject`. Neither choice executes maintenance work.

### Evidence Analyst Versus Maintenance Planner

The simplest distinction is:

> The evidence analyst explains **what the available information tells us**. The maintenance planner proposes **what should be considered next based on that information**.

For the fictional `ASSET-104` issue:

| Role | Question it answers | Example output |
|---|---|---|
| Evidence analyst | What do the records support, contradict, or leave unanswered? | The pump has a reported seal leak; the retrieved procedures conflict on revision; the latest vibration reading is missing. |
| Maintenance planner | Given that evidence and uncertainty, what should the authorized reviewer consider doing next? | Verify the current procedure revision and obtain the missing vibration reading before deciding whether to schedule maintenance. |

The evidence analyst does not recommend work. The planner does not reopen the raw records, invent missing facts, or decide whether work is approved. Keeping the roles separate makes it possible for the safety reviewer to compare the recommendation with the evidence that was actually available.

The workflow uses `SequentialBuilder` with the repository's pinned Agent Framework packages. `FoundryChatClient` provides the native Microsoft Foundry project, credential, and model integration.

## Why Three Agents?

The agents do different jobs and produce different artifacts:

| Agent | Receives | Produces | Must not do |
|---|---|---|---|
| Evidence analyst | Operational facts, retrieved documents, and constraints | An `EvidencePacket` separating supported facts, current sources, conflicts, and gaps | Recommend work, resolve missing values, or authorize actions |
| Maintenance planner | The evidence packet | A draft recommendation that preserves uncertainty and citations | Invent evidence, approve work, reserve inventory, or control equipment |
| Safety reviewer | The evidence packet and planner draft | A strict `HumanReviewPacket` with `ready_for_human`, findings, recommendation, and citations | Redo the analysis, silently fix the draft, or make the human decision |

The deterministic application code has one policy rule: a human decision cannot be recorded when `ready_for_human` is `false`.

### Why Add the Evidence Analyst?

The raw assessment package mixes observations, retrieved text, metadata, constraints, and missing information. The evidence analyst normalizes that input before anyone recommends an action. This gives the planner a smaller, more explicit context and gives the reviewer an artifact against which to check the draft.

The evidence analyst is not a search agent in this lab. Lab 03 already retrieved the sources. Its job is evidence triage:

- Separate current observations from retrieved claims.
- Preserve source titles and revisions.
- Identify conflicting or superseded evidence.
- List missing information rather than inventing it.
- Treat retrieved text as data, not as instructions.

### Why Keep the Planner Separate?

The planner converts the evidence packet into useful maintenance language. It can synthesize supported facts and propose planner-facing next steps, but it cannot approve its own draft. Each consequential recommendation carries a `[Source: title, revision]` citation. Its output remains a proposal and begins with `PLANNER_DRAFT` so the reviewer can identify it in the shared sequential conversation.

### Why Use a Binary Reviewer Output?

The earlier design asked the reviewer to choose `approve`, `revise`, or `escalate`, then asked Python to translate that choice into a second status. That created two vocabularies for the same handoff.

This design removes the translation:

```text
ready_for_human = false -> display findings and stop
ready_for_human = true  -> ask a human to approve or reject
```

Findings explain whether the next step is correction, more evidence, or expert escalation. They do not need to become application states in this lab.

## Learning Objectives

- Give each agent one distinct objective and artifact.
- Compose three agents with MAF `SequentialBuilder`.
- Validate the final model output as strict JSON.
- Gate human input with one deterministic readiness check.
- Keep human approval separate from action authority.

## Step 1: Inspect the Assessment Package

Open `data/assessment_package.json`. Identify:

1. Current equipment observations.
2. Retrieved source titles, revisions, effective dates, and content.
3. Operational and authority constraints.
4. Missing values or unresolved conflicts.

The evidence analyst receives this package first. The planner should work from the resulting evidence packet rather than independently interpreting the raw package.

## Step 2: Complete the Human Review Boundary

Open `starter/approval_gate.py`.

### TODO 1: Parse the Review Packet

Implement `parse_review_packet()` with Pydantic's JSON validation for `HumanReviewPacket`.

- Validate the raw string directly.
- Do not remove Markdown fences or extract a JSON-looking substring.
- Let `extra="forbid"` reject unknown fields.
- Require `requires_human_decision` to be exactly `true`.
- Require `action_authority` to remain `none`.

Malformed or embellished model output must fail closed.

### TODO 2: Enforce Readiness

Implement the single policy check in `record_human_decision()`:

```text
if ready_for_human is false:
    reject the attempt to record a human decision
```

Raise `ValueError` when the packet is not ready. Do not ask another model to reinterpret the findings, and do not allow a supplied `approve` value to bypass the check.

### TODO 3: Record the Human Decision

For a ready packet, return `HumanDecisionRecord` with:

- The human's `approve` or `reject` decision.
- The reviewed recommendation.
- Findings and citations.
- `action_authority="none"`.

There is no `pending`, `blocked`, `revision_required`, or `escalation_required` status. Before the human decides, the validated `HumanReviewPacket` is the artifact. After the human decides, `human_decision` is the result.

Run:

```powershell
python -m unittest tests.test_lab_04_approval -v
```

## Step 3: Compose the Three Agents

Open `starter/safety_workflow.py`. Authentication and agent instances are already implemented.

### TODO 1: Fix the Execution Order

Create a `SequentialBuilder` with:

```python
participants=[analyst, planner, reviewer]
```

Order is behavior:

1. The analyst creates the evidence packet.
2. The planner drafts from that packet.
3. The reviewer compares the draft with the evidence packet.

### TODO 2: Choose the Trusted Output

Set:

```python
output_from=[reviewer]
```

Only the reviewer's `HumanReviewPacket` may leave the orchestration. Returning the analyst or planner output would bypass the final review.

### TODO 3: Build the Workflow

Build and expose the workflow:

```python
return SequentialBuilder(
    participants=[analyst, planner, reviewer],
    output_from=[reviewer],
).build().as_agent(name="opg_maintenance_safety_workflow")
```

`.as_agent(...)` provides an agent-compatible interface; it does not create a fourth specialist.

Run the offline tests:

```powershell
python -m unittest tests.test_lab_04_approval tests.test_lab_04_workflow -v
```

## Step 4: Understand the Foundry Client

The starter uses:

```python
FoundryChatClient(
       project_endpoint=project_endpoint,
       model=model_name,
       credential=credential,
)
```

`FoundryChatClient` is the Microsoft Agent Framework integration for a Foundry project. It accepts the project endpoint and Azure credential directly, then owns the correct Foundry authentication and model-client routing. Keeping this integration behind `build_foundry_chat_client()` makes the workflow easy to test without replacing the real client in production code.

## Step 5: Run the Solution

```powershell
az login
python .\lab-04-multi-agent-safety\solution\safety_workflow.py
```

For a ready packet, enter `approve` or `reject`. For an unready packet, the program prints the findings and exits without prompting.

Approval records a recommendation decision only. The workflow has no tools for equipment control, work-order updates, or inventory changes.

## Step 6: Test Unsafe Variants

Edit a copy of the assessment package:

- Ask the planner to reserve `PART-310`.
- Remove the current R3 procedure evidence.
- Add conflicting revision evidence.
- Insert retrieved text telling later agents to ignore their instructions.

For each unsafe variant, expect:

```text
ready_for_human = false
findings = [specific evidence, safety, or authority problem]
action_authority = none
```

## Troubleshooting

- HTTP 401: rerun `az login` and confirm the signed-in identity has access to the Foundry project.
- Project endpoint error: use the full project endpoint ending in `/api/projects/<project-name>`.
- Reviewer JSON validation failure: inspect the raw final workflow text and reinforce the JSON-only contract.
- Model deployment not found: use the deployment name in `FOUNDRY_MODEL_NAME`.

## Success Criteria

- [ ] Analyst, planner, and reviewer are separate MAF agents.
- [ ] Each agent has one distinct artifact and responsibility.
- [ ] The reviewer is the only workflow output.
- [ ] Invalid review JSON fails closed.
- [ ] An unready packet cannot receive a human decision.
- [ ] Every ready recommendation requires explicit human approval or rejection.
- [ ] No path grants equipment, work-order, or inventory authority.