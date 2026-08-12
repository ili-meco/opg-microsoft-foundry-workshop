# Lab 02: Deterministic Agent Tools

**Duration:** 60 minutes | **Skill level:** Intermediate

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

## Step 1: Inspect the Synthetic Systems

Open `data/assets.json` and `data/inventory.json`. Find `ASSET-104`, then inspect both of its installed part numbers. Notice that `PART-310` is low stock. These files stand in for read-only enterprise APIs.

## Step 2: Complete the Deterministic Tools

Open `starter/maintenance_tools.py` and complete the TODOs:

1. Validate IDs before reading data.
2. Return `not_found` for a valid but unknown ID.
3. Return only the matching record for a successful lookup.
4. Dispatch only functions in `TOOL_FUNCTIONS`.

Compare with `solution/maintenance_tools.py` if you need a checkpoint.

## Step 3: Define Strict Tool Schemas

In `starter/maintenance_agent.py`, create one `FunctionTool` per definition. Set `strict=True`, require the identifier, and reject additional properties. Clear descriptions improve tool selection; the schema constrains arguments but does not replace application validation.

## Step 4: Complete the Tool-Call Loop

For each response item whose type is `function_call`:

1. Parse `item.arguments` as JSON.
2. Call the closed dispatcher, not a function name from `globals()` or `eval()`.
3. Serialize the result in a `FunctionCallOutput` with the same `call_id`.
4. Submit all outputs in one follow-up Responses API call using the same conversation.

The completed loop is in `solution/maintenance_agent.py`.

## Step 5: Test Locally

From the repository root:

```powershell
python -m unittest tests.test_lab_02_tools tests.test_lab_02_agent -v
```

These tests do not call Azure. Confirm that malformed IDs, unknown records, unknown tools, multiple tool calls, and malformed JSON are handled without crashing.

## Step 6: Run the Foundry Agent

Authenticate and run the solution:

```powershell
az login
python .\lab-02-agent-tools\solution\maintenance_agent.py
```

The script creates a temporary agent version and conversation, prints each local tool invocation, returns the final answer, and deletes the temporary resources.

Try these requests by changing `SAMPLE_REQUEST`:

- `Check ASSET-104 and all installed parts.`
- `Check ASSET-999.`
- `Reserve PART-310 for ASSET-104.`

The final request should be refused because the tools are read-only.

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