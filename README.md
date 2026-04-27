# Policy Agentforce

Low-fidelity policy lifecycle workspaces, demos, flows, and wireframes for a Block policy operations experience.

This repository currently focuses on:

- `quincy`, a standalone QC assistant for proposed Policy and Standard changes
- a `Compliance Governance / Policy Team` workflow model
- subagent prototypes aligned to Block's `Compliance Policy on Policies`

The public GitHub Pages experience is now organized around a simpler end-to-end story:

1. start in the `launcher`
2. move into the `simplified step flow`
3. continue into simplified `governance review`
4. optionally branch into `returned fixes`
5. use the advanced workspaces, `policy bot`, and `ruleset QC` pages as supporting views rather than the default primary flow

## What quincy does

The webpage should be positioned as a pre-submission QC layer that sits between the in-progress Google Doc and the formal LogicGate workflow.

In this model, LogicGate remains the system of record for the compliance process, but the actual drafting still begins in the static Google Doc referenced in the LogicGate field `Verified Link to Editable Document (In Progress Version)`. That Google Doc is the working draft where document owners and submitters make redlined edits over time.

quincy is a standalone Policy QC Assistant that helps Block employees review proposed changes to Compliance Policies and Standards against the Policy on Policies checklist using the existing in-progress Google Doc from LogicGate, then generates a change summary and one-page QC audit trail for submission.

The QC Assistant evaluates the proposed changes against the Policy on Policies tollgate checklist, identifies required fixes and recommended enhancements, and generates a submission package consisting of:

- the existing verified Google Doc link as the authoritative working draft
- a summary of the proposed changes
- a one-page QC audit trail showing checklist completion and supporting evidence

## Start here

- [Open the launcher](./index.html)
- [Open the simplified step flow](./mockups/step_01_owner_confirm_inputs.html)
- [Open the owner workspace](./mockups/document_owner_annual_refresh_mockup.html)
- [Open the governance workspace](./mockups/governance_team_mockup.html)
- [Open the returned-item workspace](./mockups/document_owner_returned_by_governance_mockup.html)
- [Open the connected flow](./mockups/end_to_end_process_flow.html)
- [Open the policy bot demo](./mockups/policy_bot_demo_mockup.html)
- [Open the ruleset QC demo](./mockups/ruleset_qc_demo_mockup.html)
- [View the annual refresh user story](./wireframes/document_owner_annual_refresh_user_story.md)

## Current Pages on GitHub Pages

### `launcher`

- [`index.html`](./index.html)
  The primary entry point for the Pages experience. It is now organized around the real process entry points:
  - `Start owner QC`
  - `Continue governance review`
  - `Resolve returned fixes`
  - the simplified step flow as the default happy path
  - advanced workspaces and assist demos as secondary paths

### `main story`

- [`mockups/step_01_owner_confirm_inputs.html`](./mockups/step_01_owner_confirm_inputs.html)
  The first simplified page in the happy-path flow. It focuses only on confirming the required owner inputs.
- [`mockups/step_02_owner_run_qc.html`](./mockups/step_02_owner_run_qc.html)
  The second simplified page in the happy-path flow. It focuses only on the quincy QC pass and the first-pass output.
- [`mockups/step_03_owner_resolve_blockers.html`](./mockups/step_03_owner_resolve_blockers.html)
  The third simplified page in the happy-path flow. It focuses only on the must-fix items that still block handoff.
- [`mockups/step_04_owner_export_package.html`](./mockups/step_04_owner_export_package.html)
  The fourth simplified page in the happy-path flow. It focuses only on exporting the owner package.
- [`mockups/step_05_governance_review_packet.html`](./mockups/step_05_governance_review_packet.html)
  The fifth simplified page in the happy-path flow. It focuses only on governance review of the imported package.
- [`mockups/step_06_approval_publish.html`](./mockups/step_06_approval_publish.html)
  The final simplified page in the happy-path flow. It shows the approval-and-publication continuation after governance accepts the package.
- [`mockups/document_owner_annual_refresh_mockup.html`](./mockups/document_owner_annual_refresh_mockup.html)
  The advanced owner workspace. It still contains the original all-in-one owner QC prototype for denser review.
- [`mockups/governance_team_mockup.html`](./mockups/governance_team_mockup.html)
  The advanced governance workspace. It still contains the original all-in-one governance review prototype with queue and packet detail.

### `alternate branch`

- [`mockups/document_owner_returned_by_governance_mockup.html`](./mockups/document_owner_returned_by_governance_mockup.html)
  The targeted return loop. This page is now framed as the alternate branch after governance sends back focused fixes, while preserving the original package context.

### `orientation and support`

- [`mockups/end_to_end_process_flow.html`](./mockups/end_to_end_process_flow.html)
  A connected lifecycle map showing how owner review, governance review, returned fixes, and assist demos connect.
- [`mockups/policy_bot_demo_mockup.html`](./mockups/policy_bot_demo_mockup.html)
  A GitHub Pages-safe policy Q&A demo with grounded answers, citations, source preview, and guided question flow.
