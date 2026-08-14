# OPG Microsoft Foundry Workshop

Build an enterprise Work Order Maintenance Assistant progressively through a full day of hands-on labs. The solution begins with a model invocation, then adds structured outputs, deterministic business tools, Azure AI Search and Foundry IQ grounding, multi-agent evidence analysis and safety review, tracing, and evaluation.

See the [complete workshop outcome architecture](ARCHITECTURE.md) for the end-state component map, runtime flow, trust boundaries, and lab-by-lab build sequence.

Read the [complete workshop user story](docs/WORKSHOP-USER-STORY.md) for the synthetic scenario, the authorized human review role, and the capability participants add in each lab.

## The Story You Will Build

> As an OPG employee reviewing an equipment issue, I want an AI assistant to gather the relevant equipment details, parts availability, maintenance procedures, and work-order history so that I can prepare an evidence-based recommendation for an authorized person to review.

This is a **work-planning and review assistant**. It:

- Reviews a reported equipment issue.
- Collects equipment, inventory, and procedural evidence.
- Identifies missing or conflicting information.
- Proposes next steps.
- Prepares a package for an authorized human reviewer.

It is not a field-worker assistant that provides instructions for performing maintenance. Lab 03 retrieves procedures as evidence supporting a recommendation; it does not tell a worker how to complete a maintenance task.

The assistant develops one capability at a time. It never approves or executes maintenance work. In Lab 04, an authorized OPG work-management or maintenance decision-maker may approve or reject a ready recommendation; that recorded decision still grants no authority to update work orders, reserve inventory, return equipment to service, or control equipment.

## Ready Labs

Complete the labs in order. Each stage adds one explicit capability and control boundary to the same maintenance-assistant scenario.

- [Lab 00: Foundry Foundations and Model Access](lab-00-foundry-foundations/README.md)
- [Lab 01: Structured Outputs and Deterministic Tools](lab-01-prompting-structured-output/README.md)
- [Lab 03: Azure AI Search and Foundry IQ Grounding](lab-03-search-grounding/README.md)
- [Lab 04: Multi-Agent Evidence, Planning, and Safety Review](lab-04-multi-agent-safety/README.md)
- [Lab 05: Tracing, Evaluation, and Promotion](lab-05-observability-evaluation/README.md)

## Repository Status

| Lab | Topic | Status |
|---|---|---|
| 00 | Foundry foundations and model access | Ready |
| 01 | Structured outputs, deterministic tools, and work-order lookups | Ready |
| 03 | Azure AI Search and Foundry IQ grounding | Ready |
| 04 | Multi-agent evidence, planning, safety review, and optional hosted deployment | Ready |
| 05 | Tracing, evaluation, and promotion | Ready |

## Participant Workspaces

Workshop resources use a cohort and participant prefix to avoid collisions in the shared Foundry project and Azure AI Search service. The current roster uses `opg26a-<initials>`, such as `opg26a-mt`.

Prepared copies for all 15 participants are committed under `participant-workspaces/`. After cloning the repository, each participant opens only their assigned `opg26a-<initials>` folder and runs its setup script.

Maintainers can generate a fresh set in an empty output folder:

```powershell
python .\scripts\create_participant_workspaces.py --output-root .\dist\opg26a
```

To also populate each generated local `.env` with allowlisted non-secret shared values from the instructor's `.env`, run:

```powershell
python .\scripts\create_participant_workspaces.py --output-root .\dist\opg26a --shared-environment .env
```

Each copy contains the same runnable labs and tests, a personalized `.env.example`, a local ignored `.env`, and `PARTICIPANT.md` with its assigned Search, Foundry IQ, hosted-agent, `azd`, and evaluation names. It excludes Git metadata, `AGENTS.md`, and facilitator guides, keeps environment-specific shared settings out of `.env.example`, and refuses to overwrite an existing participant folder.

Use `--participant mt` to generate one participant while testing the preparation process. Always use an empty output folder; the generator will not overwrite a prepared workspace.

## Quick Setup

Complete setup before the workshop:

```powershell
# Windows PowerShell
.\scripts\setup.ps1
```

```bash
# macOS or Linux
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The scripts create `.venv`, install the pinned dependencies, create `.env` from `.env.example` when needed, and run the local prerequisite checks.

Run the complete offline regression suite at any time:

```powershell
python -m unittest discover -s tests -v
```

Azure-backed scripts require the values documented in `.env.example`. Lab 05's deterministic promotion gate runs offline; its traced workflow requires Foundry Toolkit's trace receiver when you want to visualize spans.

## Authentication

Labs use `DefaultAzureCredential` and Microsoft Entra ID. Participants authenticate with `az login`; API keys must not be added to `.env`, source files, or lab output.
