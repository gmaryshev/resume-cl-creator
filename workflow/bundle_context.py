#!/usr/bin/env python3
"""Build a traceable, compact context package for a resume generation run."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_REGISTRY = Path("workflow/source_registry.json")
DEFAULT_OUTPUT_ROOT = Path(".workflow/bundles")
SUMMARY_THRESHOLD = 8000


class BundleError(Exception):
    """Raised when a context bundle cannot be built safely."""


def load_registry(path: Path) -> dict[str, Any]:
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BundleError(f"Source registry not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BundleError(f"Invalid source registry {path}: {exc}") from exc

    if not isinstance(registry, dict) or not isinstance(registry.get("groups"), list):
        raise BundleError("Source registry must contain a 'groups' array")
    return registry


def compact_text(text: str) -> str:
    """Remove transport-only whitespace while preserving source content."""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    compacted: list[str] = []
    blank_pending = False
    for line in lines:
        if line.strip():
            if blank_pending and compacted:
                compacted.append("")
            compacted.append(line.strip() if not line.startswith((" ", "\t")) else line)
            blank_pending = False
        else:
            blank_pending = True
    return "\n".join(compacted).strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _relative_path(root: Path, candidate: Path) -> str:
    try:
        return candidate.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise BundleError(f"Source is outside repository root: {candidate}") from exc


def _matches_exclude(relative_path: str, patterns: Iterable[str]) -> bool:
    path = Path(relative_path)
    return any(path.match(pattern) for pattern in patterns)


def discover_sources(root: Path, registry: dict[str, Any]) -> list[dict[str, str]]:
    discovered: dict[str, dict[str, str]] = {}
    for group in registry["groups"]:
        if not isinstance(group, dict) or not isinstance(group.get("name"), str):
            raise BundleError("Every source group needs a name")
        trust = group.get("trust", "unclassified")
        excludes = group.get("exclude", [])
        if not isinstance(trust, str) or not isinstance(excludes, list):
            raise BundleError(f"Invalid source group configuration: {group['name']}")
        for pattern in group.get("include", []):
            if not isinstance(pattern, str):
                raise BundleError(f"Invalid include pattern in group {group['name']}")
            for candidate in root.glob(pattern):
                if not candidate.is_file():
                    continue
                relative = _relative_path(root, candidate)
                if _matches_exclude(relative, excludes):
                    continue
                existing = discovered.get(relative)
                if existing and existing["trust"] != trust:
                    raise BundleError(
                        f"Source {relative} has conflicting trust levels: "
                        f"{existing['trust']} and {trust}"
                    )
                discovered[relative] = {
                    "path": relative,
                    "group": group["name"],
                    "trust": trust,
                }
    if not discovered:
        raise BundleError("Source registry did not discover any files")
    return [discovered[path] for path in sorted(discovered)]


def _read_record(root: Path, source: dict[str, str]) -> dict[str, Any]:
    path = root / source["path"]
    try:
        original = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BundleError(f"Could not read approved source {path}: {exc}") from exc
    compacted = compact_text(original)
    if not compacted:
        raise BundleError(f"Approved source is empty: {path}")
    return {
        **source,
        "sha256": sha256_text(original),
        "original_characters": len(original),
        "included_characters": len(compacted),
        "content": compacted,
    }


def _job_record(root: Path, job_path: Path) -> dict[str, Any]:
    resolved = job_path if job_path.is_absolute() else root / job_path
    relative = _relative_path(root, resolved)
    if not resolved.is_file():
        raise BundleError(f"Job description not found: {resolved}")
    return _read_record(
        root,
        {"path": relative, "group": "job-description", "trust": "job-input"},
    )


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return slug or "run"


def build_bundle(
    root: Path,
    job_description: Path,
    registry_path: Path = DEFAULT_REGISTRY,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    summary_threshold: int = SUMMARY_THRESHOLD,
    run_name: str | None = None,
) -> Path:
    root = root.resolve()
    registry_path = registry_path if registry_path.is_absolute() else root / registry_path
    output_root = output_root if output_root.is_absolute() else root / output_root
    registry = load_registry(registry_path)
    sources = [_read_record(root, source) for source in discover_sources(root, registry)]
    job = _job_record(root, job_description)

    all_records = [job, *sources]
    summaries = [
        {
            "source": record["path"],
            "reason": "Source exceeds the compact-summary threshold.",
            "characters": record["included_characters"],
            "instruction": (
                "Summarize only verifiable facts and achievements. Preserve "
                "source path and section references; do not add technologies, "
                "dates, metrics, or responsibilities not present in the source."
            ),
        }
        for record in all_records
        if record["included_characters"] > summary_threshold
    ]

    bundle_name = _safe_slug(run_name or Path(job["path"]).stem)
    bundle_dir = output_root / bundle_name
    suffix = 2
    while bundle_dir.exists():
        bundle_dir = output_root / f"{bundle_name}-{suffix}"
        suffix += 1
    bundle_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = bundle_dir / "manifest.json"
    markdown_path = bundle_dir / "context.md"

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "bundle_format": "markdown-plus-json",
        "registry": {
            "path": _relative_path(root, registry_path),
            "version": registry.get("version"),
            "sha256": sha256_text(registry_path.read_text(encoding="utf-8")),
        },
        "job_description": job["path"],
        "sources": [
            {
                key: value
                for key, value in record.items()
                if key != "content"
            }
            for record in all_records
        ],
        "summarization": {
            "provider": "copilot-agent",
            "automated_by_script": False,
            "threshold_characters": summary_threshold,
            "requests": summaries,
        },
    }

    markdown_parts = [
        "# Resume and Cover Letter Context Bundle",
        "",
        "This bundle contains approved source material for one generation run.",
        "Treat source trust levels and provenance as authoritative constraints.",
        "",
        "## Generation constraints",
        "",
        "- Use only verifiable facts from the included sources.",
        "- Do not invent technologies, dates, metrics, employers, or credentials.",
        "- Keep source paths when summarizing or selecting evidence.",
        "- Follow workflow instructions and formatting rules before job-specific preferences.",
        "",
        "## Job description",
        "",
        f"<!-- source: {job['path']} | sha256: {job['sha256']} -->",
        job["content"],
    ]
    for record in sources:
        markdown_parts.extend(
            [
                "",
                f"## Source: `{record['path']}`",
                "",
                f"<!-- group: {record['group']} | trust: {record['trust']} | "
                f"sha256: {record['sha256']} -->",
                record["content"],
            ]
        )
    if summaries:
        markdown_parts.extend(
            [
                "",
                "## Copilot summarization requests",
                "",
                "The script cannot call the cloud model. If compacting these sources "
                "further, satisfy each request and retain the listed provenance.",
            ]
        )
        for request in summaries:
            markdown_parts.extend(
                [
                    "",
                    f"- `{request['source']}` ({request['characters']} characters): "
                    f"{request['instruction']}",
                ]
            )

    markdown_path.write_text("\n".join(markdown_parts) + "\n", encoding="utf-8")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return bundle_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_description", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--summary-threshold", type=int, default=SUMMARY_THRESHOLD)
    parser.add_argument(
        "--run-name",
        help="Optional output directory name; a numeric suffix avoids overwrites.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        bundle_dir = build_bundle(
            root=args.root,
            job_description=args.job_description,
            registry_path=args.registry,
            output_root=args.output_root,
            summary_threshold=args.summary_threshold,
            run_name=args.run_name,
        )
    except BundleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(bundle_dir)
    print(f"created: {bundle_dir / 'context.md'}")
    print(f"created: {bundle_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
