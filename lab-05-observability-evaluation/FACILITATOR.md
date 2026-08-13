# Lab 05 Facilitator Guide

## Purpose

Participants instrument the MAF workflow and replace subjective release confidence with a reproducible regression gate.

## Timing

| Activity | Minutes |
|---|---:|
| Configure and inspect tracing | 15 |
| Review the six-case dataset | 10 |
| Implement deterministic evaluators | 15 |
| Run and deliberately fail the gate | 15 |
| Production extension discussion | 5 |

## Key Teaching Points

- Configure OpenTelemetry before creating clients, agents, or workflows.
- MAF already instruments model, agent, and workflow operations; avoid redundant custom spans in this lab.
- Do not capture sensitive prompt content by default.
- A passing recorded dataset proves the gate logic, not the live candidate. Production runs must collect fresh outputs from the exact candidate version.
- Critical safety and authorization metrics use a threshold of `1.0` because averaging can hide a severe single-case failure.

## Expected Baseline

The supplied six-case dataset produces:

```text
contract_valid      1.0
expected_readiness  1.0
authorization_safe  1.0
expected_behavior   1.0
citation_behavior   1.0
promotion           PASS
```

## Recovery Checkpoint

Use the `solution/` files and run:

```powershell
python -m unittest tests.test_lab_05_evaluation tests.test_lab_05_tracing -v
python .\lab-05-observability-evaluation\solution\evaluation_gate.py
```

## Debrief Questions

- Which metrics should be deterministic versus model-graded?
- What trace fields are useful without exposing sensitive content?
- Why must candidate and baseline use the same dataset and thresholds?
- Which failures should stop a release even if the aggregate score is high?