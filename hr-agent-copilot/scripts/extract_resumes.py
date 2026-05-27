#!/usr/bin/env python3
"""Extract text from resume PDFs for portable HR screening workflows.

This script intentionally performs deterministic extraction only. It does not
score candidates or make hiring judgments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: pypdf. Install it with: pip install pypdf"
    ) from exc


@dataclass
class ResumeExtract:
    source_path: str
    output_text_path: str
    file_name: str
    candidate_hint: str
    page_count: int
    char_count: int
    extracted_at: str
    warnings: list[str]


def sanitize_filename(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "_", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or "resume"


def candidate_hint_from_filename(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"(?i)\b(java|backend|resume|cv|简历|求职|开发|工程师)\b", " ", stem)
    stem = re.sub(r"\b\d+\s*年\b", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip(" -_")
    return stem or path.stem


def iter_pdf_files(inputs: Iterable[Path], recursive: bool) -> list[Path]:
    files: list[Path] = []
    for input_path in inputs:
        if input_path.is_file() and input_path.suffix.lower() == ".pdf":
            files.append(input_path)
        elif input_path.is_dir():
            pattern = "**/*.pdf" if recursive else "*.pdf"
            files.extend(input_path.glob(pattern))
    return sorted(set(files), key=lambda p: str(p).lower())


def extract_pdf_text(path: Path) -> tuple[str, int, list[str]]:
    warnings: list[str] = []
    reader = PdfReader(str(path))
    parts: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # pragma: no cover - depends on PDF internals
            warnings.append(f"Page {index}: extraction failed: {exc}")
            text = ""
        parts.append(f"\n\n--- Page {index} ---\n\n{text.strip()}")
    text = "\n".join(parts).strip()
    if not text:
        warnings.append("No extractable text. The PDF may be scanned or image-based.")
    return text, len(reader.pages), warnings


def write_summary(output_dir: Path, extracts: list[ResumeExtract]) -> None:
    lines = [
        "# Resume Extraction Summary",
        "",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"Total PDFs extracted: {len(extracts)}",
        "",
        "| File | Candidate Hint | Pages | Characters | Warnings |",
        "|---|---|---:|---:|---|",
    ]
    for item in extracts:
        warning_text = "; ".join(item.warnings) if item.warnings else ""
        lines.append(
            f"| {item.file_name} | {item.candidate_hint} | {item.page_count} | "
            f"{item.char_count} | {warning_text} |"
        )
    (output_dir / "extraction-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract text from one or more resume PDFs or resume folders."
    )
    parser.add_argument(
        "--input",
        nargs="+",
        required=True,
        help="PDF files or folders containing PDFs.",
    )
    parser.add_argument(
        "--output",
        default="output/hr-resume-extracts",
        help="Output folder for extracted text and JSON metadata.",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Disable recursive scanning when inputs are folders.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    input_paths = [Path(value).expanduser().resolve() for value in args.input]
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = iter_pdf_files(input_paths, recursive=not args.no_recursive)
    if not pdf_files:
        print("No PDF files found.", file=sys.stderr)
        return 2

    extracts: list[ResumeExtract] = []
    for pdf_path in pdf_files:
        text, page_count, warnings = extract_pdf_text(pdf_path)
        candidate_hint = candidate_hint_from_filename(pdf_path)
        output_name = sanitize_filename(pdf_path.stem) + ".txt"
        text_path = output_dir / output_name
        header = [
            f"Source: {pdf_path}",
            f"Candidate hint: {candidate_hint}",
            f"Pages: {page_count}",
            f"Extracted at: {datetime.now().isoformat(timespec='seconds')}",
            "",
            "===== Extracted Text =====",
            "",
        ]
        text_path.write_text("\n".join(header) + text + "\n", encoding="utf-8")
        extracts.append(
            ResumeExtract(
                source_path=str(pdf_path),
                output_text_path=str(text_path),
                file_name=pdf_path.name,
                candidate_hint=candidate_hint,
                page_count=page_count,
                char_count=len(text),
                extracted_at=datetime.now().isoformat(timespec="seconds"),
                warnings=warnings,
            )
        )

    json_path = output_dir / "resumes.json"
    json_path.write_text(
        json.dumps([asdict(item) for item in extracts], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_summary(output_dir, extracts)

    print(f"Extracted {len(extracts)} PDF(s) to {output_dir}")
    print(f"Metadata: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

