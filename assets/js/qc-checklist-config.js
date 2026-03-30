/**
 * qc-checklist-config.js
 *
 * Structured Policy on Policies (PoP) quality-control checklist.
 * Each item maps to a specific PoP appendix requirement and carries
 * enough metadata for the QC engine to evaluate it, render it, and
 * link it back to the governing standard.
 *
 * Adding a new PoP requirement is a data change — add an entry here
 * and the engine + UI pick it up automatically.
 */

const QC_CHECKLIST = [
  // ── Must-fix items (block submission) ─────────────────────────
  {
    id: "template",
    label: "Approved template used",
    appendix: "C",
    severity: "must",
    description: "The draft must use the Block-approved Policy or Standard template with all required sections present.",
    autoCheck: true,                       // engine can infer from uploads
    suggestedFix: null,                    // auto-pass — no fix needed when passing
  },
  {
    id: "required_sections",
    label: "Required sections present",
    appendix: "C",
    severity: "must",
    description: "All sections defined in Appendix C must appear in the draft, even if marked 'Not applicable'.",
    autoCheck: true,
    suggestedFix: null,
  },
  {
    id: "related_docs",
    label: "Related documents listed",
    appendix: "A",
    severity: "must",
    description: "The Related Documentation section must reference every linked Policy, Standard, or Procedure shown in the LogicGate record.",
    autoCheck: false,
    suggestedFix: "Add the linked Standard(s) shown in the LogicGate record to the Related Documentation section and note that they should be read in conjunction with this document.",
  },
  {
    id: "retention",
    label: "Record retention language",
    appendix: "A",
    severity: "must",
    description: "The Record Retention section must be specific enough to satisfy the PoP quality check and reference the Data Classification and Handling Policy or any longer applicable regulatory retention standard.",
    autoCheck: false,
    suggestedFix: "Expand the Record Retention section to reference the Data Classification and Handling Policy and any longer applicable legal or regulatory retention requirement.",
  },
  {
    id: "evidence",
    label: "Redline or change summary attached",
    appendix: "A",
    severity: "must",
    description: "A verified editable Google Doc link or a supporting change summary must be attached before submission.",
    autoCheck: true,
    suggestedFix: null,
  },

  // ── Recommended items (improve quality, don't block) ──────────
  {
    id: "scope",
    label: "Scope covers all entities",
    appendix: "A",
    severity: "reco",
    description: "The Scope section should list every in-scope business line and entity indicated in the owner summary.",
    autoCheck: false,
    suggestedFix: "Confirm the entity list with the Owner and update the Scope section to match all in-scope entities.",
  },
  {
    id: "glossary",
    label: "Glossary terms aligned",
    appendix: "A",
    severity: "reco",
    description: "Defined terms should match the standard glossary used across compliance documents.",
    autoCheck: false,
    suggestedFix: "Use the glossary-approved definition and capitalization for the relevant defined term.",
  },
  {
    id: "procedural_wording",
    label: "No procedural language in Policy",
    appendix: "A",
    severity: "reco",
    description: "Policies should contain principle-based requirements. Prescriptive workflow or execution language belongs in a Standard or Procedure.",
    autoCheck: false,
    suggestedFix: "Reframe the clause as a required outcome and move process steps to the supporting Standard or Procedure.",
  },
  {
    id: "plain_language",
    label: "Plain business language used",
    appendix: "A",
    severity: "reco",
    description: "Policy statements should be written in clear, principle-based language rather than implementation-level detail.",
    autoCheck: false,
    suggestedFix: "Replace detailed execution steps with a principle-based policy requirement and move operational specifics to a Standard or Procedure.",
  },
  {
    id: "roles",
    label: "Roles and responsibilities consistent",
    appendix: "C",
    severity: "reco",
    description: "The Roles and Responsibilities section should align with the owner, delegate, and stakeholder information in the LogicGate record.",
    autoCheck: false,
    suggestedFix: "Verify that the listed roles match the current LogicGate record and update any stale references.",
  },
];

// ── Context-aware trigger rules ─────────────────────────────────
// Each rule describes a condition that, when true, generates an
// additional finding on top of the baseline checklist.  Rules are
// evaluated by the QC engine at runtime.
//
// condition keys reference state fields the engine can read:
//   refreshType   — "no-change" | "updated" | "material"
//   changeSummary — owner free-text
//   uploads       — { clean, redline, "change-summary", "legal-evidence" }
//   checkboxes    — { needsLegal, needsRelatedDocs, needsRetention }

