# Lab 01, Part B: Deterministic Agent Tools

**Duration:** 50 minutes | **Skill level:** Intermediate

This is Part B of [Lab 01: Structured Outputs and Deterministic Tools](../lab-01-prompting-structured-output/README.md). Part A made the final model response predictable and validated. Part B adds controlled access to current business facts.

## What You Will Build

A Foundry prompt agent that can look up synthetic asset master data and parts inventory through two local, read-only functions.

```text
User request -> Foundry prompt agent -> function call request
                                          |
                                          v
                                local validated function
                                          |
                                          v
                       function output -> grounded final answer
```

Unlike a model prompt, a tool returns current structured facts from a controlled system boundary. Your application, not the model, decides which functions exist and executes them.

## Learning Objectives

- Define strict JSON schemas for function tools.
- Execute every tool call returned in a response.
- Return structured `ok`, `not_found`, and `error` results.
- Treat model-generated arguments as untrusted input.
- Explain why read access does not imply authority to update work orders or reserve stock.

## Files You Will Use

| File | Purpose |
|---|---|
| `data/assets.json` | Synthetic asset master data. Each asset record includes its operating status and installed part numbers. It stands in for a read-only asset API. |
| `data/inventory.json` | Synthetic parts inventory. It provides quantities and stock status for part numbers returned by the asset lookup. It stands in for a read-only inventory API. |
| `starter/maintenance_tools.py` | The deterministic application boundary. Complete its lookup and dispatch TODOs so model-generated requests can access only validated, allowlisted data functions. |
| `starter/maintenance_agent.py` | The executable agent application. Complete its schema and function-call TODOs; the supplied code handles authentication, temporary agent creation, the terminal loop, and cleanup. |
| `solution/maintenance_tools.py` | Completed reference implementation of the read-only lookups, result envelopes, and closed dispatcher. |
| `solution/maintenance_agent.py` | Completed reference agent that exposes the tools to Foundry and resolves every function call locally. |
| `tests/test_lab_02_tools.py` | Offline tests for identifier validation, record lookup, strict definitions, and rejection of unknown tools. |
| `tests/test_lab_02_agent.py` | Offline tests for SDK tool construction and function-call result handling. Fake response items are used, so no model is called. |

The starter agent imports `maintenance_tools.py` from the same starter folder. The solution agent imports the completed tools from the solution folder.

## Step 1: Inspect the Synthetic Systems

Open `data/assets.json` and `data/inventory.json`. These files are the controlled systems of record for this exercise, not prompt context. Find `ASSET-104`, then inspect both of its installed part numbers. Notice that `PART-310` is low stock. The model must use tools to retrieve these facts instead of guessing them.

## Step 2: Complete the Deterministic Tools

Open `starter/maintenance_tools.py`. This file owns the local functions that actually read data. Complete its TODOs:

1. **Implement `get_asset(asset_id)`.** Validate `ASSET-###` before opening the data file, return `status="not_found"` for a valid unknown ID, and return only the matching asset with `status="ok"`. Validation keeps malformed model arguments away from the data boundary.
2. **Implement `get_parts_inventory(part_number)`.** Apply the same pattern for `PART-###`, but return the matching inventory record. A shared status vocabulary lets the agent distinguish invalid input, absent data, and verified facts.
3. **Implement `execute_tool(tool_name, arguments)`.** Resolve names only through `TOOL_FUNCTIONS`, reject unknown names, and convert argument-shape errors into structured results. The dispatcher is the application allowlist: the model proposes a tool name but cannot choose arbitrary Python code to execute.

`load_records(file_name, key)` is supplied infrastructure. It reads one JSON array and indexes records by the selected key so each tool can retrieve exactly one record.

Compare with `solution/maintenance_tools.py` if you need a checkpoint.

## Step 3: Define Strict Tool Schemas

Open `starter/maintenance_agent.py`. This file translates the local Python capabilities into schemas that Foundry can show to the model, then runs the agent.

Complete `build_function_tools() -> list[Tool]`. Its purpose is to create one SDK `FunctionTool` for each `TOOL_DEFINITIONS` entry. For each tool:

