# Policy Agentforce

Low-fidelity policy lifecycle prototypes, wireframes, and clickable quincy mockups for a Block policy operations experience.

This repository currently focuses on:

- `quincy`, a standalone QC assistant for proposed Policy and Standard changes
- a `Compliance Governance / Policy Team` workflow model
- subagent prototypes aligned to Block's `Compliance Policy on Policies`

## What quincy does

The webpage should be positioned as a pre-submission QC layer that sits between the in-progress Google Doc and the formal LogicGate workflow.

In this model, LogicGate remains the system of record for the compliance process, but the actual drafting still begins in the static Google Doc referenced in the LogicGate field `Verified Link to Editable Document (In Progress Version)`. That Google Doc is the working draft where document owners and submitters make redlined edits over time.

quincy is a standalone Policy QC Assistant that helps Block employees review proposed changes to Compliance Policies and Standards against the Policy on Policies checklist using the existing in-progress Google Doc from LogicGate, then generates a change summary and one-page QC audit trail for submission.

The QC Assistant evaluates the proposed changes against the Policy on Policies tollgate checklist, identifies required fixes and recommended enhancements, and generates a submission package consisting of:

- the existing verified Google Doc link as the authoritative working draft
- a summary of the proposed changes
- a one-page QC audit trail showing checklist completion and supporting evidence

## Start here

- [Open the quincy annual refresh mockup](./mockups/document_owner_annual_refresh_mockup.html)
- [Open the quincy return-to-owner mockup](./mockups/document_owner_returned_by_governance_mockup.html)
- [Open the GitHub Pages landing page](./index.html)
- [View the owner annual refresh user story](./wireframes/document_owner_annual_refresh_user_story.md)

## Repository structure

### `mockups/`

- [`document_owner_annual_refresh_mockup.html`](./mockups/document_owner_annual_refresh_mockup.html)
  Standalone clickable HTML prototype for quincy's annual refresh and proposed-change QC flow
- [`document_owner_returned_by_governance_mockup.html`](./mockups/document_owner_returned_by_governance_mockup.html)
  Standalone clickable HTML prototype for quincy after Governance returns the package for fixes

### `wireframes/`

- [`document_owner_qc_assistant_wireframe.svg`](./wireframes/document_owner_qc_assistant_wireframe.svg)
  Focused quincy pre-submission QC assistant screen
- [`document_owner_annual_refresh_user_story.md`](./wireframes/document_owner_annual_refresh_user_story.md)
  Detailed step-by-step owner interaction model
- [`document_owner_wireframe.svg`](./wireframes/document_owner_wireframe.svg)
  Broader owner workspace concept
- [`governance_team_wireframe.svg`](./wireframes/governance_team_wireframe.svg)
  Governance-side workflow interface

### `prototypes/`

- [`document_owner_agents.yaml`](./prototypes/document_owner_agents.yaml)
  Document Owner Copilot and subagent definitions
- [`governance_agents.yaml`](./prototypes/governance_agents.yaml)
  Governance Team Copilot and subagent definitions
- [`policy_lifecycle_state_model.yaml`](./prototypes/policy_lifecycle_state_model.yaml)
  LogicGate-friendly lifecycle states and transitions
- [`example_payloads.json`](./prototypes/example_payloads.json)
  Example request and handoff payloads

## Current experience concept

The current quincy concept is intentionally narrow:

1. A proposer or document owner opens the Google Doc referenced in LogicGate’s `Verified Link to Editable Document (In Progress Version)` field.
2. They draft or redline changes in that same Google Doc over time.
3. They bring the draft into quincy and explain the delta.
4. quincy runs the Policy on Policies tollgate quality checks.
5. quincy identifies required fixes and recommended enhancements.
6. The owner resolves `Must fix` items and optionally accepts recommended enhancements.
7. quincy prepares the supporting submission artifacts: a change summary and a one-page QC audit trail.

This avoids making owners work through a full governance workflow while still preserving Policy Team standards and keeping the verified Google Doc as the authoritative working draft.

## Publishing

This repo includes:

- a root [`index.html`](./index.html) for GitHub Pages
- a [`.nojekyll`](./.nojekyll) file for simpler static hosting

Once GitHub Pages is enabled from `main` and `/(root)`, the site should publish from:

- `https://hreynolds95.github.io/policy-agentforce/`

## Next build ideas

- turn quincy into a LogicGate-connected intake and packaging spec
- add a governance-side clickable prototype
