# Ruleset Format

This format is designed for `document owner self-QC` of Google Docs drafts.

## File shape

1. A single `# Ruleset Metadata` block at the top of the file
2. One or more `## Rule` blocks
3. `key: value` pairs only
4. No nested YAML, lists, or markdown tables in MVP v1

## Required metadata fields

- `name`
- `version`
- `document_type`
- `document_source`
- `intended_use`
- `default_output_mode`

## Required rule fields

- `id`
- `title`
- `severity`
- `enabled`
- `check_type`
- `instructions`
- `evidence_mode`
- `enhancement_mode`
- `pass_criteria`
- `failure_message`

## Recommended enums

### `severity`

- `must`
- `recommended`
- `info`

### `check_type`

- `presence`
- `quality`
- `consistency`
- `reference`
- `clarity`

### `evidence_mode`

- `quote`
- `quote_or_missing`
- `summary_only`

### `enhancement_mode`

- `none`
- `suggest_language`
- `suggest_list`
- `rewrite_section`

## Example

```md
# Ruleset Metadata
name: Block Policy on Policies QC
version: 0.1
document_type: Policy
document_source: Google Docs
intended_use: Document owner self-QC
default_output_mode: findings_and_enhancements

## Rule
id: required_sections
title: Required Sections Present
severity: must
enabled: true
check_type: presence
instructions: Confirm the document includes purpose, scope, owner, review cadence, and related documents.
evidence_mode: quote_or_missing
enhancement_mode: suggest_language
pass_criteria: All required sections are clearly present.
failure_message: One or more required sections are missing or incomplete.
```

## Output contract

The MVP runner should produce:

- normalized JSON
- optional markdown report

The normalized JSON shape is demonstrated in [`sample_result.json`](./sample_result.json).
