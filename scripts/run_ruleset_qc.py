#!/usr/bin/env python3
"""
Ruleset-driven QC runner for Google Docs drafts.

Inputs:
- Google Doc URL
- markdown ruleset file
- LLM provider and model

Outputs:
- normalized JSON result
- optional markdown report

Environment variables:
- GOOGLE_APPLICATION_CREDENTIALS
- LLM_PROVIDER (optional: auto, anthropic, openai)
- ANTHROPIC_API_KEY (optional)
- OPENAI_API_KEY (optional)
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build


DOCS_SCOPE = ["https://www.googleapis.com/auth/documents.readonly"]
DEFAULT_MODEL = "claude-3-5-sonnet-latest"
MAX_DOCUMENT_CHARS = 24000


@dataclass
class RulesetMetadata:
    name: str
    version: str
    document_type: str
    document_source: str
    intended_use: str
    default_output_mode: str
    extra: dict[str, str]


@dataclass
class Rule:
    id: str
    title: str
    severity: str
    enabled: bool
    check_type: str
    instructions: str
    evidence_mode: str
    enhancement_mode: str
    pass_criteria: str
    failure_message: str
    extra: dict[str, str]


@dataclass
class GoogleDoc:
    document_id: str
    document_title: str
    google_doc_url: str
    document_text: str
    outline: list[str]


REQUIRED_METADATA_FIELDS = {
    "name",
    "version",
    "document_type",
    "document_source",
    "intended_use",
    "default_output_mode",
}

REQUIRED_RULE_FIELDS = {
    "id",
    "title",
    "severity",
    "enabled",
    "check_type",
    "instructions",
    "evidence_mode",
    "enhancement_mode",
    "pass_criteria",
    "failure_message",
}


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def extract_google_doc_id(url: str) -> str:
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise RuntimeError("Could not extract a Google Doc ID from the provided URL.")
    return match.group(1)


def get_docs_service():
    credentials_path = require_env("GOOGLE_APPLICATION_CREDENTIALS")
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=DOCS_SCOPE,
    )
    return build("docs", "v1", credentials=credentials, cache_discovery=False)


def read_google_doc(url: str) -> GoogleDoc:
    document_id = extract_google_doc_id(url)
    service = get_docs_service()
    document = service.documents().get(documentId=document_id).execute()

    title = document.get("title", "Untitled Google Doc")
    lines: list[str] = []
    outline: list[str] = []

    for element in document.get("body", {}).get("content", []):
        paragraph = element.get("paragraph")
        if not paragraph:
            continue

        text_runs: list[str] = []
        for paragraph_element in paragraph.get("elements", []):
            text_run = paragraph_element.get("textRun")
            if text_run:
                text_runs.append(text_run.get("content", ""))

        text = "".join(text_runs).strip()
        if not text:
            continue

        named_style = paragraph.get("paragraphStyle", {}).get("namedStyleType", "")
        if named_style.startswith("HEADING"):
            outline.append(text)
            lines.append(f"\n{text}\n")
        else:
            lines.append(text)

    document_text = "\n".join(lines).strip()
    if not document_text:
        raise RuntimeError("The Google Doc did not produce any readable text.")

    return GoogleDoc(
        document_id=document_id,
        document_title=title,
        google_doc_url=url,
        document_text=document_text,
        outline=outline,
    )


def parse_key_value_line(line: str) -> tuple[str, str] | None:
    if ":" not in line:
        return None
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def parse_ruleset_markdown(path: Path) -> tuple[RulesetMetadata, list[Rule]]:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    metadata_map: dict[str, str] = {}
    rules: list[dict[str, str]] = []
    current_rule: dict[str, str] | None = None
    in_metadata = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if line == "# Ruleset Metadata":
            in_metadata = True
            current_rule = None
            continue

        if line == "## Rule":
            in_metadata = False
            if current_rule:
                rules.append(current_rule)
            current_rule = {}
            continue

        parsed = parse_key_value_line(line)
        if not parsed:
            continue

        key, value = parsed
        if in_metadata:
            metadata_map[key] = value
        elif current_rule is not None:
            current_rule[key] = value

    if current_rule:
        rules.append(current_rule)

    missing_metadata = REQUIRED_METADATA_FIELDS - metadata_map.keys()
    if missing_metadata:
        raise RuntimeError(f"Ruleset metadata is missing required fields: {', '.join(sorted(missing_metadata))}")

    parsed_rules: list[Rule] = []
    for index, rule_map in enumerate(rules, start=1):
        missing_fields = REQUIRED_RULE_FIELDS - rule_map.keys()
        if missing_fields:
            raise RuntimeError(
                f"Rule #{index} is missing required fields: {', '.join(sorted(missing_fields))}"
            )

        parsed_rules.append(
            Rule(
                id=rule_map["id"],
                title=rule_map["title"],
                severity=rule_map["severity"],
                enabled=rule_map["enabled"].lower() == "true",
                check_type=rule_map["check_type"],
                instructions=rule_map["instructions"],
                evidence_mode=rule_map["evidence_mode"],
                enhancement_mode=rule_map["enhancement_mode"],
                pass_criteria=rule_map["pass_criteria"],
                failure_message=rule_map["failure_message"],
                extra={key: value for key, value in rule_map.items() if key not in REQUIRED_RULE_FIELDS},
            )
        )

    metadata = RulesetMetadata(
        name=metadata_map["name"],
        version=metadata_map["version"],
        document_type=metadata_map["document_type"],
        document_source=metadata_map["document_source"],
        intended_use=metadata_map["intended_use"],
        default_output_mode=metadata_map["default_output_mode"],
        extra={key: value for key, value in metadata_map.items() if key not in REQUIRED_METADATA_FIELDS},
    )
    return metadata, parsed_rules


def get_llm_provider(requested_provider: str | None = None) -> str:
    provider = (requested_provider or os.getenv("LLM_PROVIDER") or "auto").strip().lower()
    if provider == "auto":
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        raise RuntimeError("No LLM key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")
    if provider not in {"anthropic", "openai"}:
        raise RuntimeError("Unsupported provider. Use anthropic, openai, or auto.")
    return provider


def build_rule_prompt(document: GoogleDoc, metadata: RulesetMetadata, rule: Rule) -> tuple[str, str]:
    document_excerpt = document.document_text[:MAX_DOCUMENT_CHARS]
    outline_text = "\n".join(f"- {heading}" for heading in document.outline[:30]) or "- No headings detected"

    system_prompt = (
        "You are a document QC assistant for document owners.\n"
        "Review the provided Google Doc draft against one rule only.\n"
        "Use only the provided draft text and document outline.\n"
        "Return valid JSON only.\n"
        "The JSON must include the keys: status, finding, evidence, suggested_enhancement, suggested_language.\n"
        "Allowed status values: pass, fail.\n"
        "When the rule passes, suggested_enhancement and suggested_language must be null.\n"
        "When the rule fails, keep evidence concise and quote the draft when possible.\n"
    )

    user_prompt = (
        f"Ruleset: {metadata.name} v{metadata.version}\n"
        f"Document title: {document.document_title}\n"
        f"Document type: {metadata.document_type}\n"
        f"Google Doc URL: {document.google_doc_url}\n\n"
        f"Rule ID: {rule.id}\n"
        f"Rule title: {rule.title}\n"
        f"Severity: {rule.severity}\n"
        f"Check type: {rule.check_type}\n"
        f"Instructions: {rule.instructions}\n"
        f"Evidence mode: {rule.evidence_mode}\n"
        f"Enhancement mode: {rule.enhancement_mode}\n"
        f"Pass criteria: {rule.pass_criteria}\n"
        f"Failure message: {rule.failure_message}\n\n"
        f"Document outline:\n{outline_text}\n\n"
        f"Document text:\n{document_excerpt}\n"
    )
    return system_prompt, user_prompt


def extract_json(text: str) -> dict:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return json.loads(stripped)

    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if not match:
        raise RuntimeError("LLM response did not contain a JSON object.")
    return json.loads(match.group(0))


def run_rule_with_anthropic(system_prompt: str, user_prompt: str, model: str) -> dict:
    api_key = require_env("ANTHROPIC_API_KEY")
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise RuntimeError("The anthropic package is required for Anthropic runs.") from exc

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=900,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text_parts: list[str] = []
    for block in getattr(response, "content", []):
        if getattr(block, "type", None) == "text":
            text_parts.append(getattr(block, "text", ""))

    return extract_json("".join(text_parts))


def run_rule_with_openai(system_prompt: str, user_prompt: str, model: str) -> dict:
    api_key = require_env("OPENAI_API_KEY")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The openai package is required for OpenAI runs.") from exc

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    text = getattr(response, "output_text", None)
    if not text:
        raise RuntimeError("OpenAI response did not include output_text.")
    return extract_json(text)


def run_rule(rule: Rule, document: GoogleDoc, metadata: RulesetMetadata, provider: str, model: str) -> dict:
    system_prompt, user_prompt = build_rule_prompt(document, metadata, rule)
    if provider == "anthropic":
        result = run_rule_with_anthropic(system_prompt, user_prompt, model)
    else:
        result = run_rule_with_openai(system_prompt, user_prompt, model)

    status = str(result.get("status", "fail")).lower()
    if status not in {"pass", "fail"}:
        status = "fail"

    return {
        "rule_id": rule.id,
        "title": rule.title,
        "severity": rule.severity,
        "status": status,
        "finding": result.get("finding") or (rule.failure_message if status == "fail" else f"{rule.title} passed."),
        "evidence": result.get("evidence") or "No evidence returned.",
        "suggested_enhancement": result.get("suggested_enhancement"),
        "suggested_language": result.get("suggested_language"),
    }


def summarize_results(findings: list[dict]) -> dict:
    must_fix_count = sum(1 for finding in findings if finding["severity"] == "must" and finding["status"] == "fail")
    recommended_count = sum(1 for finding in findings if finding["severity"] == "recommended" and finding["status"] == "fail")
    info_count = sum(1 for finding in findings if finding["severity"] == "info")

    if must_fix_count:
        overall_readiness = "needs_revision"
    elif recommended_count:
        overall_readiness = "needs_cleanup"
    else:
        overall_readiness = "ready"

    return {
        "must_fix_count": must_fix_count,
        "recommended_count": recommended_count,
        "info_count": info_count,
        "overall_readiness": overall_readiness,
    }


def build_audit_trail(findings: list[dict]) -> dict:
    return {
        "rules_evaluated": len(findings),
        "rules_passed": [finding["rule_id"] for finding in findings if finding["status"] == "pass"],
        "rules_failed": [finding["rule_id"] for finding in findings if finding["status"] == "fail"],
    }


def build_result_payload(document: GoogleDoc, metadata: RulesetMetadata, findings: list[dict], provider: str, model: str) -> dict:
    return {
        "document_metadata": {
            "source": "google_doc",
            "google_doc_url": document.google_doc_url,
            "document_id": document.document_id,
            "document_title": document.document_title,
            "document_type": metadata.document_type,
        },
        "ruleset_metadata": {
            "name": metadata.name,
            "version": metadata.version,
            "document_type": metadata.document_type,
        },
        "run_metadata": {
            "provider": provider,
            "model": model,
            "run_timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
            "output_mode": metadata.default_output_mode,
        },
        "summary": summarize_results(findings),
        "findings": findings,
        "audit_trail": build_audit_trail(findings),
    }


def build_markdown_report(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        f"# QC Report: {payload['document_metadata']['document_title']}",
        "",
        f"- Google Doc: {payload['document_metadata']['google_doc_url']}",
        f"- Ruleset: {payload['ruleset_metadata']['name']} v{payload['ruleset_metadata']['version']}",
        f"- Provider: {payload['run_metadata']['provider']}",
        f"- Model: {payload['run_metadata']['model']}",
        f"- Run timestamp: {payload['run_metadata']['run_timestamp']}",
        "",
        "## Summary",
        f"- Must fix: {summary['must_fix_count']}",
        f"- Recommended: {summary['recommended_count']}",
        f"- Info: {summary['info_count']}",
        f"- Overall readiness: {summary['overall_readiness']}",
        "",
        "## Findings",
    ]

    for finding in payload["findings"]:
        lines.extend(
            [
                f"### {finding['title']}",
                f"- Rule ID: {finding['rule_id']}",
                f"- Severity: {finding['severity']}",
                f"- Status: {finding['status']}",
                f"- Finding: {finding['finding']}",
                f"- Evidence: {finding['evidence']}",
                f"- Suggested enhancement: {finding['suggested_enhancement'] or 'None'}",
                f"- Suggested language: {finding['suggested_language'] or 'None'}",
                "",
            ]
        )

    return "\n".join(lines).strip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a markdown QC ruleset against a Google Docs draft.")
    parser.add_argument("--google-doc-url", required=True, help="Google Doc edit URL for the working draft.")
    parser.add_argument("--ruleset", required=True, help="Path to the markdown ruleset file.")
    parser.add_argument("--provider", choices=["auto", "anthropic", "openai"], default="auto")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--dry-run", action="store_true", help="Parse the ruleset and Google Doc but skip LLM evaluation.")
    parser.add_argument("--output", help="Optional path for JSON output.")
    parser.add_argument("--report-output", help="Optional path for markdown report output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ruleset_path = Path(args.ruleset).expanduser().resolve()
    metadata, rules = parse_ruleset_markdown(ruleset_path)
    document = read_google_doc(args.google_doc_url)

    if args.dry_run:
        payload = {
            "document_metadata": asdict(document),
            "ruleset_metadata": asdict(metadata),
            "rules": [asdict(rule) for rule in rules if rule.enabled],
        }
    else:
        provider = get_llm_provider(args.provider)
        findings = [
            run_rule(rule, document, metadata, provider=provider, model=args.model)
            for rule in rules
            if rule.enabled
        ]
        payload = build_result_payload(document, metadata, findings, provider=provider, model=args.model)

        if args.report_output:
            Path(args.report_output).write_text(build_markdown_report(payload), encoding="utf-8")

    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