- [`mockups/ruleset_qc_demo_mockup.html`](./mockups/ruleset_qc_demo_mockup.html)
  A GitHub Pages-safe demo of Google Doc + markdown ruleset + provider-driven QC, with a guided 6-step flow and export outputs.

## Repository structure

### top-level page

- [`index.html`](./index.html)
  Launcher page for the GitHub Pages experience, organized around real process entry points and a happy-path demo flow

### `mockups/`

- [`end_to_end_process_flow.html`](./mockups/end_to_end_process_flow.html)
  Connected flow showing the simplified step-by-step happy path, the returned-item alternate branch, the advanced workspaces, and the assist demos
- [`step_01_owner_confirm_inputs.html`](./mockups/step_01_owner_confirm_inputs.html)
  Simplified step page for confirming the working Google Doc, owner delta, and draft inputs
- [`step_02_owner_run_qc.html`](./mockups/step_02_owner_run_qc.html)
  Simplified step page for running the quincy QC pass
- [`step_03_owner_resolve_blockers.html`](./mockups/step_03_owner_resolve_blockers.html)
  Simplified step page for clearing the must-fix blockers
- [`step_04_owner_export_package.html`](./mockups/step_04_owner_export_package.html)
  Simplified step page for packaging and exporting the owner handoff
- [`step_05_governance_review_packet.html`](./mockups/step_05_governance_review_packet.html)
  Simplified step page for reviewing the imported package in governance
- [`step_06_approval_publish.html`](./mockups/step_06_approval_publish.html)
  Simplified step page for the approval-and-publication continuation of the happy path
- [`document_owner_annual_refresh_mockup.html`](./mockups/document_owner_annual_refresh_mockup.html)
  Advanced owner workspace for annual refresh and proposed-change QC
- [`document_owner_returned_by_governance_mockup.html`](./mockups/document_owner_returned_by_governance_mockup.html)
  Returned-item workspace for targeted owner fixes after Governance review; the alternate branch in the lifecycle
- [`governance_team_mockup.html`](./mockups/governance_team_mockup.html)
  Advanced governance workspace for queue triage, Tollgate 3 QC, approval routing, publication, and maintenance decisions
- [`policy_bot_demo_mockup.html`](./mockups/policy_bot_demo_mockup.html)
  GitHub Pages-safe policy bot demo with grounded answers, citations, source preview, and guided next actions
- [`ruleset_qc_demo_mockup.html`](./mockups/ruleset_qc_demo_mockup.html)
  GitHub Pages-safe ruleset QC demo for Google Doc + markdown ruleset + provider-driven QC with a guided step-by-step flow

### `wireframes/`

- [`document_owner_qc_assistant_wireframe.svg`](./wireframes/document_owner_qc_assistant_wireframe.svg)
  Focused quincy pre-submission QC assistant screen
- [`document_owner_annual_refresh_user_story.md`](./wireframes/document_owner_annual_refresh_user_story.md)
  Detailed step-by-step owner workspace interaction model
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

### `rulesets/`

- [`RULESET_FORMAT.md`](./rulesets/RULESET_FORMAT.md)
  Parser contract and authoring format for reusable markdown QC rulesets
- [`policy_on_policies_qc_ruleset.md`](./rulesets/policy_on_policies_qc_ruleset.md)
  Reusable markdown QC ruleset for document-owner self-review of Google Docs drafts
- [`sample_result.json`](./rulesets/sample_result.json)
  Example normalized output payload for a ruleset-driven QC run

### `scripts/`

- [`ingest_policy_pdfs.py`](./scripts/ingest_policy_pdfs.py)
  Downloads published PDFs from Google Drive, extracts text, and writes chunks into Snowflake
- [`query_policy_bot.py`](./scripts/query_policy_bot.py)
  CLI query tool for grounded policy answers with citations
- [`policy_bot_web.py`](./scripts/policy_bot_web.py)
  Lightweight local web server for the policy bot chat UI
- [`run_ruleset_qc.py`](./scripts/run_ruleset_qc.py)
  Ruleset-driven QC runner for Google Docs drafts using a markdown ruleset and selected LLM provider
- [`ruleset_qc_web.py`](./scripts/ruleset_qc_web.py)
  Lightweight local web server for the ruleset-driven QC UI
- [`run_ruleset_qc_web.sh`](./scripts/run_ruleset_qc_web.sh)
  Helper script to start the local ruleset QC web UI with `.env` loaded

### `ui/`

- [`policy_bot_chat.html`](./ui/policy_bot_chat.html)
  Local browser chat interface for querying active Policies and Standards against Snowflake-backed retrieval
- [`ruleset_qc.html`](./ui/ruleset_qc.html)
  Local browser interface for Google Doc URL + markdown ruleset upload + QC execution

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

## Current UX state

The mockups have been simplified and standardized around a clearer end-to-end flow:

- a shared darker Block-style dashboard shell
- a launcher that behaves like the real process entry point instead of a page gallery
- a cleaner happy-path demo story: `launcher → simplified step flow → simplified governance review`
- the noisiest owner and governance moments now also exist as dedicated single-purpose step pages
- the returned-item workspace framed as an alternate branch rather than part of the default click-through
- shared lifecycle breadcrumbs, mini-maps, step rails, progress summaries, and next-best-action modules across the core workspaces
- more consistent CTA wording, helper copy, spacing, and action alignment across the main Pages flow

