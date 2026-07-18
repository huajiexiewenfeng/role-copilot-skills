from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys


DEFAULT_MAX_BYTES = 2_000_000
RESOURCE_ATTRIBUTES = {"src", "srcset", "href", "poster", "action", "data"}
NETWORK_PATTERNS = (
    re.compile(r"https?://", re.IGNORECASE),
    re.compile(r"@import\s+url\s*\(", re.IGNORECASE),
    re.compile(r"\bfetch\s*\(", re.IGNORECASE),
    re.compile(r"\bXMLHttpRequest\b", re.IGNORECASE),
    re.compile(r"\bWebSocket\b", re.IGNORECASE),
)


class ContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.doctypes = 0
        self.html_roots = 0
        self.sections = 0
        self.svgs = 0
        self.scripts = 0
        self.iframes = 0
        self.external_resources: list[str] = []
        self.svg_records: list[dict[str, bool]] = []
        self._svg_stack: list[dict[str, bool]] = []

    def handle_decl(self, decl: str) -> None:
        if decl.strip().lower() == "doctype html":
            self.doctypes += 1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attributes = {name.lower(): value for name, value in attrs}
        if tag == "html":
            self.html_roots += 1
        elif tag == "section":
            self.sections += 1
        elif tag == "script":
            self.scripts += 1
        elif tag == "iframe":
            self.iframes += 1

        if tag == "svg":
            record = {
                "role": (attributes.get("role") or "").lower() == "img",
                "title": False,
                "desc": False,
            }
            self.svgs += 1
            self.svg_records.append(record)
            self._svg_stack.append(record)
        elif self._svg_stack and tag == "title":
            self._svg_stack[-1]["title"] = True
        elif self._svg_stack and tag == "desc":
            self._svg_stack[-1]["desc"] = True

        for name, value in attrs:
            if name.lower() not in RESOURCE_ATTRIBUTES or value is None:
                continue
            normalized = value.strip().lower()
            if normalized.startswith(("http://", "https://", "//")):
                self.external_resources.append(value)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "svg" and self._svg_stack:
            self._svg_stack.pop()


def validate_html(
    path: Path, required_terms: tuple[str, ...], max_bytes: int = DEFAULT_MAX_BYTES
) -> dict:
    path = Path(path)
    raw = path.read_bytes()
    errors: list[str] = []

    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        errors.append("utf8-bom")

    try:
        text = raw[3:].decode("utf-8") if has_bom else raw.decode("utf-8")
    except UnicodeDecodeError:
        errors.append("invalid-utf8")
        text = raw.decode("utf-8", errors="replace")

    parser = ContractParser()
    parser.feed(text)
    parser.close()

    if parser.doctypes != 1:
        errors.append("doctype-count")
    if parser.html_roots != 1:
        errors.append("html-root-count")
    if parser.sections < 1:
        errors.append("section-missing")
    if parser.svgs < 1:
        errors.append("svg-missing")
    if parser.scripts:
        errors.append("script-forbidden")
    if parser.iframes:
        errors.append("iframe-forbidden")
    if parser.external_resources:
        errors.append("external-resource-forbidden")
    if any(pattern.search(text) for pattern in NETWORK_PATTERNS):
        errors.append("network-reference-forbidden")
    if parser.svg_records and any(
        not all(record.values()) for record in parser.svg_records
    ):
        errors.append("svg-accessibility-incomplete")
    if not re.search(r"@media\s*\([^)]*max-width\s*:", text, re.IGNORECASE):
        errors.append("responsive-rule-missing")
    if "prefers-reduced-motion" not in text.lower():
        errors.append("reduced-motion-rule-missing")
    if "prefers-color-scheme" not in text.lower():
        errors.append("color-scheme-rule-missing")
    if len(raw) > max_bytes:
        errors.append("size-limit-exceeded")
    for term in required_terms:
        if term not in text:
            errors.append(f"required-term-missing:{term}")

    return {
        "overall": "passed" if not errors else "failed",
        "errors": errors,
        "metrics": {
            "sizeBytes": len(raw),
            "sectionCount": parser.sections,
            "svgCount": parser.svgs,
            "scriptCount": parser.scripts,
            "iframeCount": parser.iframes,
            "externalResourceCount": len(parser.external_resources),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate one offline Technical Visual Companion HTML file."
    )
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--required-term", action="append", default=[])
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = validate_html(
            args.html, tuple(args.required_term), max_bytes=args.max_bytes
        )
    except OSError as exc:
        report = {
            "overall": "failed",
            "errors": [f"file-read-failed:{exc}"],
            "metrics": {},
        }
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if report["overall"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
