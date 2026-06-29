#!/usr/bin/env python3
"""Sync the LLM Wiki Doctor source script into the project-init scaffold."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = Path(__file__).resolve().parents[1]
SOURCE = SKILL_ROOT / "scripts" / "llm_wiki_doctor.py"
SCAFFOLD_ROOT = SKILL_ROOT / "assets" / "llm-wiki-doctor-scaffold"
TARGET = SCAFFOLD_ROOT / ".llm-wiki" / "tools" / "llm_wiki_doctor.py"
VERSION = SCAFFOLD_ROOT / ".llm-wiki" / "tools" / "VERSION"


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def version_text() -> str:
    return "\n".join(
        [
            "tool=llm_wiki_doctor",
            f"source_path={SOURCE.relative_to(ROOT).as_posix()}",
            f"source_commit={git_commit()}",
            "",
        ]
    )


def check() -> int:
    if not TARGET.exists():
        print(f"missing scaffold doctor: {TARGET}", file=sys.stderr)
        return 1
    if SOURCE.read_bytes() != TARGET.read_bytes():
        print("scaffold doctor is out of sync with scripts/llm_wiki_doctor.py", file=sys.stderr)
        return 1
    if not VERSION.exists():
        print(f"missing scaffold VERSION: {VERSION}", file=sys.stderr)
        return 1
    return 0


def sync() -> int:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(SOURCE.read_bytes())
    VERSION.write_text(version_text(), encoding="utf-8")
    print(f"synced {SOURCE.relative_to(ROOT).as_posix()} -> {TARGET.relative_to(ROOT).as_posix()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync LLM Wiki Doctor scaffold copy.")
    parser.add_argument("--check", action="store_true", help="Fail if the scaffold copy is missing or stale.")
    args = parser.parse_args(argv)
    return check() if args.check else sync()


if __name__ == "__main__":
    sys.exit(main())
