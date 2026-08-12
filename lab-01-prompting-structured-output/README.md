# Lab 01: Prompting and Structured Outputs

**Duration:** 45 minutes | **Skill level:** Beginner

## What You Will Build

A maintenance assessment whose shape is enforced by the Responses API and Pydantic. You will compare a free-form baseline with a validated result that separates facts, assumptions, risk, evidence gaps, recommendations, and authorization.

```text
Maintenance request -> instructions -> model -> strict JSON schema -> validated object
```

## Learning Objectives

- Separate behavioral instructions from an output contract.
- Use `client.responses.parse` with a Pydantic model.
- Reject unexpected fields and constrain enumerated values.
- Fail closed when no parsed result is returned.
- Explain why structured output improves reliability but does not prove factual accuracy.

## Step 1: Run the Offline Contract Tests

From the repository root:

```powershell
python -m unittest tests.test_lab_01_structured_output -v
```

The tests validate the solution contract without calling Azure.

## Step 2: Complete the Contract

Open `starter/maintenance_assessment.py` and complete the TODOs. Add:

- `recommended_actions: list[str]`
- `missing_evidence: list[str]`
- `requires_escalation: bool`
- `authorization: Literal["recommendation_only"]`

Keep `extra="forbid"`. This causes unexpected model fields to fail validation instead of silently entering the application.

## Step 3: Request Parsed Output

Implement `request_structured_assessment` with:

```python
response = client.responses.parse(
    model=model_name,
    instructions=ASSESSMENT_INSTRUCTIONS,
    input=request,
    text_format=MaintenanceAssessment,
)
```

Return `response.output_parsed`, but raise an error when it is `None`. The completed implementation is in `solution/maintenance_assessment.py`.

## Step 4: Run Against Foundry

Authenticate and run the solution:

```powershell
az login
python .\lab-01-prompting-structured-output\solution\run_assessment.py
```

The script prints a free-form baseline and the validated structured response. Compare what is predictable in each result.

## Step 5: Probe the Boundary

Change `SAMPLE_REQUEST` and try:

- A report with no asset identifier.
- A request to approve a work order.
- A request with observations but no current measurements.

The output must retain `authorization: "recommendation_only"`. That field is an application contract, not an Azure permission or a substitute for an approval workflow.

## Success Criteria

- [ ] The Pydantic schema rejects additional properties.
- [ ] Risk is constrained to the documented values.
- [ ] Facts and assumptions are separate arrays.
- [ ] Missing evidence and escalation are explicit.
- [ ] The result cannot claim authorization beyond recommendation.

## Discussion

- Which failures can a JSON schema prevent?
- Which claims still require tools or grounding?
- Why should a missing parsed result stop the workflow?