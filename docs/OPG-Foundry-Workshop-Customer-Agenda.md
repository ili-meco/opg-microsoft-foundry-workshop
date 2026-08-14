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

## Day 1: Build with Microsoft Foundry

**Estimated time:** 9:00 AM-5:30 PM, including lunch and breaks

| Time | Session | What participants will learn or do |
|---|---|---|
| 9:00-9:15 | Welcome and workshop orientation | Review objectives, working agreements, the maintenance scenario, and the two-day journey. |
| 9:15-9:50 | Agentic AI and Microsoft Foundry foundations | Understand agents, agentic architecture patterns, Microsoft Foundry capabilities, and model-selection considerations. Includes a short model benchmarking demonstration. |
| 9:50-10:20 | Hands-on: Foundry foundations and model access | Connect to the Foundry project, authenticate without API keys, invoke a deployed model, and inspect a baseline response. |
| 10:20-10:35 | Break |  |
| 10:35-11:05 | Building agents with Foundry Agent Service, Foundry Toolkit, and Microsoft Agent Framework | Explore the development experience, framework choices, agent lifecycle, and the relationship between local development and managed hosting. |
| 11:05-11:30 | Tools and enterprise connectivity | Review function tools, Toolboxes, MCP, OpenAPI, A2A, and governed connectivity patterns. Includes a short tools demonstration. |
| 11:30-12:30 | Hands-on: Structured outputs and deterministic tools | Make model responses consistent and checkable, validate structured output, add read-only asset and inventory tools, and enforce an application-controlled tool boundary. |
| 12:30-1:15 | Lunch |  |
| 1:15-1:50 | Enterprise knowledge, RAG, Azure AI Search, and Foundry IQ | Compare grounding approaches, retrieval strategies, hybrid search, Foundry IQ knowledge bases, source permissions, and memory concepts. Includes a retrieval demonstration. |
| 1:50-3:00 | Hands-on: Azure AI Search and Foundry IQ grounding | Create a Search index, compare keyword, vector, and hybrid retrieval, build a Foundry IQ knowledge path, and test a grounded agent with citations. |
| 3:00-3:15 | Break |  |
| 3:15-3:40 | Hosted agents, multi-agent patterns, and model customization | Review hosted-agent capabilities, common orchestration patterns, when multi-agent design is appropriate, and when to consider RAG versus fine-tuning. |
| 3:40-4:25 | Hands-on: Multi-agent evidence, planning, and safety review | Build a sequential workflow with an evidence analyst, maintenance planner, and safety reviewer while keeping approval and action authority with a person. |
| 4:25-4:45 | Operating agents responsibly | Introduce tracing, evaluation, monitoring, optimization, content safety, prompt-injection defenses, and guardrails. Includes an operations demonstration. |
| 4:45-5:20 | Hands-on: Tracing, evaluation, and promotion | Inspect workflow traces, run evaluation cases, measure safety and quality, and apply a repeatable promotion gate. |
| 5:20-5:30 | Day 1 recap and Day 2 preparation | Summarize the reference architecture, capture questions, and introduce the use-case design goals for Day 2. |

## Day 2: Envision and Prioritize OPG Use Cases

**Estimated time:** 9:00 AM-4:15 PM, including lunch and breaks

| Time | Session | What participants will learn or do |
|---|---|---|
| 9:00-9:15 | Day 1 recap and Day 2 goals | Connect the technical patterns from Day 1 to OPG opportunities and confirm the desired outcomes for the day. |
| 9:15-9:45 | Opportunity framing | Identify target users, business problems, current pain points, and decisions or tasks that could benefit from an AI assistant. |
| 9:45-10:30 | Use-case discovery | Develop candidate use cases from participant ideas or the provided starter scenarios, including maintenance recommendations, incident triage, shift handover, policy navigation, spare-parts planning, and change readiness. |
| 10:30-10:45 | Break |  |
| 10:45-11:30 | Data, knowledge, tools, and integration readiness | Map the required data and systems, including work orders, operational records, procedures, SharePoint, Azure Blob Storage, APIs, and human workflows. Identify access, quality, and ownership gaps. |
| 11:30-12:15 | Prioritization | Compare candidates by business value, feasibility, data readiness, risk, measurable outcomes, and suitability for an initial prototype. Select the strongest opportunities. |
| 12:15-1:00 | Lunch |  |
| 1:00-1:45 | Target solution and responsible AI boundaries | Define the proposed agent experience, grounding approach, tools, orchestration pattern, evaluation needs, and decisions that must remain under human control. |
| 1:45-2:45 | Team design session | Create a concise concept for each selected use case, including the user journey, required data, agent responsibilities, success measures, risks, and prototype scope. |
| 2:45-3:00 | Break |  |
| 3:00-3:45 | Team share-outs and feedback | Present each concept, challenge assumptions, identify common platform capabilities, and refine the recommendations. |
| 3:45-4:15 | Roadmap and next steps | Agree on priority use cases, owners, discovery actions, technical spikes, data preparation, governance needs, and the path to a proof of concept. |