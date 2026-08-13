# Lab 01 Facilitator Guide: Structured Outputs and Deterministic Tools

## Purpose

Participants first turn the Lab 00 free-form response into a validated contract, then give an agent controlled access to current asset and inventory facts. Emphasize that formatting reliability, factual grounding, and authorization are three different concerns.

## Timing

| Activity | Minutes |
|---|---:|
| Explain instructions, response schemas, and application validation | 8 |
| Complete the Pydantic model and `responses.parse` | 17 |
| Run and probe the structured response | 10 |
| Explain tool schemas and controlled execution | 5 |
| Implement validated lookups and the closed dispatcher | 20 |
| Complete the function schemas and tool-call loop | 15 |
| Run tests, invoke Foundry, and debrief | 15 |

## Demonstration Notes

1. Show `MaintenanceAssessment.model_json_schema()` and point out `additionalProperties: false`.
2. Compare the baseline prose with `model_dump_json(indent=2)`.
3. Ask whether valid JSON proves the recommendation is correct. The answer is no; Part B adds current structured facts and Lab 03 adds approved procedural evidence.
4. Ask whether `authorization="recommendation_only"` prevents a write. The answer is no; Lab 04 adds an application-controlled approval boundary and no write tool exists in the workshop.
5. Use the terminal loop to submit normal, missing-evidence, and unauthorized prompts without editing Python between runs. Explain that each prompt is independent and that the solution uses two model calls per prompt.
6. Transition with: "The result is now predictable, but its facts can still be stale or invented. Next, the application will expose two controlled read-only tools."
7. Continue with [Part B facilitator notes](part-b-tools/FACILITATOR.md). Demonstrate `ASSET-104`, malformed input, an unknown identifier, and an unauthorized reservation request.

## Common Issues

- `output_parsed` is `None`: confirm the deployment supports structured outputs and the request uses `responses.parse`.
- Validation error: inspect the schema and avoid optional fields unless the application can genuinely handle their absence.
- Authentication error: run `az login` and confirm the Foundry project endpoint and model deployment in `.env`.
- Tool call has no final answer: confirm every function output is submitted with the same conversation ID.
- Only one installed part is checked: confirm the loop handles every output item and allows another tool-call round.

## Recovery Checkpoint

Use `solution/maintenance_assessment.py` and rerun:

```powershell
python -m unittest tests.test_lab_01_structured_output -v
python -m unittest tests.test_lab_01_tools tests.test_lab_01_agent_tools -v
```