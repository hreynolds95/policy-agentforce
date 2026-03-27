# Policy Lifecycle Subagent Prototypes

This folder contains a first-cut prototype set for subagents that support two primary user groups in the Block compliance policy lifecycle:

- `Document Owners`
- `Compliance Governance / Policy Team`

The prototypes are aligned to the February 18, 2026 `Compliance Policy on Policies` and are designed around the Block lifecycle requirements:

- Only `Policies` and `Standards` are in scope for Policy Team governance
- The lifecycle follows `Tollgate 1` through `Tollgate 4`
- New documents require conflict checks against existing inventory
- Owners use approved templates and maintain clean + redline versions
- Owners attest to content before formal approvals
- Approvals follow a `Tier 1 / Tier 2 / Tier 3` model
- Publication occurs to the `system of record (LogicGate)` and `Go/Policy`
- Ongoing maintenance includes annual review, off-cycle changes, deferments, exceptions, and retirement

## Files

- [`document_owner_agents.yaml`](/Users/hreynolds/Documents/policy%20agentforce/prototypes/document_owner_agents.yaml)
  Primary Document Owner agent and supporting subagents
- [`governance_agents.yaml`](/Users/hreynolds/Documents/policy%20agentforce/prototypes/governance_agents.yaml)
  Primary Governance agent and supporting subagents
- [`policy_lifecycle_state_model.yaml`](/Users/hreynolds/Documents/policy%20agentforce/prototypes/policy_lifecycle_state_model.yaml)
  LogicGate-friendly lifecycle stages, statuses, transitions, and decision points
- [`example_payloads.json`](/Users/hreynolds/Documents/policy%20agentforce/prototypes/example_payloads.json)
  Example requests, outputs, and handoff payloads

## Recommended prototype structure

Use two top-level agents in the product experience:

1. `Document Owner Copilot`
2. `Governance Team Copilot`

Each top-level agent orchestrates smaller subagents with narrow responsibilities. This preserves the approvals and decision rights defined in the PoP while still accelerating drafting, review, routing, and monitoring.

## Suggested UI split

### Document Owner interface

The Document Owner UI should focus on:

- Intake initiation
- Scope and conflict-check questions
- Drafting and redline management
- Stakeholder review coordination
- Owner attestation
- Implementation plans and awareness tasks
- Annual review and off-cycle change initiation

### Compliance Governance interface

The Governance Team UI should focus on:

- Intake triage and in-scope validation
- Tiering and governance metadata
- QC checklist execution
- Approval routing control
- Publication and record retention
- Review calendar management
- Deferment, exception, and retirement tracking

## Guardrail summary

- Subagents may recommend, summarize, validate, route, and monitor
- Subagents may not grant approvals reserved to Owners, Compliance Leadership, CPC, or Boards
- Procedures may be referenced, but they are not governed by the Policy Team under this PoP
- Material changes must preserve approval evidence, redlines or change summaries, and revision history

## How to use this prototype pack

1. Start with the lifecycle model to define LogicGate workflow stages.
2. Map the top-level agents to the two UI surfaces.
3. Implement subagents as modular skills, prompts, or services.
4. Use the example payloads to define API contracts or database records.
5. Add user-facing forms, queues, and notifications after the core handoffs are stable.
