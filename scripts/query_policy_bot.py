#!/usr/bin/env python3
"""
MVP retrieval/chat script for the policy bot.

What it does:
1. Reads chunked policy content from LOGICGATE_SF.POLICY_BOT.DOCUMENT_CHUNKS
2. Runs keyword-based retrieval against active policy and standard text
3. Optionally synthesizes an answer with an LLM using only the top retrieved excerpts
4. Falls back to a concise extractive answer when no LLM is configured
4. Prints citations with PDF and LogicGate references
5. Logs the interaction to LOGICGATE_SF.POLICY_BOT.CHAT_LOGS

Expected environment variables:
- SF_ACCOUNT
- SF_USER
- SF_PASSWORD
- SF_WAREHOUSE
- SF_DATABASE=LOGICGATE_SF
- SF_SCHEMA=POLICY_BOT
- SF_ROLE (optional)
- OPENAI_API_KEY (optional, for OpenAI synthesis)
- ANTHROPIC_API_KEY (optional, for Anthropic synthesis)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from dataclasses import asdict, dataclass
from typing import Iterable

import snowflake.connector


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "do",
    "does",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


@dataclass
class MatchRow:
    chunk_id: str
    document_id: str
    logicgate_record_id: str
    document_title: str
    domain: str | None
    document_type_label: str | None
    document_status: str | None
    approval_date: str | None
    publication_date: str | None
    pdf_url: str | None
    page_number: int | None
    section_heading: str | None
    chunk_index: int
    chunk_text: str
    score: int


def require_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_snowflake_connection():
    conn_kwargs = {
        "account": require_env("SF_ACCOUNT"),
        "user": require_env("SF_USER"),
        "password": require_env("SF_PASSWORD"),
        "warehouse": require_env("SF_WAREHOUSE"),
        "database": require_env("SF_DATABASE", "LOGICGATE_SF"),
        "schema": require_env("SF_SCHEMA", "POLICY_BOT"),
    }
    role = os.getenv("SF_ROLE")
    if role:
        conn_kwargs["role"] = role
    return snowflake.connector.connect(**conn_kwargs)


def tokenize_question(question: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9']+", question.lower())
    seen: set[str] = set()
    cleaned: list[str] = []

    for token in tokens:
        if len(token) < 3 or token in STOPWORDS:
            continue
        if token.endswith("'s"):
            token = token[:-2]
        if token not in seen:
            seen.add(token)
            cleaned.append(token)
    return cleaned[:12]


def build_search_sql(tokens: list[str], candidate_limit: int, document_type: str | None, domain: str | None) -> tuple[str, list[object]]:
    if not tokens:
        raise RuntimeError("Question did not contain enough searchable keywords.")

    where_parts: list[str] = []
    params: list[object] = []

    for token in tokens:
        like = f"%{token}%"

        where_parts.append(
            "(lower(DOCUMENT_TITLE) like %s or lower(coalesce(SECTION_HEADING, '')) like %s or lower(CHUNK_TEXT) like %s)"
        )
        params.extend([like, like, like])

    sql = f"""
        select
          CHUNK_ID,
          DOCUMENT_ID,
          LOGICGATE_RECORD_ID,
          DOCUMENT_TITLE,
          DOMAIN,
          DOCUMENT_TYPE_LABEL,
          DOCUMENT_STATUS,
          APPROVAL_DATE,
          PUBLICATION_DATE,
          PDF_URL,
          PAGE_NUMBER,
          SECTION_HEADING,
          CHUNK_INDEX,
          CHUNK_TEXT
        from LOGICGATE_SF.POLICY_BOT.DOCUMENT_CHUNKS
        where ({' or '.join(where_parts)})
    """

    if document_type:
        sql += " and DOCUMENT_TYPE_LABEL = %s"
        params.append(document_type)

    if domain:
        sql += " and DOMAIN = %s"
        params.append(domain)

    sql += " order by DOCUMENT_TITLE asc, PAGE_NUMBER asc limit %s"
    params.append(candidate_limit)
    return sql, params


def run_search(conn, question: str, top_k: int, document_type: str | None, domain: str | None) -> tuple[list[str], list[MatchRow]]:
    tokens = tokenize_question(question)
    candidate_limit = max(top_k * 8, 25)
    sql, params = build_search_sql(
        tokens,
        candidate_limit=candidate_limit,
        document_type=document_type,
        domain=domain,
    )

    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    candidates: list[MatchRow] = []
    for row in rows:
        candidates.append(
            MatchRow(
                chunk_id=row[0],
                document_id=row[1],
                logicgate_record_id=row[2],
                document_title=row[3],
                domain=row[4],
                document_type_label=row[5],
                document_status=row[6],
                approval_date=str(row[7]) if row[7] is not None else None,
                publication_date=str(row[8]) if row[8] is not None else None,
                pdf_url=row[9],
                page_number=row[10],
                section_heading=row[11],
                chunk_index=row[12],
                chunk_text=row[13],
                score=0,
            )
        )

    reranked = rerank_matches(question, tokens, candidates)
    return tokens, reranked[:top_k]


def rerank_matches(question: str, tokens: list[str], matches: Iterable[MatchRow]) -> list[MatchRow]:
    phrase = " ".join(tokens).strip().lower()
    reranked: list[MatchRow] = []

    for match in matches:
        title = (match.document_title or "").lower()
        heading = (match.section_heading or "").lower()
        text = (match.chunk_text or "").lower()

        score = 0
        matched_tokens = 0

        if phrase and phrase in title:
            score += 24
        if phrase and phrase in heading:
            score += 18
        if phrase and phrase in text:
            score += 12

        for token in tokens:
            title_hits = title.count(token)
            heading_hits = heading.count(token)
            text_hits = text.count(token)

            if title_hits or heading_hits or text_hits:
                matched_tokens += 1

            score += min(title_hits, 2) * 8
            score += min(heading_hits, 2) * 6
            score += min(text_hits, 5) * 2

        if tokens:
            coverage = matched_tokens / len(tokens)
            score += int(coverage * 20)
            if matched_tokens == len(tokens):
                score += 10

        if match.document_type_label == "Policy":
            score += 1

        reranked.append(
            MatchRow(
                chunk_id=match.chunk_id,
                document_id=match.document_id,
                logicgate_record_id=match.logicgate_record_id,
                document_title=match.document_title,
                domain=match.domain,
                document_type_label=match.document_type_label,
                document_status=match.document_status,
                approval_date=match.approval_date,
                publication_date=match.publication_date,
                pdf_url=match.pdf_url,
                page_number=match.page_number,
                section_heading=match.section_heading,
                chunk_index=match.chunk_index,
                chunk_text=match.chunk_text,
                score=score,
            )
        )

    reranked.sort(
        key=lambda match: (
            match.score,
            1 if match.section_heading else 0,
            -(match.page_number or 9999),
        ),
        reverse=True,
    )
    return reranked


def build_answer(question: str, matches: list[MatchRow]) -> tuple[str, str]:
    if not matches:
        return (
            "I couldn’t find supporting text in the active policy and standard corpus for that question.",
            "low",
        )

    top = matches[0]
    summary = summarize_chunk(top.chunk_text)

    same_doc_matches = [m for m in matches if m.document_id == top.document_id]
    confidence = "high" if top.score >= 12 else "medium"

    if len(same_doc_matches) > 1:
        answer = (
            f"The strongest match is the active {safe_label(top.document_type_label)} "
            f'"{top.document_title}". Based on the retrieved text, {summary}'
        )
    else:
        answer = (
            f'The best-supported match is "{top.document_title}". '
            f"Based on the retrieved excerpt, {summary}"
        )

    if len(matches) > 1:
        secondary_titles = unique_titles(matches[1:4])
        if secondary_titles:
            answer += " Related supporting documents also surfaced: " + ", ".join(secondary_titles) + "."

    return answer, confidence


def build_context(matches: list[MatchRow], max_matches: int = 5) -> str:
    context_parts: list[str] = []
    for index, match in enumerate(matches[:max_matches], start=1):
        context_parts.append(
            "\n".join(
                [
                    f"[{index}] document_title: {match.document_title}",
                    f"[{index}] document_type: {match.document_type_label or 'Unknown'}",
                    f"[{index}] domain: {match.domain or 'Unknown'}",
                    f"[{index}] logicgate_record_id: {match.logicgate_record_id or 'Unknown'}",
                    f"[{index}] publication_date: {match.publication_date or 'Unknown'}",
                    f"[{index}] page_number: {match.page_number if match.page_number is not None else 'Unknown'}",
                    f"[{index}] section_heading: {match.section_heading or 'Unknown'}",
                    f"[{index}] excerpt:",
                    match.chunk_text,
                ]
            )
        )
    return "\n\n".join(context_parts)


def get_llm_provider(requested_provider: str | None = None) -> str:
    provider = (requested_provider or os.getenv("LLM_PROVIDER") or "auto").strip().lower()
    if provider == "auto":
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        raise RuntimeError(
            "No LLM provider key was found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY when --use-llm is enabled."
        )
    if provider not in {"anthropic", "openai"}:
        raise RuntimeError("Unsupported LLM provider. Use 'anthropic', 'openai', or 'auto'.")
    return provider


def build_prompts(question: str, context: str) -> tuple[str, str]:
    system_prompt = (
        "You are a compliance policy assistant for Block employees.\n"
        "Answer only from the retrieved policy excerpts provided.\n"
        "Do not use outside knowledge.\n"
        "If the excerpts do not clearly support an answer, say so.\n"
        "Cite each substantive claim inline using bracketed citations like [1] or [2].\n"
        "Prefer a concise answer, then a short bullet list when helpful.\n"
    )

    user_prompt = (
        f"Question:\n{question}\n\n"
        f"Retrieved excerpts:\n{context}\n\n"
        "Write a concise answer using only the retrieved excerpts. "
        "If multiple documents apply, distinguish them clearly."
    )
    return system_prompt, user_prompt


def generate_openai_answer(question: str, matches: list[MatchRow], model: str) -> tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required when the OpenAI provider is selected.")

    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("The openai package is required for OpenAI synthesis. Install it with `pip install openai`.") from exc

    if not matches:
        return (
            "I couldn’t find supporting text in the active policy and standard corpus for that question.",
            "low",
        )

    client = OpenAI(api_key=api_key)
    context = build_context(matches)
    system_prompt, user_prompt = build_prompts(question, context)

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    answer = getattr(response, "output_text", None)
    if not answer:
        raise RuntimeError("The LLM response did not include output_text.")

    top_score = matches[0].score if matches else 0
    confidence = "high" if top_score >= 16 else "medium"
    return answer.strip(), confidence


def generate_anthropic_answer(question: str, matches: list[MatchRow], model: str) -> tuple[str, str]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is required when the Anthropic provider is selected.")

    try:
        from anthropic import Anthropic
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("The anthropic package is required for Anthropic synthesis. Install it with `pip install anthropic`.") from exc

    if not matches:
        return (
            "I couldn’t find supporting text in the active policy and standard corpus for that question.",
            "low",
        )

    client = Anthropic(api_key=api_key)
    context = build_context(matches)
    system_prompt, user_prompt = build_prompts(question, context)

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

    answer = "".join(text_parts).strip()
    if not answer:
        raise RuntimeError("The Anthropic response did not include text content.")

    top_score = matches[0].score if matches else 0
    confidence = "high" if top_score >= 16 else "medium"
    return answer, confidence


def generate_llm_answer(question: str, matches: list[MatchRow], model: str, provider: str | None = None) -> tuple[str, str]:
    resolved_provider = get_llm_provider(provider)
    if resolved_provider == "anthropic":
        return generate_anthropic_answer(question, matches, model=model)
    return generate_openai_answer(question, matches, model=model)


def safe_label(document_type_label: str | None) -> str:
    return (document_type_label or "document").lower()


def unique_titles(matches: list[MatchRow]) -> list[str]:
    titles: list[str] = []
    seen: set[str] = set()
    for match in matches:
        if match.document_title not in seen:
            seen.add(match.document_title)
            titles.append(match.document_title)
    return titles


def summarize_chunk(text: str, max_chars: int = 320) -> str:
    normalized = " ".join(text.split())
    sentences = re.split(r"(?<=[.!?])\s+", normalized)
    if not sentences:
        return normalized[:max_chars]

    chosen: list[str] = []
    current_len = 0
    for sentence in sentences:
        if not sentence:
            continue
        if current_len + len(sentence) > max_chars and chosen:
            break
        chosen.append(sentence)
        current_len += len(sentence) + 1
        if len(chosen) >= 2:
            break

    summary = " ".join(chosen).strip()
    if len(summary) > max_chars:
        summary = summary[: max_chars - 1].rstrip() + "…"
    return summary


def print_result(question: str, answer: str, confidence: str, matches: list[MatchRow]) -> None:
    print()
    print("Question")
    print(question)
    print()
    print("Answer")
    print(answer)
    print()
    print(f"Confidence: {confidence}")
    print()
    print("Citations")

    if not matches:
        print("- No supporting excerpts found.")
        return

    for index, match in enumerate(matches[:5], start=1):
        location_parts = []
        if match.section_heading:
            location_parts.append(f"section: {match.section_heading}")
        if match.page_number is not None:
            location_parts.append(f"page: {match.page_number}")
        location_text = ", ".join(location_parts) if location_parts else "location unavailable"

        print(f"{index}. {match.document_title}")
        print(f"   type: {match.document_type_label or 'Unknown'}")
        print(f"   domain: {match.domain or 'Unknown'}")
        print(f"   {location_text}")
        print(f"   publication date: {match.publication_date or 'Unknown'}")
        print(f"   LogicGate record ID: {match.logicgate_record_id or 'Unknown'}")
        print(f"   PDF: {match.pdf_url or 'Unavailable'}")
        print(f"   excerpt: {summarize_chunk(match.chunk_text, max_chars=220)}")
        print()


def log_chat(conn, chat_id: str, user_id: str, question: str, filters: dict, matches: list[MatchRow], answer: str, confidence: str) -> None:
    retrieved = [
        {
            "chunk_id": match.chunk_id,
            "document_id": match.document_id,
            "document_title": match.document_title,
            "page_number": match.page_number,
            "section_heading": match.section_heading,
            "score": match.score,
        }
        for match in matches[:10]
    ]

    with conn.cursor() as cur:
        cur.execute(
            """
            insert into LOGICGATE_SF.POLICY_BOT.CHAT_LOGS (
              CHAT_ID,
              ASKED_AT,
              USER_ID,
              QUESTION,
              APPLIED_FILTERS,
              RETRIEVED_CHUNKS,
              ANSWER_TEXT,
              CONFIDENCE_LABEL,
              FEEDBACK
            )
            select
              %s,
              current_timestamp(),
              %s,
              %s,
              parse_json(%s),
              parse_json(%s),
              %s,
              %s,
              null
            """,
            (
                chat_id,
                user_id,
                question,
                json.dumps(filters),
                json.dumps(retrieved),
                answer,
                confidence,
            ),
        )
    conn.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query policy chunks and return a cited answer.")
    parser.add_argument("question", type=str, help="The user question to ask.")
    parser.add_argument("--document-type", choices=["Policy", "Standard"], default=None)
    parser.add_argument("--domain", type=str, default=None)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--user-id", type=str, default=os.getenv("USER", "local-user"))
    parser.add_argument("--use-llm", action="store_true", help="Use an LLM to synthesize the answer from retrieved excerpts.")
    parser.add_argument("--provider", choices=["auto", "anthropic", "openai"], default="auto", help="LLM provider to use with --use-llm.")
    parser.add_argument("--model", type=str, default="claude-3-5-sonnet-latest", help="LLM model to use with --use-llm.")
    parser.add_argument("--json", action="store_true", help="Print JSON output instead of plain text.")
    parser.add_argument("--no-log", action="store_true", help="Skip writing to CHAT_LOGS.")
    return parser.parse_args()


def print_json(question: str, answer: str, confidence: str, matches: list[MatchRow]) -> None:
    payload = {
        "question": question,
        "answer": answer,
        "confidence": confidence,
        "citations": [asdict(match) for match in matches[:5]],
    }
    print(json.dumps(payload, indent=2))


def run_query(
    conn,
    question: str,
    document_type: str | None = None,
    domain: str | None = None,
    top_k: int = 5,
    use_llm: bool = False,
    provider: str = "auto",
    model: str = "claude-3-5-sonnet-latest",
    user_id: str = "local-user",
    no_log: bool = False,
) -> dict:
    tokens, matches = run_search(
        conn,
        question=question,
        top_k=top_k,
        document_type=document_type,
        domain=domain,
    )

    if use_llm:
        resolved_provider = get_llm_provider(provider)
        answer, confidence = generate_llm_answer(question, matches, model=model, provider=resolved_provider)
    else:
        answer, confidence = build_answer(question, matches)
        resolved_provider = None

    payload = {
        "question": question,
        "answer": answer,
        "confidence": confidence,
        "citations": [asdict(match) for match in matches[:5]],
        "applied_filters": {
            "document_type": document_type,
            "domain": domain,
            "top_k": top_k,
            "tokens": tokens,
            "use_llm": use_llm,
            "provider": resolved_provider if use_llm else None,
            "model": model if use_llm else None,
        },
    }

    if not no_log:
        log_chat(
            conn,
            chat_id=str(uuid.uuid4()),
            user_id=user_id,
            question=question,
            filters=payload["applied_filters"],
            matches=matches,
            answer=answer,
            confidence=confidence,
        )

    return payload


def main() -> int:
    args = parse_args()
    conn = get_snowflake_connection()

    try:
        payload = run_query(
            conn=conn,
            question=args.question,
            document_type=args.document_type,
            domain=args.domain,
            top_k=args.top_k,
            use_llm=args.use_llm,
            provider=args.provider,
            model=args.model,
            user_id=args.user_id,
            no_log=args.no_log,
        )

        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            matches = [MatchRow(**match) for match in payload["citations"]]
            print_result(payload["question"], payload["answer"], payload["confidence"], matches)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