## Ruleset-driven Google Doc QC MVP

The repo now includes a lightweight MVP for a different QC approach:

- a working Google Doc draft remains the source document
- a reusable markdown ruleset defines the QC checks
- the owner chooses the LLM provider and model
- the runner returns normalized JSON and an optional markdown report

Core assets:

- [`rulesets/RULESET_FORMAT.md`](./rulesets/RULESET_FORMAT.md)
- [`rulesets/policy_on_policies_qc_ruleset.md`](./rulesets/policy_on_policies_qc_ruleset.md)
- [`rulesets/sample_result.json`](./rulesets/sample_result.json)
- [`scripts/run_ruleset_qc.py`](./scripts/run_ruleset_qc.py)

Example dry run:

```bash
python3 scripts/run_ruleset_qc.py \
  --google-doc-url "https://docs.google.com/document/d/YOUR_DOC_ID/edit" \
  --ruleset rulesets/policy_on_policies_qc_ruleset.md \
  --dry-run \
  --output /tmp/ruleset-qc-dry-run.json
```

Example live run with Anthropic:

```bash
export ANTHROPIC_API_KEY="YOUR_KEY"
export LLM_PROVIDER="auto"

python3 scripts/run_ruleset_qc.py \
  --google-doc-url "https://docs.google.com/document/d/YOUR_DOC_ID/edit" \
  --ruleset rulesets/policy_on_policies_qc_ruleset.md \
  --provider anthropic \
  --model claude-3-5-sonnet-latest \
  --output /tmp/ruleset-qc-result.json \
  --report-output /tmp/ruleset-qc-report.md
```

Local web UI:

```bash
./scripts/run_ruleset_qc_web.sh
```

Then open:

```text
http://127.0.0.1:8090
```

## Policy bot setup

The policy bot uses:

- `LOGICGATE_SF.PUBLIC.POLICY_DASHBOARD` as the filtered LogicGate source
- `LOGICGATE_SF.POLICY_BOT.DOCUMENTS` as the active document registry
- `LOGICGATE_SF.POLICY_BOT.DOCUMENT_CHUNKS` as the searchable content table
- Google Drive published PDFs as the content source

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local env file:

```bash
cp .env.example .env
```

Then edit `.env` and fill in your real credentials and paths.

If you prefer manual exports instead, use:

```bash
export SF_ACCOUNT="SQUARE"
export SF_USER="YOUR_USER"
export SF_PASSWORD="YOUR_PASSWORD"
export SF_WAREHOUSE="YOUR_WAREHOUSE"
export SF_DATABASE="LOGICGATE_SF"
export SF_SCHEMA="POLICY_BOT"
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account.json"
```

Optional for LLM synthesis in the query layer and web UI:

```bash
export LLM_PROVIDER="auto"
export ANTHROPIC_API_KEY="YOUR_KEY"
export OPENAI_API_KEY="YOUR_KEY"
```

`LLM_PROVIDER=auto` will prefer Anthropic when `ANTHROPIC_API_KEY` is present and otherwise fall back to OpenAI.

## Policy bot workflow

1. Ingest active published PDFs into the chunk table:

```bash
python3 scripts/ingest_policy_pdfs.py --limit 3 --dry-run
python3 scripts/ingest_policy_pdfs.py --limit 3
```

2. Query the chunked corpus from the command line:

```bash
python3 scripts/query_policy_bot.py "What policy governs third-party due diligence?"
python3 scripts/query_policy_bot.py "What is the record retention requirement?" --document-type Policy
python3 scripts/query_policy_bot.py "What policy governs third-party due diligence?" --use-llm
python3 scripts/query_policy_bot.py "What policy governs third-party due diligence?" --use-llm --provider anthropic --model claude-3-5-sonnet-latest
```

3. Run the local web chat UI:

```bash
./scripts/run_policy_bot.sh
```

Then open:

```text
http://127.0.0.1:8080
```

If you prefer to launch manually instead of using the helper script:

```bash
source .venv/bin/activate
python3 scripts/policy_bot_web.py
```

Recommended test order:

- run ingestion on 1-3 documents first
- validate `DOCUMENT_CHUNKS` in Snowflake
- test CLI retrieval without `--use-llm`
- compare the same query with `--use-llm` using Anthropic or OpenAI
- then use the web UI for a more realistic employee experience

For demos without a local server, use:

- [`mockups/policy_bot_demo_mockup.html`](./mockups/policy_bot_demo_mockup.html)
  Open the policy bot demo on GitHub Pages when you want a static walkthrough without the local server

## Publishing

This repo includes:

- a root [`index.html`](./index.html) for GitHub Pages
- a [`.nojekyll`](./.nojekyll) file for simpler static hosting

Once GitHub Pages is enabled from `main` and `/(root)`, the site should publish from:

- `https://hreynolds95.github.io/policy-agentforce/`

## Next build ideas

- turn quincy into a LogicGate-connected intake and packaging spec
- add a governance-side clickable prototype
