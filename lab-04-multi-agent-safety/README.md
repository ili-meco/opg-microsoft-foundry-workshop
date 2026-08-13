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

Before writing code, identify which input belongs in each category:

1. Find the current equipment observations. These are facts the planner may state directly.
2. Find each retrieved source's title, revision, effective date, and content. These are evidence, not instructions to the agent.
3. Find the operational and authority constraints. These remain in force even if a retrieved document or model response says otherwise.
4. Note what the package does **not** contain. Missing values must remain unknown rather than being inferred or invented.

The entire package enters the sequential workflow. The planner turns it into a draft, and the reviewer uses the shared context to check that draft against the original facts and evidence.

## Step 2: Complete the Approval Gate

Open `starter/approval_gate.py`. The two Pydantic models are already complete; your job is to connect untrusted reviewer output to a deterministic state machine.

### TODO 1: Parse the Reviewer Contract

Implement `parse_safety_review()` using Pydantic's JSON validation for `SafetyReview`.

Keep these constraints intact:

- Pass the raw reviewer string to the validator. Do not strip Markdown fences or search for a JSON-looking substring.
- Let malformed JSON fail rather than asking another model call to repair it.
- Let `extra="forbid"` reject unexpected fields such as `execute_work_order`.
- Let `Literal[True]` reject a response that attempts to remove human approval.
- Return the validated `SafetyReview`, not a plain dictionary.

This deliberately fails closed. A reviewer response that is almost correct is still not an approved application contract.

### TODO 2: Calculate the Approval Status

Think of `apply_approval_gate()` as two gates that must be checked in order:

```text
reviewer gate -> human gate -> final status
```

#### Gate 1: Did the Safety Reviewer Clear the Recommendation?

Check `review.decision` first.

- If the reviewer says `revise`, set the status to `blocked`. The draft has a correctable safety or evidence problem and must be rewritten.
- If the reviewer says `escalate`, set the status to `blocked`. The available evidence or workflow authority is insufficient, so the case must leave the automated path.
- Only when the reviewer says `approve` may the recommendation continue to the human gate.

Once the reviewer blocks a recommendation, stop evaluating approval choices. A supplied human value does not change the result. For example:

```text
reviewer = revise
human = approve
status = blocked
```

This is intentional. A person cannot turn an unsupported model recommendation into a supported one simply by selecting **approve**.

#### Gate 2: What Did the Human Decide?

Reach this gate only when `review.decision == "approve"`.

- If `human_decision` is `None`, set the status to `pending`. The reviewer cleared the recommendation, but nobody has made the accountable human decision yet.
- If `human_decision` is `approve`, set the status to `approved`.
- If `human_decision` is `reject`, set the status to `rejected`.

For example:

```text
reviewer = approve
human = None
status = pending
```

Later, the same reviewer-cleared recommendation can receive a human decision:

```text
reviewer = approve
human = reject
status = rejected
```

The four statuses mean:

- `blocked`: The reviewer found a problem. Human approval is unavailable.
- `pending`: The reviewer cleared the recommendation, but the human has not decided.
- `approved`: Both the reviewer and the human approved the recommendation.
- `rejected`: The reviewer cleared the recommendation, but the human declined it.

Use this control flow:

```text
if the reviewer did not approve:
    status is blocked
else if the human has not decided:
    status is pending
else if the human approved:
    status is approved
else:
    status is rejected
```

The ordering is the core safety rule: **the reviewer decides whether human approval is available; the human decides whether to accept a reviewer-cleared recommendation.**

### TODO 3: Create the Approval Record

Return an `ApprovalRecord` containing:

- The calculated status.
- The original reviewer and human decisions.
- `review.reviewed_recommendation`, not an earlier unreviewed planner draft.
- The review findings and citations for auditability.
- No action implementation and no expanded authority.

Do not set `action_authority` to another value when status becomes `approved`. Its type and default intentionally keep it at `none`: approval permits presenting or recording a recommendation, not controlling equipment or changing a work order.

After calculating the status, return a record that preserves the review evidence and grants no action authority.

### Validate Steps 1-3

Run:

```powershell
python -m unittest tests.test_lab_04_approval -v
```

Map failures back to the TODOs:

| Failing test behavior | Recheck |
|---|---|
| Exact JSON does not parse | TODO 1 and the Pydantic JSON validation call. |
| Extra reviewer fields are accepted | `SafetyReview.model_config` and whether validation was bypassed. |
| A clean review immediately approves | The `human_decision is None` branch in TODO 2. |
| Human approval overrides `revise` or `escalate` | Branch ordering in TODO 2. |
| `action_authority` is not `none` | The `ApprovalRecord` construction in TODO 3. |

