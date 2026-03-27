# Document Owner Annual Refresh User Story

This user story assumes:

- the document is already in LogicGate
- the document is due for its annual review or refresh
- the owner remains inside LogicGate for the owner-side experience
- the page is a pre-submission quality checkpoint before the record returns to the Governance workflow

The goal is to make annual refresh fast for owners while still aligning to the Block `Compliance Policy on Policies`.

## Primary user

- `Document Owner`

## Supporting user

- `Delegate`

## Trigger

LogicGate sends a notification:

- in-app task
- email
- dashboard alert

### Example notification

`Annual review due in 14 days: Third-Party Compliance Oversight Policy`

Action:

- `Open annual refresh`

## Screen entry state

When the owner opens the task, the page should already be populated from the LogicGate record.

### Header components

- `Document title`
- `LogicGate record ID`
- `Document type`
- `Compliance domain`
- `Tier`
- `Current stage`
- `Next review due date`
- `Last approval date`
- `Owner`
- `Delegate`

### Right-side status chips

- `Annual refresh due`
- `Draft check not started`

### Read-only context modules

- last approved version link
- last redline or change summary link
- related documents
- prior approver path
- open exceptions, if any

## Step 1: Owner confirms refresh type

The first interaction should be a short prompt block, not a large form.

### Components

- radio: `No substantive changes`
- radio: `Updated content`
- radio: `Potential material change`
- text area: `What changed since last approval?`
- checkbox: `Legal review may be needed`
- checkbox: `Related documents may need updates`
- checkbox: `Retention language may need updates`

### System behavior

- If the owner selects `No substantive changes`, the UI still requires the owner to upload the refreshed clean version or confirm that the current approved version remains accurate.
- If the owner selects `Potential material change`, the page should highlight that the document will likely need fuller evidence and approval routing.

### Status change

- `Draft check not started` -> `Refresh type captured`

## Step 2: Owner uploads review package

The UI should center on uploads because that is the natural owner workflow.

### Required components

- upload zone: `Clean draft`
- upload zone: `Redline`
- alternate upload zone: `Change summary` when rewrite is selected

### Optional components

- upload zone: `Stakeholder review evidence`
- upload zone: `Legal review evidence`
- upload zone: `Supporting reference`

### Auto-detected metadata

After upload, the page should display:

- last modified date
- file comparison status
- whether redline or change summary is present
- whether the uploaded title matches the LogicGate record

### Status change

- `Refresh type captured` -> `Files uploaded`

## Step 3: Agent runs PoP QC

The owner should not manually navigate the checklist. The agent runs it and translates it into plain language.

### Primary action

- button: `Run annual refresh QC`

### What the agent checks

- required template sections
- related documents list
- scope completeness
- roles and responsibilities consistency
- record retention language
- glossary and terminology consistency
- procedural wording inside a Policy
- presence of clean draft plus redline or change summary
- likely evidence gaps for Tollgate 3 handoff

### Output modules

- `Must fix before submit`
- `Recommended improvements`
- `Checklist summary`
- `Suggested text`
- `Submission readiness`

### Example required findings

- Related Documents section missing linked Standard
- Record Retention section missing detail
- Scope section missing one entity

### Example recommended findings

- simplify one paragraph into plainer business language
- replace procedural wording with policy language
- align one glossary term with approved definitions

### Status change

- `Files uploaded` -> `QC complete`

## Step 4: Owner resolves findings

The UI should make each finding immediately actionable.

### For each finding, show:

- issue title
- why it matters
- source checklist area
- suggested enhancement
- actions:
  - `Accept suggestion`
  - `Edit myself`
  - `Dismiss with note`

### Helpful controls

- filter: `Must fix`
- filter: `Recommended`
- toggle: `Show suggested text`
- button: `Re-run QC`

### Status logic

- If at least one required finding is still open:
  - status = `Needs owner updates`
- If no required findings remain:
  - status = `Ready for submission`

## Step 5: Owner reviews submission readiness

The owner should not need to infer whether the package is complete.

### Readiness panel components

- `Required fixes open: count`
- `Recommended items open: count`
- `Package completeness: yes/no`
- `Expected next stage: Governance QC queue`

### Included package preview

- clean draft
- redline or change summary
- QC summary
- owner change explanation
- optional evidence attachments

### Status change

- `Needs owner updates` -> `Ready for submission`

## Step 6: Owner submits back into LogicGate workflow

This should be one clear action.

### Primary CTA

- `Submit to Governance queue`

### Confirmation modal

Show:

- package contents
- unresolved recommended improvements count
- expected next stage

### After submit

The page becomes read-only for the owner unless Governance returns it.

### Status change

- `Ready for submission` -> `Submitted to Governance`

## Governance handoff behavior

After submit, LogicGate should automatically:

- update the record stage to `Tollgate 3 QC review`
- attach the owner package
- store the QC output
- notify the Governance queue
- record the owner submission timestamp

## If Governance returns it

The owner should not restart from zero.

### Returned state

- status chip: `Returned by Governance`
- return reason summary
- list of remaining required issues
- prior uploaded files preserved
- prior accepted suggestions preserved

### CTA

- `Resume fixes`

## Time-saving mechanics

This page saves time because it:

- auto-fills all existing LogicGate metadata
- asks only change-specific questions
- uses uploads as the main input
- translates policy checklists into plain-language findings
- suggests fixes, not just problems
- creates a single package for handoff
- avoids duplicate data entry between owner and governance stages

## Recommended statuses

- `Annual refresh due`
- `Refresh type captured`
- `Files uploaded`
- `QC complete`
- `Needs owner updates`
- `Ready for submission`
- `Submitted to Governance`
- `Returned by Governance`

## Recommended on-screen components summary

### Header

- title
- record ID
- tier
- due date
- status chips

### Left column

- refresh type prompt
- upload zones

### Center column

- must-fix findings
- recommended improvements
- checklist summary
- suggested text

### Right column

- readiness panel
- package preview
- activity log
- submit CTA
