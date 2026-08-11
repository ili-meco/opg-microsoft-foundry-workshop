# Lab 00: Foundry Foundations and Model Access

**Duration:** 45 minutes | **Skill level:** Beginner

## What You Will Build

A small Python client that authenticates with Microsoft Entra ID, connects to your team project, invokes an approved model deployment through the Foundry project endpoint, and optionally compares a second deployment.

```text
Technician request
       |
       v
Python workshop client -- Entra ID --> Microsoft Foundry project
                                             |
                                             v
                                  Approved model deployment
                                             |
                                             v
                                  Maintenance assessment
```

This is a connectivity and model-behavior exercise. Retrieval, tools, and agents are introduced in later labs.

## Learning Objectives

By the end of this lab, you can:

- Locate a Foundry project, its project endpoint, and deployed models.
- Explain the difference between a model name and a deployment name.
- Authenticate from Python without API keys.
- Invoke a deployed model with the Responses API.
- Compare two models using task fit, instruction following, latency, and response quality.

## Prerequisites

- Python 3.11 or newer, Git, VS Code, and Azure CLI.
- Access to the instructor-provided OPG workshop project.
- `Foundry User` on your assigned project.
- At least one model deployment created by the workshop administrator.
- The root setup script completed successfully.

## Step 1: Verify Local Setup

From the repository root, activate the environment and run the local checks:

```powershell
.\.venv\Scripts\Activate.ps1
python .\scripts\verify_setup.py
```

Resolve every `FAIL` before continuing. Endpoint warnings are expected until `.env` is configured.

## Step 2: Sign In and Confirm the Subscription

```powershell
az login
az account show --output table
python .\scripts\verify_setup.py --azure
```

Confirm that the tenant and subscription are the workshop values supplied by the instructor.

## Step 3: Explore the Foundry Project

In the Microsoft Foundry portal:

1. Open your assigned team project.
2. Locate the project endpoint. It has the form `https://<account>.services.ai.azure.com/api/projects/<project>`.
3. Open the deployed-model list and record the deployment name in the **Name** column.
4. Open the model playground and run the maintenance request below.
5. Record the response quality and approximate latency.

Use this synthetic request throughout the lab:

> Pump P-104 has increasing vibration and a small seal leak. The last inspection was 30 days ago. Recommend the immediate next action and identify any assumptions.

Do not enter real asset identifiers, operational details, or sensitive work-order data.

## Step 4: Configure the Lab

Copy `.env.example` to `.env` if the setup script did not already do so, then set:

```dotenv
FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
FOUNDRY_MODEL_NAME=<deployment-name-from-the-name-column>
FOUNDRY_COMPARISON_MODEL_NAME=<optional-second-deployment>
```

Use deployment names, not model catalog labels. Do not add API keys.

## Step 5: Complete the Python Client

Open `starter/foundry_model_check.py` and implement `request_model_response()` by following its TODOs:

1. Call `client.responses.create()`.
2. Pass the deployment name as `model`.
3. Pass `SYSTEM_INSTRUCTIONS` as `instructions`.
4. Pass the maintenance request as `input`.
5. Return `response.output_text`.

Run the client from the repository root:

```powershell
python .\lab-00-foundry-foundations\starter\foundry_model_check.py
```

If you are blocked, compare your implementation with `solution/foundry_model_check.py` and continue.

## Step 6: Compare Models

When `FOUNDRY_COMPARISON_MODEL_NAME` is configured, the script invokes both deployments. Compare them using this scorecard:

| Criterion | Primary | Comparison |
|---|---:|---:|
| Followed the requested format |  |  |
| Clearly labeled assumptions |  |  |
| Avoided inventing maintenance history |  |  |
| Proposed a cautious immediate action |  |  |
| Observed latency |  |  |

The fastest or largest model is not automatically the best choice. Select the least costly approved model that reliably meets the task and quality requirements.

## Success Criteria

- [ ] `python scripts/verify_setup.py --azure` has no failures.
- [ ] The project endpoint and deployment name are configured in `.env`.
- [ ] The starter script authenticates without an API key.
- [ ] At least one model returns a maintenance assessment.
- [ ] The response identifies assumptions instead of presenting unsupported facts.
- [ ] You can explain one quality, latency, or cost tradeoff in model selection.

## Bonus Challenge

Change the maintenance request so critical evidence is missing. Improve `SYSTEM_INSTRUCTIONS` so the model explicitly escalates uncertainty instead of inventing an answer. Lab 01 will turn that behavior into a validated structured-output contract.

## Key Concepts

| Concept | Meaning |
|---|---|
| Foundry account | Administrative, security, model, and monitoring boundary |
| Foundry project | Team workspace and data-plane development boundary |
| Deployment name | Identifier sent in the `model` field at runtime |
| Project endpoint | Project-scoped API endpoint used by `AIProjectClient` |
| `DefaultAzureCredential` | Credential chain that can use the attendee's Azure CLI sign-in |
| Responses API | Model inference API used for the workshop baseline |