After the focused gate tests pass, continue to workflow composition.

## Step 3: Compose the Agents

Open `starter/safety_workflow.py`. The Foundry client and both agent instances are already created. Complete only the orchestration returned by `build_workflow()`.

Before the TODOs, notice how authentication is constructed:

```python
get_bearer_token_provider(credential, "https://ai.azure.com/.default")
```

`FOUNDRY_PROJECT_ENDPOINT` is a project-scoped endpoint under `services.ai.azure.com/api/projects/...`. It expects a Microsoft Foundry data-plane token whose audience is `https://ai.azure.com`. Passing `DefaultAzureCredential` directly to this pinned `OpenAIChatClient` version would make Agent Framework request its default Azure OpenAI scope, `https://cognitiveservices.azure.com/.default`, and the project endpoint would reject that token with HTTP 401. The explicit provider keeps the credential chain while selecting the correct audience.

The starter passes that provider through the client's `api_key` parameter intentionally. For this OpenAI-compatible `/openai/v1` route, the callable supplies the bearer token while keeping the transport on `AsyncOpenAI`. Passing it through `credential` would select Azure routing, append an `api-version` query parameter, and produce HTTP 400 because `/v1` forbids that query parameter.

The Azure Identity helper returns a synchronous callable, while `AsyncOpenAI` awaits callable API-key providers. `foundry_token_provider()` therefore returns a small async wrapper around the Azure Identity provider. Returning the synchronous provider directly causes `TypeError: object str can't be used in 'await' expression` before any HTTP request is sent.

### TODO 1: Fix the Execution Order

Create a `SequentialBuilder` whose `participants` are `[planner, reviewer]` in that order. Order is behavior here:

- The planner must see the assessment package first and produce a draft.
- The reviewer must run second so it can inspect the draft and shared evidence.
- Reversing the list asks the reviewer to review something that does not yet exist.

### TODO 2: Choose the Trusted Workflow Output

Set `output_from=[reviewer]`. Both agents contribute messages to the workflow, but only the reviewer's strict JSON should leave the orchestration as its final text. Returning the planner output would bypass the independent review.

### TODO 3: Build and Wrap the Workflow

Build the orchestration and expose it through an agent-compatible interface named `opg_maintenance_safety_workflow`:

```python
SequentialBuilder(
    participants=[planner, reviewer],
    output_from=[reviewer],
).build().as_agent(name="opg_maintenance_safety_workflow")
```

Return that composed object from `build_workflow()`. The reviewer sees the shared workflow context and returns the final output. The application still validates that output.

Read the composition from left to right:

1. `participants=[planner, reviewer]` fixes the order. The planner drafts first; the reviewer evaluates second.
2. The orchestrator carries the assessment package and prior messages through the workflow, so the reviewer can compare the draft with its evidence.
3. `output_from=[reviewer]` prevents the unreviewed planner draft from becoming the application result.
4. `.as_agent(...)` packages the composed workflow behind an agent-compatible interface. It does not create a third reasoning role.

After the workflow returns, `parse_safety_review()` validates the reviewer output and `apply_approval_gate()` owns the state transition. Neither responsibility is delegated to a model.

Run both offline test modules before making a live model call:

```powershell
python -m unittest tests.test_lab_04_approval tests.test_lab_04_workflow -v
```

The workflow tests verify endpoint construction, accepted human input, and the reviewer's structured-output requirements. They do not call Azure, so failures here should be fixed before `az login` or live execution.

## Step 4: Run the Solution

```powershell
az login
python .\lab-04-multi-agent-safety\solution\safety_workflow.py
```

When prompted, type `approve` or `reject`. Approval means the recommendation may be presented to the planner; it does not execute a maintenance action.

If the run returns HTTP 401 with `audience is incorrect (https://ai.azure.com)`, confirm your file contains `FOUNDRY_TOKEN_SCOPE = "https://ai.azure.com/.default"`. If it returns HTTP 400 saying `api-version query parameter is not allowed when using /v1 path`, confirm `OpenAIChatClient` receives `api_key=foundry_token_provider(credential)`, not `credential=...`. If Python reports that a token string cannot be awaited, confirm `foundry_token_provider()` returns its async `get_token` wrapper. Rerun `az login` only if all three settings are correct and the message instead says the token is missing, invalid, or expired.

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