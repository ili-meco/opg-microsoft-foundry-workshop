# OPG Microsoft Foundry Workshop

Build an enterprise Work Order Maintenance Assistant progressively through a full day of hands-on labs. The solution begins with a model invocation, then adds structured outputs, deterministic business tools, Azure AI Search and Foundry IQ grounding, multi-agent safety review, tracing, and evaluation.

See the [complete workshop outcome architecture](ARCHITECTURE.md) for the end-state component map, runtime flow, trust boundaries, and lab-by-lab build sequence.

## Ready Labs

Complete the labs in order. Each stage adds one explicit capability and control boundary to the same maintenance-assistant scenario.

- [Lab 00: Foundry Foundations and Model Access](lab-00-foundry-foundations/README.md)
- [Lab 01: Prompting and Structured Outputs](lab-01-prompting-structured-output/README.md)
- [Lab 02: Deterministic Agent Tools](lab-02-agent-tools/README.md)
- [Lab 03: Azure AI Search and Foundry IQ Grounding](lab-03-search-grounding/README.md)
- [Lab 04: Multi-Agent Safety Review and Human Approval](lab-04-multi-agent-safety/README.md)
- [Lab 05: Tracing, Evaluation, and Promotion](lab-05-observability-evaluation/README.md)

## Repository Status

| Lab | Topic | Status |
|---|---|---|
| 00 | Foundry foundations and model access | Ready |
| 01 | Prompt engineering and structured outputs | Ready |
| 02 | Deterministic agent tools and work-order lookups | Ready |
| 03 | Azure AI Search and Foundry IQ grounding | Ready |
| 04 | Multi-agent safety review and human approval | Ready |
| 05 | Tracing, evaluation, and promotion | Ready |

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
