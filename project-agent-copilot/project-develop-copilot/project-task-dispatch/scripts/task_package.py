from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile


SCHEMA_VERSION = 1
UTF8_BOM = b"\xef\xbb\xbf"


def _canonical_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if raw.startswith(UTF8_BOM):
        raw = raw[len(UTF8_BOM) :]
    text = raw.decode("utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _safe_document_name(name: str) -> PurePosixPath:
    if not isinstance(name, str) or not name:
        raise ValueError("unsafe document name: expected a non-empty string")
    if "\\" in name:
        raise ValueError(f"unsafe document name: {name}")
    path = PurePosixPath(name)
    has_windows_drive = len(name) >= 3 and name[1] == ":" and name[2] == "/"
    if (
        path.is_absolute()
        or has_windows_drive
        or ".." in path.parts
        or path.as_posix() != name
    ):
        raise ValueError(f"unsafe document name: {name}")
    return path


def _chunk_text(text: str, chunk_size: int) -> list[dict]:
    if chunk_size <= 0:
        raise ValueError("chunk size must be positive")
    pieces = [
        text[offset : offset + chunk_size]
        for offset in range(0, len(text), chunk_size)
    ]
    if not pieces:
        pieces = [""]
    total = len(pieces)
    return [
        {"index": index, "total": total, "text": piece}
        for index, piece in enumerate(pieces, start=1)
    ]


def _bundle_hash(documents: list[tuple[str, str, bytes]]) -> str:
    digest_input = bytearray()
    for name, document_sha, content in documents:
        digest_input.extend(name.encode("utf-8"))
        digest_input.extend(b"\0")
        digest_input.extend(document_sha.encode("utf-8"))
        digest_input.extend(b"\0")
        digest_input.extend(content)
    return _sha256(bytes(digest_input))


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def build_package(
    input_dir: Path | str,
    output_manifest: Path | str,
    chunk_size: int,
) -> dict:
    source = Path(input_dir)
    output = Path(output_manifest)
    if chunk_size <= 0:
        raise ValueError("chunk size must be positive")
    if not source.is_dir():
        raise ValueError(f"input directory does not exist: {source}")

    document_files = sorted(
        (path for path in source.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(source).as_posix(),
    )
    documents: list[dict] = []
    bundle_documents: list[tuple[str, str, bytes]] = []
    for document_path in document_files:
        name = document_path.relative_to(source).as_posix()
        _safe_document_name(name)
        content = _canonical_bytes(document_path)
        document_sha = _sha256(content)
        text = content.decode("utf-8")
        documents.append(
            {
                "name": name,
                "sha256": document_sha,
                "byteLength": len(content),
                "chunks": _chunk_text(text, chunk_size),
            }
        )
        bundle_documents.append((name, document_sha, content))

    manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "encoding": "utf-8",
        "lineEndings": "lf",
        "documents": documents,
        "bundleSha256": _bundle_hash(bundle_documents),
    }
    _write_json(output, manifest)
    return manifest


def _validate_chunks(chunks: object) -> str:
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("invalid chunk sequence")
    expected_total = len(chunks)
    text_parts: list[str] = []
    for expected_index, chunk in enumerate(chunks, start=1):
        if not isinstance(chunk, dict):
            raise ValueError("invalid chunk sequence")
        if (
            chunk.get("index") != expected_index
            or chunk.get("total") != expected_total
            or not isinstance(chunk.get("text"), str)
        ):
            raise ValueError("invalid chunk sequence")
        text_parts.append(chunk["text"])
    return "".join(text_parts)


def _read_manifest(path: Path) -> dict:
    raw = path.read_bytes()
    if raw.startswith(UTF8_BOM):
        raise ValueError("manifest must be UTF-8 without BOM")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("manifest must be a JSON object")
    return value


def verify_package(
    manifest_path: Path | str,
    output_dir: Path | str,
) -> list[Path]:
    manifest = _read_manifest(Path(manifest_path))
    if manifest.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("unsupported schema version")
    if manifest.get("encoding") != "utf-8":
        raise ValueError("unsupported encoding")
    if manifest.get("lineEndings") != "lf":
        raise ValueError("unsupported line endings")

    raw_documents = manifest.get("documents")
    if not isinstance(raw_documents, list):
        raise ValueError("documents must be a list")

    verified: list[tuple[PurePosixPath, str, bytes]] = []
    bundle_documents: list[tuple[str, str, bytes]] = []
    seen_names: set[str] = set()
    previous_name: str | None = None
    for document in raw_documents:
        if not isinstance(document, dict):
            raise ValueError("document must be an object")
        name = document.get("name")
        safe_name = _safe_document_name(name)
        if name in seen_names or (
            previous_name is not None and name <= previous_name
        ):
            raise ValueError("documents must be uniquely sorted by name")
        seen_names.add(name)
        previous_name = name

        text = _validate_chunks(document.get("chunks"))
        if text.startswith("\ufeff") or "\r" in text:
            raise ValueError(f"document is not canonical UTF-8/LF: {name}")
        content = text.encode("utf-8")
        document_sha = _sha256(content)
        if document.get("sha256") != document_sha:
            raise ValueError(f"document hash mismatch: {name}")
        if document.get("byteLength") != len(content):
            raise ValueError(f"document byte length mismatch: {name}")

        verified.append((safe_name, name, content))
        bundle_documents.append((name, document_sha, content))

    if manifest.get("bundleSha256") != _bundle_hash(bundle_documents):
        raise ValueError("bundle hash mismatch")

    destination = Path(output_dir)
    destination.parent.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    with tempfile.TemporaryDirectory(
        prefix="task-package-",
        dir=destination.parent,
    ) as temporary:
        stage = Path(temporary)
        for safe_name, _, content in verified:
            staged_path = stage.joinpath(*safe_name.parts)
            staged_path.parent.mkdir(parents=True, exist_ok=True)
            staged_path.write_bytes(content)
        if destination.exists():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        shutil.copytree(stage, destination)
        for safe_name, _, _ in verified:
            written.append(destination.joinpath(*safe_name.parts))
    return written


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build or verify a lossless project task document package."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build")
    build.add_argument("--input", required=True, type=Path)
    build.add_argument("--output", required=True, type=Path)
    build.add_argument("--chunk-size", required=True, type=int)

    verify = commands.add_parser("verify")
    verify.add_argument("--manifest", required=True, type=Path)
    verify.add_argument("--output-dir", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        if arguments.command == "build":
            build_package(
                arguments.input,
                arguments.output,
                arguments.chunk_size,
            )
        else:
            verify_package(arguments.manifest, arguments.output_dir)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
