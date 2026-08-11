# OPG Microsoft Foundry Workshop

Build an enterprise Work Order Maintenance Assistant progressively through a full day of hands-on labs. The solution begins with a model invocation, then adds structured outputs, maintenance grounding, business tools, multi-agent safety review, tracing, and evaluation.

## Current Lab

### Lab 00: Foundry Foundations and Model Access

Connect to an instructor-provided Microsoft Foundry project using Microsoft Entra ID, invoke an approved model deployment from Python, and compare model behavior in code and the Foundry playground.

Start with [Lab 00](lab-00-foundry-foundations/README.md).

## Repository Status

| Lab | Topic | Status |
|---|---|---|
| 00 | Foundry foundations and model access | Ready |
| 01 | Prompt engineering and structured outputs | Planned |
| 02 | Grounding with Azure AI Search | Planned |
| 03 | Agent tools and work-order workflow | Planned |
| 04 | Multi-agent safety review | Planned |
| 05 | Tracing, evaluation, and promotion | Planned |

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

## Authentication

Labs use `DefaultAzureCredential` and Microsoft Entra ID. Participants authenticate with `az login`; API keys must not be added to `.env`, source files, or lab output.
