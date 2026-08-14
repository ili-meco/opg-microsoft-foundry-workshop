# Workshop User Story: Work-Management Assistant

## Scenario Boundary

This is a fictional workshop scenario grounded in terminology from OPG discussions. The asset, condition, people, records, and supporting data are synthetic. The workshop does not connect to production work-management or operational systems.

## Full User Story

> As an OPG employee reviewing an equipment issue, I want an AI assistant to gather the relevant equipment details, parts availability, maintenance procedures, and work-order history so that I can prepare an evidence-based recommendation for an authorized person to review.

### What This Assistant Is For

This is a **work-planning and review assistant**. It:

- Reviews a reported equipment issue.
- Collects equipment, inventory, and procedural evidence.
- Identifies missing or conflicting information.
- Proposes next steps.
- Prepares a package for an authorized human reviewer.

Lab 03 retrieves procedures, but it uses them as evidence supporting a recommendation. It does not tell a field worker how to perform maintenance.

A field-worker assistant would be a different use case:

> As an OPG field worker, I want to find the current approved procedure for my assigned task so that I can review the correct instructions and safety requirements before starting work.

That use case would require controls for worker authorization, assigned work orders, current procedure revisions, prerequisites, hold points, and acknowledgements. Those controls are outside this workshop scenario.

In the fictional scenario, an adverse condition has been recorded for pump `ASSET-104`. The record notes increasing vibration and a small seal leak. Before deciding what should happen next, the work-management user needs to understand:

- The asset's identity, location, operating status, and installed parts.
- Whether required parts are available.
- Which approved maintenance procedures and revisions apply.
- Whether available evidence conflicts or important information is missing.
- Whether a proposed next step is sufficiently grounded and safe to present for a human decision.

The assistant gathers information only from the workshop's controlled, read-only sources. It distinguishes verified facts from assumptions, cites procedural evidence, preserves uncertainty, and prepares a recommendation. It cannot approve work, modify a work order, reserve inventory, return equipment to service, or control equipment.

## Human Review And Authority

The human reviewer is an **authorized OPG work-management or maintenance decision-maker**. This generic workshop role should be mapped to OPG's actual accountable job title and process before any production implementation.

The human reviewer:

- Confirms that the correct asset and condition were identified.
- Reviews the supporting asset, inventory, procedure, and work-order evidence.
- Resolves missing or conflicting information through the established process.
- Considers operational and safety implications.
- Approves or rejects the recommendation presented by the workshop application.
- Uses OPG's established systems and procedures for any action outside the AI workflow.

An approval in the workshop records a decision about the recommendation only. It does not authorize or execute maintenance work.

## Story By Lab

Each lab adds one capability and one control boundary to the same scenario.

### Lab 00: Establish The Model Baseline

**Participant story**

> As an OPG employee, I want an AI model to review an equipment issue so that I can see what it can determine before it is given maintenance records, operating procedures, or access to other systems.

**What participants build:** A small Python application that signs in securely, connects to Microsoft Foundry, and asks an AI model to review the fictional `ASSET-104` equipment issue.

**Why it matters:** This first response is the baseline for the workshop. It shows what the model can produce without current equipment data, maintenance history, or procedures, and why a plausible answer is not yet a trustworthy recommendation.

### Lab 01A: Make The Assessment Predictable

**Participant story**

> As a developer building the assistant, I want every assessment to use the same clearly defined fields so that the application can reliably display, check, and test the result.

**What participants build:** A Pydantic model that requires the AI response to separate known facts, assumptions, risks, missing information, and recommended next steps.

**Why it matters:** A predictable structure lets the application validate and use the answer safely. It also makes errors easier to spot, although a correctly formatted answer can still contain unsupported claims.

### Lab 01B: Add Controlled Operational Facts

**Participant story**

> As an OPG employee, I want the assistant to look up the equipment record and parts availability so that its assessment is based on current information rather than assumptions.

**What participants build:** Two controlled, read-only tools that let the assistant retrieve the fictional equipment record and check whether installed parts are in stock.

**Why it matters:** The model no longer has to guess these facts. The application still decides which lookups are allowed, validates every request, and prevents the assistant from changing inventory or work orders.

### Lab 03: Ground The Recommendation In Procedures

**Participant story**

> As an OPG employee, I want the assistant to find the relevant maintenance procedures and show where each piece of information came from so that I can verify the evidence behind its recommendation.

**What participants build:** A searchable collection of fictional maintenance documents and a Foundry IQ connection that lets the assistant retrieve relevant passages and cite their sources.

**Why it matters:** A recommendation should be traceable to the procedures and records that support it. Participants also learn that a retrieved document can be outdated, conflicting, incomplete, or untrusted, so a citation must still be reviewed.

### Lab 04: Prepare A Safe Human Decision Package

**Participant story**

> As the authorized OPG reviewer, I want to see the evidence, proposed next steps, missing information, and safety concerns in one clear package so that I can make an informed decision about the recommendation.

**What participants build:** A three-step workflow in which the evidence analyst organizes what is known and missing, the maintenance planner uses that evidence to propose next steps, and the safety reviewer checks whether the package is complete and safe enough to show to a person.

**Why it matters:** The AI agents prepare and check the recommendation, but they cannot approve it. Only an authorized person can approve or reject a complete package, and that decision does not itself start or authorize maintenance work.

### Lab 05: Measure Readiness Before Promotion

**Participant story**

> As a member of the team responsible for the assistant, I want to test how it behaves in both normal and unsafe situations so that we can find failures before deciding whether it is ready for wider use.

**What participants build:** Traces that show what happened during each run, repeatable tests for six normal and unsafe situations, and a report that shows whether the assistant passed the required checks.

**Why it matters:** One successful demonstration does not prove that the assistant is dependable. The team needs repeatable evidence that it handles missing information, conflicting procedures, malicious instructions, unauthorized requests, and tool failures correctly.

## End-To-End Acceptance Criteria

- Model output used by the application is schema-valid.
- Asset and inventory claims come only from approved read-only tools.
- Procedural claims include retrievable source evidence and citations.
- Facts, assumptions, conflicts, and missing evidence remain distinguishable.
- The recommendation does not claim authority to approve or execute work.
- The safety reviewer blocks incomplete, unsupported, or unsafe packages from human decision.
- Only an authorized human can approve or reject a ready recommendation.
- Human approval does not update work orders, reserve parts, or control equipment.
- Traces and evaluation results make the workflow's behavior reviewable before promotion.