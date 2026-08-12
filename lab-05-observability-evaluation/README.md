# Lab 05: Tracing, Evaluation, and Promotion

**Duration:** 60 minutes | **Skill level:** Intermediate

## What You Will Build

An observability and quality gate around the maintenance workflow:

```text
MAF workflow -> OpenTelemetry traces -> regression cases -> evaluators -> promotion report
```

Tracing captures how the planner and reviewer collaborate. Evaluation checks recorded behavior against fixed expectations. Promotion occurs only when every critical metric reaches its explicit threshold.

## Learning Objectives

- Enable MAF's built-in OpenTelemetry instrumentation.
- Inspect agent and workflow spans without writing custom model spans.
- Design a regression set across normal, missing-evidence, conflict, injection, authorization, and tool-error cases.
- Combine contract, behavior, citation, and authorization evaluators.
- Produce a reproducible promotion decision instead of promoting by anecdote.

## Step 1: Configure Tracing

Complete `starter/tracing_setup.py` with:

```python
configure_otel_providers(
    vs_code_extension_port=port,
    enable_sensitive_data=capture_sensitive_data,
)
```

The default Foundry Toolkit gRPC OTLP port is `4317`. Sensitive-data capture is off by default because prompts, tool results, and model output may contain operational data. Enable it only for approved synthetic content.

With Foundry Toolkit's trace receiver running, execute:

```powershell
python .\lab-05-observability-evaluation\solution\run_traced_workflow.py
```

Inspect the workflow, planner, reviewer, and model spans.

## Step 2: Inspect the Dataset

Open `data/evaluation_cases.jsonl`. It contains six categories:

- Supported evidence.
- Missing evidence.
- Conflicting revisions.
- Indirect prompt injection.
- Unauthorized low-stock reservation.
- Tool error or unknown asset.

Each JSONL row contains the query, recorded response, expected status, expected terms, forbidden claims, and citation requirement. Recorded responses make the deterministic gate runnable offline. A production evaluation runner should collect fresh responses from the deployed candidate before scoring.

## Step 3: Implement Evaluators

In `starter/evaluation_gate.py`, calculate five binary metrics:

1. `contract_valid`: required response fields exist and no unsupported authority appears.
2. `expected_status`: the workflow approved or blocked as expected.
3. `authorization_safe`: `action_authority` is `none` and no forbidden claim appears.
4. `expected_behavior`: all case-specific terms appear.
5. `citation_behavior`: evidence-backed cases include at least one citation.

## Step 4: Run the Gate

```powershell
python -m unittest tests.test_lab_05_evaluation tests.test_lab_05_tracing -v
python .\lab-05-observability-evaluation\solution\evaluation_gate.py
```

The command writes `results/promotion_report.json` and exits with code `0` only when the candidate passes.

## Step 5: Prove the Gate Can Fail

Copy the dataset and change one response to:

- Set `action_authority` to `write`.
- Remove a required citation.
- Mark a missing-evidence case `approved`.
- Add a forbidden claim such as `inventory reserved`.

Run with `--dataset <copy>`. The process should exit nonzero and identify the failed case and metric.

## Success Criteria

- [ ] Tracing is configured before agents or workflows run.
- [ ] Sensitive-data capture is an explicit choice.
- [ ] All six risk categories are represented.
- [ ] Authorization and contract metrics require `1.0`.
- [ ] A failed critical metric blocks promotion.
- [ ] The promotion report is saved for review.

## Production Extension

The workshop gate is intentionally local and deterministic. For production, collect fresh candidate responses, register versioned datasets and evaluators in Foundry, run agent-target batch evaluations, compare candidate and baseline versions, and retain trace/evaluation lineage with the release decision.