1. Set `name` and `description` from the definition so the model can select the intended capability.
2. Build a JSON object schema with one string property named by `parameter_name` and constrained by `pattern`.
3. Put that property in `required` so an empty call is not valid.
4. Set `additionalProperties=False` so the model cannot add undeclared arguments.
5. Set `strict=True` so Foundry constrains generated arguments to the declared schema.

The schema improves generated calls, but `maintenance_tools.py` still validates at execution time because model output remains untrusted input.

## Step 4: Complete the Tool-Call Loop

In the same starter file, complete `resolve_function_calls(response_output)`. Its purpose is to convert every model-requested function call into a local result that can be sent back to the same Foundry conversation.

For each response item whose type is `function_call`:

1. **Parse `item.arguments` as JSON.** Tool arguments arrive as a string. Catch malformed JSON and return a structured `invalid_json` result instead of crashing.
2. **Call `execute_tool(item.name, arguments)`.** This preserves the allowlist and local validation boundary; never resolve names through `globals()` or `eval()`.
3. **Create `FunctionCallOutput`.** Preserve the original `call_id` so Foundry can match the result to the requested call, and JSON-serialize the result into `output`.
4. **Append every result.** A response can request several tools at once. Returning only the first result would leave the conversation incomplete.

The supplied `invoke_agent()` function submits all collected outputs in one follow-up Responses API call using the same conversation ID. It allows up to four rounds because one result, such as an asset's installed part numbers, can lead to another set of tool calls. Its `finally` block deletes the temporary conversation and agent version even when execution fails.

The completed loop is in `solution/maintenance_agent.py`.

## Step 5: Test Locally

From the repository root:

```powershell
python -m unittest tests.test_lab_02_tools tests.test_lab_02_agent -v
```

These tests establish the deterministic application behavior before a model is involved. They use the synthetic JSON files and fake response items, so they do not authenticate to Azure or consume model tokens.

The tool tests verify successful asset and inventory reads, the low-stock signal, the difference between malformed and unknown identifiers, strict schemas, and rejection of non-allowlisted tools. The agent tests verify SDK `FunctionTool` construction, processing of every requested call, safe malformed-JSON handling, ignored non-tool output, and terminal input behavior.

They do not prove that the model will select the right tool or produce a useful final recommendation. Step 6 tests that live Foundry behavior.

## Step 6: Run the Foundry Agent

Open a VS Code terminal at the repository root, activate the environment, authenticate, and run your completed starter:

```powershell
.\.venv\Scripts\Activate.ps1
az login
python .\lab-02-agent-tools\starter\maintenance_agent.py
```

If you need a checkpoint, run the completed reference implementation from the same terminal:

```powershell
python .\lab-02-agent-tools\solution\maintenance_agent.py
```

For each terminal prompt, the script creates a temporary agent version and conversation, prints each local tool invocation, returns the final answer, and deletes the temporary resources. Type `exit` or `quit` to stop. Each request is independent and may require several billable model calls when the agent performs multiple tool rounds.

Enter these prompts at `Maintenance request (or type 'exit'):`; no Python edits are required:

```text
ASSET-104 has a seal leak. Check the asset record and stock position for every installed part, then tell me what a planner should verify next.
```

```text
Check ASSET-999 and tell me its current operating status.
```

```text
Check asset ../../assets.json and report its installed parts.
```

```text
Reserve PART-310 for ASSET-104 and confirm that the inventory was updated.
```

The unknown and malformed identifiers should become missing evidence rather than invented records. The final request should be refused because the tools are read-only.

## Success Criteria

- [ ] Both tool schemas are strict and reject extra properties.
- [ ] Valid records are returned without model-generated substitutions.
- [ ] Unknown and malformed identifiers produce distinct results.
- [ ] Every function call in one response is returned to the conversation.
- [ ] The agent does not claim to reserve stock, update a work order, or control equipment.

## Discussion

- Which validation belongs in JSON Schema, and which must remain in application code?
- What authorization check would be required before adding a write tool?
- Why is a `not_found` result better than returning an empty string?
- How does validating a final response differ from validating a tool request?

## Combined Lab Outcome

After both parts, you have an application that can validate model output, accept only strictly shaped tool requests, execute only allowlisted read-only functions, and distinguish verified facts from missing evidence. Continue to Lab 03 to add unstructured procedural evidence through Azure AI Search and Foundry IQ.