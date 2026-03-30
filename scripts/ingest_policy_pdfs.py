#!/usr/bin/env python3
"""
MVP ingestion script for the policy bot.

What it does:
1. Reads active policy/standard metadata from LOGICGATE_SF.POLICY_BOT.DOCUMENTS
2. Downloads published PDFs from Google Drive using DRIVE_FILE_ID
3. Extracts text page-by-page
4. Splits text into simple chunks
5. Loads chunks into LOGICGATE_SF.POLICY_BOT.DOCUMENT_CHUNKS

Expected environment variables:
- SF_ACCOUNT
- SF_USER
- SF_PASSWORD
- SF_WAREHOUSE
- SF_DATABASE=LOGICGATE_SF
- SF_SCHEMA=POLICY_BOT
- SF_ROLE (optional)
- GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json

Required Python packages:
- snowflake-connector-python
- google-api-python-client
- google-auth
- pdfplumber
"""

from __future__ import annotations

import argparse
import hashlib
import io
import os
import re
import sys
from dataclasses import dataclass
from typing import Iterable

import pdfplumber
import snowflake.connector
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


DRIVE_READONLY_SCOPE = ["https://www.googleapis.com/auth/drive.readonly"]


@dataclass
class DocumentRow:
    document_id: str
    logicgate_record_id: str
    document_title: str
    domain: str | None
    document_type: float | None
    document_type_label: str | None
    document_sub_type: str | None
    document_status: str | None
    approval_date: str | None
    publication_date: str | None
    pdf_url: str | None
    drive_file_id: str


@dataclass
class ChunkRow:
    chunk_id: str
    document_id: str
    logicgate_record_id: str
    document_title: str
    domain: str | None
    document_type: float | None
    document_type_label: str | None
    document_sub_type: str | None
    document_status: str | None
    approval_date: str | None
    publication_date: str | None
    pdf_url: str | None
    page_number: int
    section_heading: str | None
    chunk_index: int
    chunk_text: str
    token_count: int


@dataclass
class SectionBlock:
    page_number: int
    section_heading: str | None
    text: str


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


def get_drive_service():
    credentials_path = require_env("GOOGLE_APPLICATION_CREDENTIALS")
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=DRIVE_READONLY_SCOPE,
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def fetch_documents(conn, limit: int | None, title_filter: str | None) -> list[DocumentRow]:
    sql = """
        select
          DOCUMENT_ID,
          LOGICGATE_RECORD_ID,
          DOCUMENT_TITLE,
          DOMAIN,
          DOCUMENT_TYPE,
          DOCUMENT_TYPE_LABEL,
          DOCUMENT_SUB_TYPE,
          DOCUMENT_STATUS,
          APPROVAL_DATE,
          PUBLICATION_DATE,
          PDF_URL,
          DRIVE_FILE_ID
        from LOGICGATE_SF.POLICY_BOT.DOCUMENTS
        where DRIVE_FILE_ID is not null
    """
    params: list[object] = []

    if title_filter:
        sql += " and DOCUMENT_TITLE ilike %s"
        params.append(f"%{title_filter}%")

    sql += " order by DOCUMENT_TITLE"

    if limit:
        sql += " limit %s"
        params.append(limit)

    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    documents: list[DocumentRow] = []
    for row in rows:
        documents.append(
            DocumentRow(
                document_id=row[0],
                logicgate_record_id=row[1],
                document_title=row[2],
                domain=row[3],
                document_type=row[4],
                document_type_label=row[5],
                document_sub_type=row[6],
                document_status=row[7],
                approval_date=str(row[8]) if row[8] is not None else None,
                publication_date=str(row[9]) if row[9] is not None else None,
                pdf_url=row[10],
                drive_file_id=row[11],
            )
        )
    return documents


def download_drive_file(drive_service, file_id: str) -> bytes:
    request = drive_service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    return buffer.getvalue()


def extract_pages(pdf_bytes: bytes) -> list[tuple[int, list[str]]]:
    pages: list[tuple[int, list[str]]] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = normalize_lines(text)
            if lines:
                pages.append((index, lines))
    return pages


def normalize_lines(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines()]
    return [line for line in lines if line]


def normalize_text(text: str) -> str:
    return "\n".join(normalize_lines(text)).strip()


def is_heading_candidate(line: str) -> bool:
    stripped = line.strip().strip(":")
    if len(stripped) < 3 or len(stripped) > 90:
        return False

    if re.match(r"^\d+(\.\d+)*\s+[A-Z].*", stripped):
        return True

    if re.match(r"^[A-Z][A-Za-z/&,\-\s]{2,}$", stripped):
        words = stripped.split()
        if 1 <= len(words) <= 8 and all(word[:1].isupper() for word in words if word.isalpha()):
            return True

    letters = [char for char in stripped if char.isalpha()]
    if letters:
        upper_ratio = sum(1 for char in letters if char.isupper()) / len(letters)
        if upper_ratio > 0.8 and len(stripped.split()) <= 8:
            return True

    return False


def build_section_blocks(pages: Iterable[tuple[int, list[str]]]) -> list[SectionBlock]:
    blocks: list[SectionBlock] = []
    current_heading: str | None = None

    for page_number, lines in pages:
        buffer: list[str] = []

        for line in lines:
            if is_heading_candidate(line):
                if buffer:
                    blocks.append(
                        SectionBlock(
                            page_number=page_number,
                            section_heading=current_heading,
                            text="\n".join(buffer).strip(),
                        )
                    )
                    buffer = []
                current_heading = line.strip().strip(":")
                continue

            buffer.append(line)

        if buffer:
            blocks.append(
                SectionBlock(
                    page_number=page_number,
                    section_heading=current_heading,
                    text="\n".join(buffer).strip(),
                )
            )

    return [block for block in blocks if block.text]


