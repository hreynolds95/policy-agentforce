/**
 * qc-engine.js
 *
 * Dynamic QC engine for quincy.  Evaluates user inputs against the
 * PoP checklist (qc-checklist-config.js) and produces:
 *
 *   1. A checklist status array   — one row per QC_CHECKLIST item
 *   2. A findings array           — actionable cards for the owner
 *
 * The engine is pure functions with no DOM access so it can be
 * tested independently.  The mockup wires it into the UI.
 *
 * Depends on: QC_CHECKLIST, QC_CONTEXT_RULES (from qc-checklist-config.js)
 */

const QCEngine = (() => {
  "use strict";

  // ── Public entry point ──────────────────────────────────────────
  /**
   * Run the full QC evaluation.
   *
   * @param {Object} ctx  Snapshot of current owner inputs:
   *   refreshType    string   "no-change" | "updated" | "material" | ""
   *   changeSummary  string   free-text from the owner
   *   uploads        object   { clean, redline, "change-summary", "legal-evidence" }
   *   checkboxes     object   { needsLegal, needsRelatedDocs, needsRetention }
   *
   * @returns {{ checklist: ChecklistResult[], findings: Finding[] }}
   */
  function evaluate(ctx) {
    const checklist = evaluateChecklist(ctx);
    const findings  = generateFindings(ctx, checklist);
    return { checklist, findings };
  }

  // ── Checklist evaluation ────────────────────────────────────────
  /**
   * Walk every QC_CHECKLIST item and decide pass / fail / skip.
   *
   * Auto-checkable items are evaluated from the context.
   * Non-auto items use heuristics from the context or default to
   * "needs_review" so the owner sees them.
   */
  function evaluateChecklist(ctx) {
    return QC_CHECKLIST.map(item => {
      const result = { ...item, status: "unknown" };

      if (item.autoCheck) {
        result.status = evaluateAutoItem(item, ctx) ? "pass" : "fail";
      } else {
        result.status = evaluateHeuristicItem(item, ctx);
      }
      return result;
    });
  }

  /** Items the engine can evaluate from uploads and metadata alone. */
  function evaluateAutoItem(item, ctx) {
    switch (item.id) {
      case "template":
        // If a clean draft is uploaded we assume the template is correct
        // (real implementation would parse the doc).
        return ctx.uploads.clean;

      case "required_sections":
        // Same heuristic — clean draft present implies sections present.
        return ctx.uploads.clean;

      case "evidence":
        return ctx.uploads.redline || ctx.uploads["change-summary"];

      default:
        return false;
    }
  }

  /**
   * Items that need human judgment but where the engine can still
   * surface a signal from the context.
   *
   * Returns "pass" | "fail" | "needs_review"
   */
  function evaluateHeuristicItem(item, ctx) {
    switch (item.id) {
      case "related_docs":
        // If the owner explicitly flagged related-doc updates, mark fail
        // so the finding appears.  Otherwise needs_review.
        if (ctx.checkboxes.needsRelatedDocs) return "fail";
        // If the summary mentions related docs, surface it
        if (/related|standard|procedure|linked/i.test(ctx.changeSummary)) return "fail";
        return "needs_review";

      case "retention":
        if (ctx.checkboxes.needsRetention) return "fail";
        if (/retention/i.test(ctx.changeSummary)) return "fail";
        return "needs_review";

      case "scope":
        // If the summary mentions scope or entities, flag for review
        if (/scope|entit|business line/i.test(ctx.changeSummary)) return "fail";
        return "needs_review";

      case "glossary":
        if (/glossary|definition|terminology/i.test(ctx.changeSummary)) return "fail";
        return "needs_review";

      case "procedural_wording":
        // Always surface as a recommendation — can't parse the doc yet
        return "needs_review";

      case "plain_language":
        return "needs_review";

      case "roles":
        if (/role|responsibilit|owner|delegate/i.test(ctx.changeSummary)) return "fail";
        return "needs_review";

      default:
        return "needs_review";
    }
  }

  // ── Finding generation ──────────────────────────────────────────
  /**
   * Build the ordered list of findings the owner will see.
   *
   * Sources:
   *   1. Checklist items that failed or need review
   *   2. Context rules whose conditions are true
   *
   * De-duplicated by id so the same issue doesn't appear twice.
   */
  function generateFindings(ctx, checklist) {
    const findings = [];
    const seen = new Set();

    // 1. Findings from checklist failures
    checklist.forEach(item => {
      if (item.status === "fail" && item.suggestedFix) {
        if (seen.has(item.id)) return;
        seen.add(item.id);
        findings.push(makeFinding(item.id, item.severity, titleFromChecklist(item), item.description, item.appendix, item.suggestedFix, item.id));
      }
    });

    // 2. Findings from "needs_review" items that are reco severity
    //    (surface them so the owner can dismiss or accept)
    checklist.forEach(item => {
      if (item.status === "needs_review" && item.severity === "reco" && item.suggestedFix) {
        if (seen.has(item.id)) return;
        seen.add(item.id);
        findings.push(makeFinding(item.id, "reco", titleFromChecklist(item), item.description, item.appendix, item.suggestedFix, item.id));
      }
    });

    // 3. Findings from context rules
    QC_CONTEXT_RULES.forEach(rule => {
      if (seen.has(rule.id)) return;
      try {
        if (rule.condition(ctx)) {
          seen.add(rule.id);
          findings.push(makeFinding(rule.id, rule.severity, rule.title, rule.body, rule.appendix, rule.suggestedFix, null));
        }
      } catch (_) {
        // Defensive — never let a bad rule crash the engine
      }
    });

    // Sort: must-fix first, then reco, alphabetical within group
    findings.sort((a, b) => {
      if (a.kind !== b.kind) return a.kind === "must" ? -1 : 1;
      return a.title.localeCompare(b.title);
    });

    return findings;
  }

  function makeFinding(id, kind, title, body, appendix, suggestedFix, checkTarget) {
    return {
      id,
      kind,           // "must" | "reco"
      title,
      body,
      appendix: appendix || "",
      suggestedFix: suggestedFix || "",
      checkTarget,    // links back to checklist id, or null
      resolved: false,
    };
  }

  function titleFromChecklist(item) {
    // Turn the short checklist label into a finding title
    const map = {
      related_docs:       "Related Documents section is incomplete",
      retention:          "Record Retention section is missing detail",
      scope:              "Scope section may not cover all entities",
      glossary:           "Glossary term may not align with approved definitions",
      procedural_wording: "Procedural wording detected in Policy draft",
      plain_language:     "Consider simplifying into plainer business language",
      roles:              "Roles and responsibilities may need updating",
      template:           "Approved template may not be used",
      required_sections:  "Required sections may be missing",
      evidence:           "Redline or change summary not attached",
    };
    return map[item.id] || item.label;
  }

  // ── Readiness score ─────────────────────────────────────────────
  /**
   * Compute a transparent, weighted readiness score.
   *
   * Returns { score: number 0-100, breakdown: { label: points }[] }
   */
  function computeReadiness(ctx, checklist, findings) {
    const weights = {
      refreshType:       { max: 8,  earned: ctx.refreshType ? 8 : 0,  label: "Refresh type captured" },
      cleanDraft:        { max: 12, earned: ctx.uploads.clean ? 12 : 0, label: "Clean draft uploaded" },
      redlineOrSummary:  { max: 12, earned: (ctx.uploads.redline || ctx.uploads["change-summary"]) ? 12 : 0, label: "Redline or change summary" },
      changeSummary:     { max: 8,  earned: ctx.changeSummary.trim().length >= 20 ? 8 : (ctx.changeSummary.trim().length > 0 ? 4 : 0), label: "Change summary written" },
      qcRun:             { max: 10, earned: 10, label: "QC check completed" },  // always earned when this fn is called
    };

    // Must-fix deductions
    const mustOpen = findings.filter(f => f.kind === "must" && !f.resolved).length;
    const recoOpen = findings.filter(f => f.kind === "reco" && !f.resolved).length;
    weights.mustFixes = { max: 35, earned: Math.max(0, 35 - (mustOpen * 12)), label: "Required fixes resolved" };
    weights.recoItems = { max: 15, earned: Math.max(0, 15 - (recoOpen * 3)),  label: "Recommended items addressed" };

    let total = 0;
    let earned = 0;
    const breakdown = [];

    Object.values(weights).forEach(w => {
      total += w.max;
      earned += w.earned;
      breakdown.push({ label: w.label, max: w.max, earned: w.earned });
    });

    const score = Math.round(Math.max(0, Math.min(100, (earned / total) * 100)));
    return { score, breakdown };
  }

  // ── Checklist summary for the UI ────────────────────────────────
  /**
   * Returns a display-ready array for the checklist panel.
   *
   * Each entry: { label, status: "pass"|"fail"|"needs_review", appendix }
   */
  function getChecklistSummary(checklist) {
    return checklist.map(item => ({
      id:       item.id,
      label:    item.label,
      status:   item.status,
      appendix: item.appendix,
    }));
  }

  // ── Public API ──────────────────────────────────────────────────
  return {
    evaluate,
    computeReadiness,
    getChecklistSummary,
  };
})();
