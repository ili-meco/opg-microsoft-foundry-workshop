# Lab 04: Multi-Agent Evidence, Planning, and Safety Review

**Duration:** Part A: 60 minutes; optional Part B: 25 minutes | **Skill level:** Intermediate

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
- Optionally package and deploy the workflow with a Foundry Toolkit hosted-agent template.

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

## Part B: Deploy the Workflow as a Hosted Agent

Part B uses the Foundry Toolkit's official workflow template to create the hosting project. Do not build or copy `azure.yaml`, `.foundry`, `.vscode`, or the hosting dependencies by hand; the template owns those files.

The deployment boundary is:

```text
caller -> hosted analyst -> planner -> safety reviewer -> HumanReviewPacket candidate
                                                        |
                                              caller validates JSON
                                                        |
                                         authorized human approve/reject
```

The hosted agent prepares the review packet. It does not prompt for, store, or execute the human decision.

**Instructor preflight:** Before offering Part B, deploy and smoke-test the model used by the generated workflow template, confirm hosted-agent quota, and confirm participants can deploy to the shared project. Participants should reuse that deployment rather than create models during the lab.

### Step B1: Create the Hosted-Agent Project

Create the agent in a new empty sibling folder named with `HOSTED_AGENT_NAME` from your generated `.env`, such as `opg26a-mt-maintenance-agent`. Keeping the hosted project outside this workshop workspace prevents its generated files from colliding with the lab files.

1. Open the Foundry Toolkit view in VS Code.
2. Select **Create New Hosted Agent**.
3. Select the existing workshop Foundry project when prompted.
4. Choose **Workflow agent (Responses, Agent Framework, Python)**.
5. Keep **Code** deployment and the generated Python 3.13 runtime.
6. Use `HOSTED_AGENT_NAME` for the hosted-agent name and `AZURE_ENV_NAME` for the `azd` environment whenever the Toolkit prompts for them.

The template creates the structure shown by the Toolkit, including:

```text
.foundry/
.vscode/
src/<generated-agent-folder>/
       main.py
       requirements.txt
azure.yaml
```

The picker uses the same curated catalog as `azd ai agent sample list`. The template manifest is `samples/python/hosted-agents/agent-framework/responses/05-workflows/azure.yaml` in the official `microsoft-foundry/foundry-samples` repository.

### Step B2: Replace Only the Sample Workflow

Replace the generated `src/<generated-agent-folder>/main.py` with [part-b-hosted-agent/main.py](part-b-hosted-agent/main.py). Keep the generated `requirements.txt`, `azure.yaml`, `.foundry`, and `.vscode` files.

The generated host uses `AZURE_AI_MODEL_DEPLOYMENT_NAME`; Part A uses `FOUNDRY_MODEL_NAME`. Keep the generated variable because the Toolkit injects it for local runs and deployments.

Compare the replacement with Part A:

- `FoundryChatClient` still connects MAF to the Foundry project.
- `WorkflowBuilder` and `AgentExecutor` use the hosting template's workflow pattern.
- `context_mode="full"` lets the reviewer inspect the original input, EvidencePacket, and planner draft. The template's slogan example uses `last_agent`, which is too narrow for this safety review.
- `output_executors=[reviewer_executor]` prevents intermediate drafts from becoming the hosted response.
- `ResponsesHostServer` exposes the workflow through the Foundry Responses protocol.
- No `input()` or approval function runs inside the hosted agent.

### Step B3: Run in Agent Inspector

1. Create or select the Python virtual environment when prompted.
2. Install the generated `requirements.txt` if the template has not already done so.
3. Press `F5`. The generated debug configuration starts the host and opens Agent Inspector.
4. Paste the contents of `data/assessment_package.json` into the Inspector.
5. Confirm that the final response is one JSON object with `requires_human_decision=true` and `action_authority="none"`.

The official workflow template currently recommends a stronger model for continuing a workflow from prior assistant messages and is tested with the model declared by its generated manifest. Use the template-selected or instructor-validated deployment; do not silently replace it with another model without repeating the local smoke test.

### Step B4: Deploy with Foundry Toolkit

1. Open the Command Palette with `Ctrl+Shift+P`.
2. Run **Foundry Toolkit: Deploy Hosted Agent**.
3. Select **Code**, confirm the generated agent name and runtime, then choose **Review + Deploy**.
4. After deployment, invoke the agent in the Agent Playground and inspect its logs.
5. Submit the same assessment package and compare the remote response with the local result.

Deployment is complete when the remote endpoint returns the reviewer packet and still exposes no approval or action capability. A production caller must validate the response with the strict `HumanReviewPacket` contract from `solution/approval_gate.py` before offering an authorized person the separate approve/reject action.

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
- [ ] In Part B, the Toolkit-generated host returns only the reviewer packet.
- [ ] Human approval remains outside the hosted agent.