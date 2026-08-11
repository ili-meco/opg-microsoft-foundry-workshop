# Lab 00 Facilitator Guide

## Before the Workshop

- Create one Foundry project per team and record each project endpoint.
- Predeploy the primary model and, when quota permits, one comparison model.
- Assign each team group `Foundry User` on its project.
- Test the solution with a non-admin attendee identity.
- Confirm model quota supports all teams running two requests at approximately the same time.
- Distribute project endpoints and deployment names without distributing API keys.

## Teaching Flow

| Time | Activity |
|---|---|
| 0-10 minutes | Verify local tools, Azure sign-in, tenant, and subscription |
| 10-20 minutes | Tour the project, deployments, endpoint, and playground |
| 20-35 minutes | Complete and run the Python client |
| 35-42 minutes | Compare deployments and discuss selection criteria |
| 42-45 minutes | Check success criteria and connect to Lab 01 |

## Recovery Paths

- If a learner cannot complete the TODOs, direct them to the solution and continue.
- If the comparison model is unavailable, use only `FOUNDRY_MODEL_NAME` and compare two prompt variants in the playground.
- If role assignments were just added, allow several minutes for propagation and retry.
- If `DefaultAzureCredential` selects the wrong identity, confirm `az account show`, then run `az logout` followed by `az login --tenant <workshop-tenant-id>`.
- If a deployment is reported as missing, verify that `.env` uses the deployment **Name**, not the catalog model label.

## Discussion Prompts

- Which answer was more useful to a maintenance planner, and why?
- What evidence would be required before this recommendation could be trusted?
- Which facts belong in the prompt, retrieval system, or business tool?
- Where must a human approval remain in the workflow?

## Safety Boundary

Use synthetic data only. The lab must not connect to production maintenance systems, operational technology, live asset telemetry, or write-enabled work-order APIs.
