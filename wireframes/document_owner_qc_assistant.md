# Document Owner QC Assistant

This screen assumes the Document Owner is working inside LogicGate and only needs help with the pre-submission quality pass before the normal governance workflow resumes.

## Core design idea

The owner should not have to navigate a full lifecycle workspace. Instead, the UI should behave like a short guided checkpoint:

1. Upload drafted changes
2. Run the Policy on Policies quality checks
3. Review required fixes and recommended enhancements
4. Submit the package back into the LogicGate governance queue

## What the screen should do

### Minimize owner input

The screen should auto-fill from the existing LogicGate record:

- document title
- record ID
- document type
- owner and delegate
- domain
- current tier
- next review date

The owner should only provide:

- clean draft
- redline or change summary
- short answer on what changed
- whether the change is believed to be material or immaterial
- optional supporting evidence if applicable

### Run the PoP QC checks automatically

The agent should check the draft against the Block PoP appendices and return:

- required fixes
- recommended enhancements
- checklist status
- suggested text where useful

The most valuable checks for owners are:

- missing required sections
- incomplete related documents list
- missing or weak record retention language
- scope gaps
- glossary and terminology inconsistency
- procedural wording inside a Policy
- missing redline or change-summary evidence

### Keep output action-oriented

The owner should not receive a long audit report. The UI should group findings into:

- `Must fix before submit`
- `Recommended improvements`
- `Ready to send`

Each finding should support one of three actions:

- accept suggestion
- edit myself
- dismiss with note

## Best simplifications for saving owner time

### 1. Ask only delta questions

Do not re-ask metadata LogicGate already knows. Focus on what changed and what evidence was added.

### 2. Treat uploads as the main input

Owners already work in drafts and redlines. The UI should start with upload, not a long form.

### 3. Collapse checklist language into plain guidance

Instead of showing the full Appendix checklist, translate it into:

- missing section
- missing evidence
- wording issue
- governance metadata gap

### 4. Generate fixes, not just findings

For common issues, the agent should propose:

- draft text for missing sections
- a related-document list
- a change summary
- a retention section prompt

### 5. Show one readiness score

A single readiness panel is easier than multiple statuses. Suggested display:

- package complete: yes or no
- required fixes open: count
- recommended enhancements open: count

### 6. One button back into the main process

The owner should end with one clear action:

- `Submit to Governance queue`

That keeps the owner experience lightweight and avoids duplicating the downstream LogicGate workflow.
