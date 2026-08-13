# Lab 00 Facilitator Guide

## Before the Workshop

- Ask attendees to confirm access to their own Azure subscription and Foundry project.
- Ask attendees to deploy one low-cost model that supports the Responses API in their region.
- Ask attendees to confirm `Foundry User` or equivalent model-inference access on their project.
- Test the solution with a non-admin attendee identity.
- Recommend a small `mini` or `nano` deployment and leave the comparison model unset by default.
- Remind attendees that model availability, quota, and charges belong to their Azure subscription.

## Teaching Flow

| Time | Activity |
|---|---|
| 0-10 minutes | Verify local tools and select the attendee's project subscription |
| 10-20 minutes | Tour the project, deployments, endpoint, and playground |
| 20-35 minutes | Complete and run the Python client |
| 35-42 minutes | Compare deployments and discuss selection criteria |
| 42-45 minutes | Check success criteria and introduce Lab 01's output-to-tools progression |

## Recovery Paths

- If a learner cannot complete the TODOs, direct them to the solution and continue.
- If the comparison model is unavailable, use only `FOUNDRY_MODEL_NAME` and compare two prompt variants in the playground.
- If role assignments were just added, allow several minutes for propagation and retry.
- If `DefaultAzureCredential` selects the wrong identity, confirm `az account show`, then sign in to the tenant that contains the attendee's Foundry project.
- If a deployment is reported as missing, verify that `.env` uses the deployment **Name**, not the catalog model label.

## Discussion Prompts

- Which answer was more useful to a maintenance planner, and why?
- What evidence would be required before this recommendation could be trusted?
- Which facts belong in the prompt, retrieval system, or business tool?
- Where must a human approval remain in the workflow?

## Safety Boundary

Use synthetic data only. The lab must not connect to production maintenance systems, operational technology, live asset telemetry, or write-enabled work-order APIs.
