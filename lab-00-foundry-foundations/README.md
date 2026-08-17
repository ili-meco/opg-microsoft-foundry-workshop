# Lab 00: Foundry Foundations and Model Access

**Duration:** 45 minutes | **Skill level:** Beginner

## Your Part In The User Story

> As an OPG employee, I want an AI model to review an equipment issue so that I can see what it can determine before it is given maintenance records, operating procedures, or access to other systems.

**You build:** A small Python application that signs in securely, connects to Microsoft Foundry, and asks an AI model to review the fictional `ASSET-104` equipment issue.

**Why it matters:** This first response is the baseline for the workshop. It shows what the model can produce without current equipment data, maintenance history, or procedures, and why a plausible answer is not yet a trustworthy recommendation.

This lab is the first increment of the [complete workshop user story](../docs/WORKSHOP-USER-STORY.md).

## What You Will Build

A small Python client that authenticates with Microsoft Entra ID, connects to your team project, invokes an approved model deployment through the Foundry project endpoint, and optionally compares a second deployment.

```text
Recorded condition
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
- Access to your own Azure subscription and Microsoft Foundry project.
- `Foundry User` or equivalent model-inference access on your project.
- At least one model deployment in that project.
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

Confirm that Azure CLI is using the tenant and subscription that contain your Foundry project. If you have access to multiple subscriptions, select the correct one before continuing:

```powershell
az account list --output table
az account set --subscription "<your-subscription-name-or-id>"
az account show --output table
```

## Step 3: Explore the Foundry Project

In the Microsoft Foundry portal, open the project in your Azure subscription:

1. Open your Foundry project.
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

### Keep Workshop Model Costs Low

Use a small, low-cost model deployment that supports the Responses API and is available in your region. For example, choose a `mini` or `nano` model such as GPT-4.1-mini or GPT-4.1-nano when it meets the exercise requirements. Model availability and pricing vary by subscription and region, so confirm the current price before deployment.

Configure only `FOUNDRY_MODEL_NAME` for the first run. Leave `FOUNDRY_COMPARISON_MODEL_NAME` empty unless you specifically want to compare two deployments; setting it causes every execution to make a second billable model call. Use the short synthetic request provided by the lab, avoid repeatedly rerunning unchanged prompts, and delete deployments you no longer need after the workshop.

## Step 5: Complete the Python Client

In VS Code, open `lab-00-foundry-foundations/starter/foundry_model_check.py` and implement `request_model_response()` by following its TODOs:

1. **Call `client.responses.create()`.** This sends an inference request through the project-scoped OpenAI client. The client already carries the Foundry endpoint and Microsoft Entra authentication configured in `main()`.
2. **Pass `model_name` as `model`.** Foundry routes the request to this deployment. The value must be the deployment name from your project, not merely the model-family name shown in the catalog.
3. **Pass `SYSTEM_INSTRUCTIONS` as `instructions`.** These instructions define the assistant's role, expected answer organization, uncertainty behavior, and safety boundary independently from the user's request.
4. **Pass `request` as `input`.** This is the task-specific maintenance observation the model must assess. Keeping it separate from the system instructions makes the control boundary visible.
5. **Return `response.output_text`.** The Responses API can return several structured output items; `output_text` is the SDK convenience property that combines the generated text into the string this command prints.

### Run Your Starter

Open a VS Code terminal with the repository root as its current directory. The prompt should end with `OPG>`. Activate the virtual environment, then run your completed starter file:

```powershell
cd "C:\path\to\OPG"
.\.venv\Scripts\Activate.ps1
python .\lab-00-foundry-foundations\starter\foundry_model_check.py
```

Replace `C:\path\to\OPG` with the folder where you cloned the repository. If your terminal is already at the repository root and the virtual environment is active, run only the final `python` command.

### Run the Completed Solution

If you are blocked, compare your implementation with `lab-00-foundry-foundations/solution/foundry_model_check.py`. You can also run the completed reference implementation from the same repository-root terminal:

```powershell
python .\lab-00-foundry-foundations\solution\foundry_model_check.py
```

The starter command runs the file you edit. The solution command runs the completed reference version. Both read the same root `.env` file and call the configured Foundry deployment.

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
- [ ] You can explain the observed latency difference between the model deployments.

## Bonus Challenge

Change the maintenance request so critical evidence is missing. Improve `SYSTEM_INSTRUCTIONS` so the model explicitly escalates uncertainty instead of inventing an answer. Lab 01 will turn that behavior into a validated response contract, then add controlled access to current asset and inventory facts.

## Key Concepts

| Concept | Meaning |
|---|---|
| Foundry account | Administrative, security, model, and monitoring boundary |
| Foundry project | Team workspace and data-plane development boundary |
| Deployment name | Identifier sent in the `model` field at runtime |
| Project endpoint | Project-scoped API endpoint used by `AIProjectClient` |
| `DefaultAzureCredential` | Credential chain that can use the attendee's Azure CLI sign-in |
| Responses API | Model inference API used for the workshop baseline |