const QC_CONTEXT_RULES = [
  // ── Refresh-type signals ──────────────────────────────────────
  {
    id: "material_no_legal",
    condition: ctx => ctx.refreshType === "material" && !ctx.checkboxes.needsLegal,
    severity: "must",
    title: "Material change flagged but Legal review not indicated",
    body: "You selected 'Potential material change' but did not check 'Legal review may be needed'. Material changes typically require documented legal review per the Compliance Document Approval Matrix.",
    appendix: "A",
    suggestedFix: "Confirm whether Legal review is needed. If it is, check the Legal review box and attach supporting evidence before submission.",
  },
  {
    id: "material_no_evidence",
    condition: ctx => ctx.refreshType === "material" && !ctx.uploads["legal-evidence"],
    severity: "reco",
    title: "Consider attaching stakeholder or legal evidence for material change",
    body: "Material changes often require fuller evidence for approval routing. Attaching legal or stakeholder review evidence now will reduce Governance round-trips.",
    appendix: "A",
    suggestedFix: "Upload legal review evidence or stakeholder sign-off documentation in the Supporting Evidence slot.",
  },
  {
    id: "no_change_but_redline",
    condition: ctx => ctx.refreshType === "no-change" && ctx.uploads.redline,
    severity: "reco",
    title: "Redline detected but refresh type is 'No substantive changes'",
    body: "You selected 'No substantive changes' but attached a verified Google Doc link, which may contain tracked edits. Confirm the refresh type is accurate.",
    appendix: "A",
    suggestedFix: "Review the Google Doc for tracked changes. If edits exist, update the refresh type to 'Updated content' or 'Potential material change'.",
  },

  // ── Change-summary quality signals ────────────────────────────
  {
    id: "summary_too_brief",
    condition: ctx => ctx.changeSummary.trim().length > 0 && ctx.changeSummary.trim().length < 40,
    severity: "reco",
    title: "Change summary appears brief",
    body: "The change summary is under 40 characters. A more detailed summary helps Governance understand the scope of changes without opening the full document.",
    appendix: "A",
    suggestedFix: "Expand the change summary to describe which sections changed, why, and whether the changes affect scope, retention, or related documents.",
  },
  {
    id: "summary_mentions_retention",
    condition: ctx => /retention/i.test(ctx.changeSummary) && !ctx.checkboxes.needsRetention,
    severity: "reco",
    title: "Change summary mentions retention but checkbox not selected",
    body: "Your change summary references retention language, but you did not check 'Retention language may need updates'. Consider selecting it so quincy flags this for closer review.",
    appendix: "A",
    suggestedFix: "Check the 'Retention language may need updates' box to ensure quincy evaluates the retention section more carefully.",
  },
  {
    id: "summary_mentions_related",
    condition: ctx => /related|standard|procedure|linked/i.test(ctx.changeSummary) && !ctx.checkboxes.needsRelatedDocs,
    severity: "reco",
    title: "Change summary references related documents but checkbox not selected",
    body: "Your change summary mentions related documents, standards, or procedures, but you did not check 'Related documents may need updates'.",
    appendix: "A",
    suggestedFix: "Check the 'Related documents may need updates' box so quincy flags the Related Documentation section for review.",
  },

  // ── Upload completeness signals ───────────────────────────────
  {
    id: "no_clean_draft",
    condition: ctx => !ctx.uploads.clean,
    severity: "must",
    title: "Reference clean draft not uploaded",
    body: "A clean draft is required for the submission package. Upload the current approved or proposed clean version.",
    appendix: "A",
    suggestedFix: "Upload the reference clean draft document.",
  },
  {
    id: "no_redline_or_summary",
    condition: ctx => !ctx.uploads.redline && !ctx.uploads["change-summary"],
    severity: "must",
    title: "No verified Google Doc link or change summary attached",
    body: "At least one of these is required: a verified editable Google Doc link or a supporting change summary document.",
    appendix: "A",
    suggestedFix: "Attach the verified Google Doc link from LogicGate, or upload a change summary document.",
  },

  // ── Checkbox-driven signals ───────────────────────────────────
  {
    id: "legal_checked_no_evidence",
    condition: ctx => ctx.checkboxes.needsLegal && !ctx.uploads["legal-evidence"],
    severity: "reco",
    title: "Legal review indicated but no supporting evidence attached",
    body: "You indicated that legal review may be needed. Consider attaching legal review evidence or a confirmation note before submission.",
    appendix: "A",
    suggestedFix: "Upload legal review evidence or a written confirmation from Legal Counsel.",
  },
  {
    id: "retention_checked",
    condition: ctx => ctx.checkboxes.needsRetention,
    severity: "reco",
    title: "Retention language flagged for update — verify draft section",
    body: "You indicated that retention language may need updates. Verify the Record Retention section in the draft is specific enough to satisfy the PoP quality check.",
    appendix: "A",
    suggestedFix: "Review the Record Retention section and confirm it references the Data Classification and Handling Policy or any longer applicable regulatory retention standard.",
  },
  {
    id: "related_docs_checked",
    condition: ctx => ctx.checkboxes.needsRelatedDocs,
    severity: "reco",
    title: "Related documents flagged for update — verify draft section",
    body: "You indicated that related documents may need updates. Verify the Related Documentation section lists all linked Policies, Standards, and Procedures.",
    appendix: "A",
    suggestedFix: "Cross-check the Related Documentation section against the LogicGate record and update any missing references.",
  },
];
