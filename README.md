# Policy Agentforce

Low-fidelity policy lifecycle prototypes, wireframes, and clickable mockups for a LogicGate-centered policy operations experience.

This repository currently focuses on:

- a `Document Owner` annual refresh and pre-submission QC experience
- a `Compliance Governance / Policy Team` workflow model
- subagent prototypes aligned to Block's `Compliance Policy on Policies`

## Start here

- [Open the clickable annual refresh mockup](./mockups/document_owner_annual_refresh_mockup.html)
- [Open the Governance return-to-owner mockup](./mockups/document_owner_returned_by_governance_mockup.html)
- [Open the GitHub Pages landing page](./index.html)
- [View the owner annual refresh user story](./wireframes/document_owner_annual_refresh_user_story.md)

## Repository structure

### `mockups/`

- [`document_owner_annual_refresh_mockup.html`](./mockups/document_owner_annual_refresh_mockup.html)
  Standalone clickable HTML prototype for the Document Owner annual refresh flow
- [`document_owner_returned_by_governance_mockup.html`](./mockups/document_owner_returned_by_governance_mockup.html)
  Standalone clickable HTML prototype for the owner experience after Governance returns the record for fixes

### `wireframes/`

- [`document_owner_qc_assistant_wireframe.svg`](./wireframes/document_owner_qc_assistant_wireframe.svg)
  Focused pre-submission QC assistant screen
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

The current owner-side concept is intentionally narrow:

1. LogicGate notifies the owner that annual refresh is due
2. The owner opens a pre-filled annual refresh page
3. The owner uploads draft changes and explains the delta
4. An agent runs Policy on Policies quality checks
5. The owner resolves `Must fix` items and optionally accepts recommended enhancements
6. The owner submits the package back into the Governance queue

This avoids making owners work through a full governance workflow while still preserving Policy Team standards.

## Publishing

This repo includes:

- a root [`index.html`](./index.html) for GitHub Pages
- a [`.nojekyll`](./.nojekyll) file for simpler static hosting

Once GitHub Pages is enabled from `main` and `/(root)`, the site should publish from:

- `https://hreynolds95.github.io/policy-agentforce/`

## Next build ideas

- turn the owner mockup into a LogicGate field and automation spec
- add a governance-side clickable prototype