def chunk_text(text: str, max_chars: int = 3500, overlap_chars: int = 300) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + max_chars, text_length)

        if end < text_length:
            boundary = text.rfind("\n", start, end)
            if boundary == -1:
                boundary = text.rfind(" ", start, end)
            if boundary > start + max_chars // 2:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break
        start = max(0, end - overlap_chars)

    return chunks


def count_tokens(text: str) -> int:
    return len(text.split())


def build_chunk_rows(document: DocumentRow, sections: Iterable[SectionBlock]) -> list[ChunkRow]:
    chunk_rows: list[ChunkRow] = []

    per_page_index: dict[int, int] = {}

    for section in sections:
        page_chunks = chunk_text(section.text)
        for local_index, chunk in enumerate(page_chunks):
            chunk_index = per_page_index.get(section.page_number, 0)
            per_page_index[section.page_number] = chunk_index + 1
            digest = hashlib.md5(
                f"{document.document_id}|{section.page_number}|{chunk_index}|{section.section_heading}|{chunk[:100]}".encode("utf-8")
            ).hexdigest()
            chunk_rows.append(
                ChunkRow(
                    chunk_id=digest,
                    document_id=document.document_id,
                    logicgate_record_id=document.logicgate_record_id,
                    document_title=document.document_title,
                    domain=document.domain,
                    document_type=document.document_type,
                    document_type_label=document.document_type_label,
                    document_sub_type=document.document_sub_type,
                    document_status=document.document_status,
                    approval_date=document.approval_date,
                    publication_date=document.publication_date,
                    pdf_url=document.pdf_url,
                    page_number=section.page_number,
                    section_heading=section.section_heading,
                    chunk_index=chunk_index,
                    chunk_text=chunk,
                    token_count=count_tokens(chunk),
                )
            )

    return chunk_rows


def delete_existing_chunks(conn, document_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            delete from LOGICGATE_SF.POLICY_BOT.DOCUMENT_CHUNKS
            where DOCUMENT_ID = %s
            """,
            (document_id,),
        )


def insert_chunks(conn, chunks: list[ChunkRow]) -> None:
    if not chunks:
        return

    rows = [
        (
            chunk.chunk_id,
            chunk.document_id,
            chunk.logicgate_record_id,
            chunk.document_title,
            chunk.domain,
            chunk.document_type,
            chunk.document_type_label,
            chunk.document_sub_type,
            chunk.document_status,
            chunk.approval_date,
            chunk.publication_date,
            chunk.pdf_url,
            chunk.page_number,
            chunk.section_heading,
            chunk.chunk_index,
            chunk.chunk_text,
            chunk.token_count,
        )
        for chunk in chunks
    ]

    with conn.cursor() as cur:
        cur.executemany(
            """
            insert into LOGICGATE_SF.POLICY_BOT.DOCUMENT_CHUNKS (
              CHUNK_ID,
              DOCUMENT_ID,
              LOGICGATE_RECORD_ID,
              DOCUMENT_TITLE,
              DOMAIN,
              DOCUMENT_TYPE,
              DOCUMENT_TYPE_LABEL,
              DOCUMENT_SUB_TYPE,
              DOCUMENT_STATUS,
              APPROVAL_DATE,
              PUBLICATION_DATE,
              PDF_URL,
              PAGE_NUMBER,
              SECTION_HEADING,
              CHUNK_INDEX,
              CHUNK_TEXT,
              TOKEN_COUNT
            ) values (
              %s, %s, %s, %s, %s, %s, %s, %s, %s,
              %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            rows,
        )


def ingest_documents(limit: int | None, title_filter: str | None, dry_run: bool) -> int:
    conn = get_snowflake_connection()
    drive_service = get_drive_service()

    inserted_chunks = 0
    try:
        documents = fetch_documents(conn, limit=limit, title_filter=title_filter)
        if not documents:
            print("No matching documents found.")
            return 0

        print(f"Found {len(documents)} document(s) to ingest.")

        for index, document in enumerate(documents, start=1):
            print(f"[{index}/{len(documents)}] Downloading: {document.document_title}")

            pdf_bytes = download_drive_file(drive_service, document.drive_file_id)
            pages = extract_pages(pdf_bytes)
            if not pages:
                print(f"  Skipping: no extractable text found for {document.document_title}")
                continue

            sections = build_section_blocks(pages)
            chunks = build_chunk_rows(document, sections)
            print(
                f"  Extracted {len(pages)} page(s), identified {len(sections)} section block(s), built {len(chunks)} chunk(s)."
            )

            if dry_run:
                continue

            delete_existing_chunks(conn, document.document_id)
            insert_chunks(conn, chunks)
            conn.commit()
            inserted_chunks += len(chunks)

        return inserted_chunks
    finally:
        conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest policy PDFs into Snowflake chunk table.")
    parser.add_argument("--limit", type=int, default=None, help="Only ingest the first N documents.")
    parser.add_argument(
        "--title-filter",
        type=str,
        default=None,
        help="Only ingest documents whose title contains this text.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run extraction without writing chunks to Snowflake.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        inserted = ingest_documents(
            limit=args.limit,
            title_filter=args.title_filter,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("Dry run completed.")
    else:
        print(f"Ingestion completed. Inserted {inserted} chunk(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
