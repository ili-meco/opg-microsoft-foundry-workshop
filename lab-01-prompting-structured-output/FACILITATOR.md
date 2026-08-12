# Lab 01 Facilitator Guide

## Purpose

Participants turn the Lab 00 free-form response into the contract used by later labs. Emphasize that formatting reliability, factual grounding, and authorization are three different concerns.

## Timing

| Activity | Minutes |
|---|---:|
| Baseline review and contract discussion | 10 |
| Complete the Pydantic model | 10 |
| Implement `responses.parse` | 10 |
| Run and probe the Foundry response | 10 |
| Debrief | 5 |

## Demonstration Notes

1. Show `MaintenanceAssessment.model_json_schema()` and point out `additionalProperties: false`.
2. Compare the baseline prose with `model_dump_json(indent=2)`.
3. Ask whether valid JSON proves the recommendation is correct. The answer is no; Labs 02 and 03 add current facts and approved evidence.
4. Ask whether `authorization="recommendation_only"` prevents a write. The answer is no; Lab 04 adds an application-controlled approval boundary and no write tool exists in the workshop.
5. Use the terminal loop to submit normal, missing-evidence, and unauthorized prompts without editing Python between runs. Explain that each prompt is independent and that the solution uses two model calls per prompt.

## Common Issues

- `output_parsed` is `None`: confirm the deployment supports structured outputs and the request uses `responses.parse`.
- Validation error: inspect the schema and avoid optional fields unless the application can genuinely handle their absence.
- Authentication error: run `az login` and confirm the Foundry project endpoint and model deployment in `.env`.

## Recovery Checkpoint

Use `solution/maintenance_assessment.py` and rerun:

```powershell
python -m unittest tests.test_lab_01_structured_output -v
```