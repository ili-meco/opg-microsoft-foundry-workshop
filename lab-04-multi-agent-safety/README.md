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

## Why Add More Than One Agent?

Lab 03 used one grounded agent to retrieve evidence and answer a question. Lab 04 adds two agents because drafting a maintenance recommendation and independently challenging that recommendation are different jobs. Each role gets a narrower instruction set, a clear output responsibility, and no authority to perform maintenance actions.

The goal is not to make the workflow safe merely by increasing the agent count. The separation makes each responsibility visible and testable:

| Component | Purpose | Receives | Produces | Must not do |
|---|---|---|---|---|
| Maintenance planner agent | Converts the assessment package into a useful draft for a maintenance planner. It organizes facts, evidence, uncertainty, and suggested next steps. | Operational facts, retrieved evidence, and constraints from `assessment_package.json`. | A draft evidence-based recommendation for review. | Approve work, update work orders, reserve parts, control equipment, or treat retrieved text as instructions. |
| Safety reviewer agent | Challenges the planner's draft from an independent role before a person sees an approvable recommendation. It checks support, recency, conflicts, unsafe direction, and claims of authority. | The original workflow context and the planner's draft. | One strict JSON review with a decision, findings, blocked actions, reviewed recommendation, citations, and a human-approval requirement. | Repeat the planner task, silently repair missing evidence, authorize actions, or return free-form prose. |
| Sequential orchestrator | Runs the roles in a fixed order and passes workflow context from planner to reviewer. | The assessment package and participant definitions. | The reviewer's message as the workflow output. | Decide whether content is safe or grant authority. It coordinates agents; it is not an agent reviewer or approval system. |
| Deterministic approval gate | Converts validated reviewer JSON and optional human input into an application-owned approval record. | A schema-valid safety review and `approve` or `reject` when approval is allowed. | `pending`, `approved`, `rejected`, or `blocked`, always with `action_authority="none"`. | Ask a model to interpret malformed output, let a human override a reviewer block, or execute an action. |

### Agent 1: Maintenance Planner

The planner is added to turn raw inputs into a coherent proposal. The assessment package can contain telemetry, work-order facts, retrieved procedures, revision metadata, and constraints. Presenting that package directly to a person forces the person to assemble the argument themselves. The planner performs that synthesis while preserving the distinction between:

- **Facts:** Current operational observations, such as increasing vibration or a visible seal leak.
- **Evidence:** Retrieved procedures or records, including their titles, revisions, and effective dates.
- **Uncertainty:** Missing measurements, absent torque values, or unresolved conflicts.
- **Recommendations:** Planner-facing next steps that remain proposals rather than executed actions.

Its output is intentionally called a **draft**. A fluent recommendation can still contain unsupported claims, follow malicious text retrieved from a document, use a superseded procedure, or imply authority the application does not possess. The planner therefore cannot approve its own work.

### Agent 2: Independent Safety Reviewer

The reviewer is added as a separate agent so its primary objective is critique rather than completion. It receives the planner's draft but follows different instructions: find reasons the draft should be blocked, revised, or escalated. This reduces the risk that the same role which composed a persuasive answer will simply confirm its own assumptions.

The reviewer checks four boundaries:

1. **Evidence support:** Does each consequential claim have supporting evidence and citations?
2. **Evidence quality:** Is the evidence current, sufficient, and free of unresolved revision conflicts?
3. **Operational safety:** Does the recommendation avoid unsafe direction and acknowledge missing information?
4. **Authority:** Does the draft avoid claiming it can control equipment, approve or update work, or reserve inventory?

The decision meanings are deliberately different:

| Decision | Meaning | What happens next |
|---|---|---|
| `approve` | The reviewed recommendation is supported enough to be presented for human approval. | The deterministic gate creates a `pending` record until a person approves or rejects it. |
| `revise` | The draft has a correctable problem, such as an unsupported statement or missing citation. | The deterministic gate returns `blocked`; a person cannot approve it. |
| `escalate` | Available evidence is insufficient or the situation requires expertise outside the workflow. | The deterministic gate returns `blocked` and the case must leave the automated path. |

The reviewer does not make the workflow safe by itself. Its text is still model output, so the application validates the exact JSON contract before using the decision.

### Why These Are Separate Roles

A single prompt could ask one agent to draft and review its own answer, but the two responsibilities would remain entangled. Separate agents provide:

- Instructions optimized for different objectives: synthesis versus challenge.
- An inspectable handoff between the draft and review.
- Independent test cases for planner behavior and reviewer behavior.
- A place to use a different model, policy, or review team later without rewriting the planner.

Separation also has a cost: another model call adds latency, token usage, and another failure mode. Add an agent only when the role has a distinct objective, context, or control boundary. Do not split a workflow into agents merely to make the architecture look more sophisticated.

### Example Handoff

For an assessment package describing rising vibration and a visible seal leak, the handoff should look conceptually like this:

```text
Planner draft:
    Current evidence supports notifying maintenance planning and evaluating a controlled
    shutdown. The exact coupling-bolt torque is unknown and must not be invented.

Reviewer JSON:
    decision = "approve"
    findings = ["Recommendation is supported by the current R3 procedure."]
    blocked_actions = ["No autonomous shutdown or work-order update."]
    requires_human_approval = true

Approval gate:
    status = "pending"
    action_authority = "none"
```

If the planner instead claims it reserved a part, cites only a superseded procedure, or invents the missing torque, the reviewer should return `revise` or `escalate`, and the deterministic gate should return `blocked` regardless of human input.

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

Read the composition from left to right:

1. `participants=[planner, reviewer]` fixes the order. The planner drafts first; the reviewer evaluates second.
2. The orchestrator carries the assessment package and prior messages through the workflow, so the reviewer can compare the draft with its evidence.
3. `output_from=[reviewer]` prevents the unreviewed planner draft from becoming the application result.
4. `.as_agent(...)` packages the composed workflow behind an agent-compatible interface. It does not create a third reasoning role.

After the workflow returns, `parse_safety_review()` validates the reviewer output and `apply_approval_gate()` owns the state transition. Neither responsibility is delegated to a model.

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