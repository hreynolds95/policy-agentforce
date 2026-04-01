# Ruleset Metadata
name: Block Policy on Policies QC
version: 0.1
document_type: Policy
document_source: Google Docs
intended_use: Document owner self-QC before continuing the standard LogicGate and Google Drive lifecycle
default_output_mode: findings_and_enhancements
ruleset_owner: Compliance Governance
ruleset_description: Evaluate a working Google Doc draft against a reusable Policy on Policies QC checklist and suggest practical enhancements for document owners.

## Rule
id: required_sections
title: Required Sections Present
severity: must
enabled: true
check_type: presence
instructions: Confirm the document includes clearly identifiable sections for purpose, scope, document owner, review cadence, and related documents.
evidence_mode: quote_or_missing
enhancement_mode: suggest_language
pass_criteria: All required sections are present and clearly labeled or unmistakably identifiable in the draft.
failure_message: One or more required sections are missing, incomplete, or not clearly identifiable.

## Rule
id: document_purpose_scope_alignment
title: Purpose and Scope Are Distinct and Clear
severity: must
enabled: true
check_type: clarity
instructions: Confirm the document distinguishes purpose from scope and that scope identifies who or what the document applies to.
evidence_mode: quote
enhancement_mode: suggest_language
pass_criteria: Purpose explains why the document exists and scope clearly states the populations, activities, or entities covered.
failure_message: Purpose and scope are missing, blended together, or too vague to support reliable interpretation.

## Rule
id: owner_and_review_cadence
title: Owner and Review Cadence Are Explicit
severity: must
enabled: true
check_type: presence
instructions: Confirm the draft states the accountable document owner and includes an explicit review cadence or annual review expectation.
evidence_mode: quote_or_missing
enhancement_mode: suggest_language
pass_criteria: The owner is named or clearly designated, and the review cadence is explicit.
failure_message: The owner or review cadence is missing, ambiguous, or implied rather than explicit.

## Rule
id: retention_language_specificity
title: Retention Language Is Specific
severity: must
enabled: true
check_type: quality
instructions: Review the retention language and determine whether it is specific enough to be actionable rather than generic.
evidence_mode: quote
enhancement_mode: suggest_language
pass_criteria: Retention language is explicit, operationally meaningful, and not limited to generic statements about keeping records as required.
failure_message: Retention language is missing, vague, or too generic to guide document owners and reviewers.

## Rule
id: related_documents_consistency
title: Related Documents Are Complete and Consistent
severity: recommended
enabled: true
check_type: consistency
instructions: Confirm that related policies, standards, procedures, or guidelines are listed consistently when referenced in the body of the draft.
evidence_mode: quote_or_missing
enhancement_mode: suggest_list
pass_criteria: Related documents are named consistently, and key linked documents are not omitted.
failure_message: Related document references are inconsistent, incomplete, or missing from the draft.

## Rule
id: policy_vs_procedure_language
title: Policy Language Avoids Excessive Procedure Detail
severity: recommended
enabled: true
check_type: quality
instructions: Check whether the draft stays at the policy level rather than embedding step-by-step operational procedure language.
evidence_mode: quote
enhancement_mode: rewrite_section
pass_criteria: The draft states requirements, principles, and responsibilities without turning into a procedural instruction set.
failure_message: The draft includes operational detail that would be better handled in a standard or procedure.

## Rule
id: obligation_language_clarity
title: Requirement Language Is Clear
severity: recommended
enabled: true
check_type: clarity
instructions: Evaluate whether mandatory obligations are expressed clearly with unambiguous requirement language.
evidence_mode: quote
enhancement_mode: suggest_language
pass_criteria: Requirement statements are direct, clear, and consistently framed as obligations where appropriate.
failure_message: Requirement language is weak, inconsistent, or difficult to interpret.

## Rule
id: references_to_external_authority
title: External Authority References Are Anchored
severity: info
enabled: true
check_type: reference
instructions: Identify references to laws, regulations, or external frameworks and note whether they are specific enough to be useful to the owner.
evidence_mode: quote
enhancement_mode: none
pass_criteria: External authority references are specific enough to understand what is driving the policy language.
failure_message: External references are generic or too high level to be useful, but this does not block owner review.
