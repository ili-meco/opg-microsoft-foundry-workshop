# OPG Microsoft Foundry Workshop

## Customer Agenda

**Format:** Two-day, instructor-led workshop
**Audience:** Developers, architects, technical leads, data and AI practitioners, and use-case owners
**Approach:** Technical presentations, live demonstrations, guided hands-on exercises, and facilitated use-case design

## Workshop Objectives

By the end of the workshop, participants will be able to:

- Explain how Microsoft Foundry supports the agent development lifecycle.
- Build an agent that uses structured outputs and controlled business tools.
- Ground agent responses with Azure AI Search and Foundry IQ.
- Design a multi-agent workflow with explicit human decision boundaries.
- Trace and evaluate agent behavior before promotion.
- Identify and prioritize OPG use cases for further discovery and prototyping.

## Workshop Outcomes

- Working Microsoft Foundry maintenance-assistant reference implementation.
- Reusable patterns for tools, knowledge grounding, multi-agent orchestration, safety, tracing, and evaluation.
- Prioritized OPG use-case shortlist.
- Initial architecture and delivery considerations for selected use cases.
- Agreed actions, owners, and follow-up steps.

> Times are estimates and may be adjusted based on participant questions, environment readiness, and the depth of hands-on discussion.

Memory and fine-tuning are covered as design choices within the enterprise knowledge and retrieval session rather than as standalone sessions. The recovered 45 minutes is used to give participants more time for questions, examples, and discussion in the tools, enterprise knowledge, hosted agents, and governance presentations.

## Day 1: Foundry Foundations, Tools, and Enterprise Knowledge

**Estimated time:** 9:00 AM-4:30 PM, including lunch and breaks

| Time | Session | What participants will learn or do |
|---|---|---|
| 9:00-9:15 | Welcome and workshop orientation | Review the objectives, working approach, maintenance scenario, and expected outcomes. |
| 9:15-9:50 | Agentic AI and Microsoft Foundry foundations | Introduce agents, agentic architecture, Microsoft Foundry, and model-selection considerations. |
| 9:50-10:20 | Hands-on: Foundry foundations and model access | Connect to Foundry, authenticate without API keys, invoke a model, and inspect a baseline response. |
| 10:20-10:35 | Break |  |
| 10:35-11:00 | Foundry Agent Service and Foundry Toolkit | Explore the agent development lifecycle, development tools, project organization, and managed services. |
| 11:00-11:35 | Tools and enterprise connectivity | Review function tools, Toolboxes, MCP, OpenAPI, A2A, governed system integration, and the boundaries between model reasoning and deterministic operations. |
| 11:35-12:50 | Hands-on: Structured outputs and deterministic tools | Validate structured model responses and add controlled, read-only asset and inventory tools. |
| 12:50-1:35 | Lunch |  |
| 1:35-2:30 | Enterprise knowledge and retrieval | Explore grounding and RAG patterns, retrieval strategies, Azure AI Search, Foundry IQ, memory, and when fine-tuning is appropriate. Compare the choices through practical enterprise examples. |
| 2:30-4:00 | Hands-on: Azure AI Search and Foundry IQ grounding | Build a Search index, compare retrieval methods, create a knowledge base, and test grounded answers with citations. |
| 4:00-4:15 | Break |  |
| 4:15-4:30 | Day 1 recap | Review the solution built during Day 1 and prepare for multi-agent development on Day 2. |

## Day 2: Multi-Agent Systems, Governance, and Collaborative Solution Design

**Estimated time:** 9:00 AM-4:30 PM, including lunch and breaks

| Time | Session | What participants will learn or do |
|---|---|---|
| 9:00-9:15 | Day 1 recap and Day 2 objectives | Connect the grounded agent built on Day 1 to multi-agent orchestration and responsible operation. |
| 9:15-9:55 | Hosted agents and Microsoft Agent Framework | Explore managed hosting, the Microsoft Agent Framework development model, and sequential, concurrent, handoff, group-chat, and Magentic patterns. |
| 9:55-10:55 | Hands-on: Multi-agent evidence, planning, and safety review | Build a workflow with an evidence analyst, maintenance planner, and safety reviewer while preserving human decision authority. |
| 10:55-11:10 | Break |  |
| 11:10-11:50 | Governance and responsible agent operations | Cover tracing, monitoring, evaluation, identity, content safety, prompt-injection defenses, guardrails, and accountable human decision boundaries. |
| 11:50-12:40 | Hands-on: Tracing, evaluation, and promotion | Inspect traces, run evaluation scenarios, measure quality and safety, and apply a promotion gate. |
| 12:40-1:25 | Lunch |  |
| 1:25-1:40 | Group challenge briefing | Form teams, assign use cases, introduce the whiteboard template, and explain final presentation expectations. |
| 1:40-2:05 | Step 1: Define the use case | Identify the user, business problem, current workflow, pain points, desired outcome, and measurable value. |
| 2:05-2:35 | Step 2: Break apart the solution | Map data, knowledge sources, business tools, integrations, user interactions, and human decisions. |
| 2:35-2:50 | Break |  |
| 2:50-3:35 | Step 3: Design the target architecture | Select the agent pattern, models, grounding approach, tools, memory, hosting, identity, and integration architecture. |
| 3:35-3:55 | Step 4: Validate the design | Identify risks, guardrails, evaluation criteria, human approval boundaries, assumptions, and prototype scope. |
| 3:55-4:20 | Group presentations | Present each use case, proposed architecture, key decisions, risks, and recommended next steps. |
| 4:20-4:30 | Workshop close | Confirm key takeaways, owners, and follow-up actions. |