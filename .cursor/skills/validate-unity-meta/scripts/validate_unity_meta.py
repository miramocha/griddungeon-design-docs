#!/usr/bin/env python3
"""Validate Unity .meta GUIDs and asset pairing under Assets/."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

GUID_RE = re.compile(r"^guid:\s*([0-9a-fA-F]+)\s*$")
VALID_GUID_RE = re.compile(r"^[0-9a-f]{32}$")

# Unity generates .meta for these; flag if missing after agent adds assets.
META_EXPECTED_SUFFIXES = {
    ".cs",
    ".uxml",
    ".uss",
    ".unity",
    ".asset",
    ".prefab",
    ".inputactions",
    ".asmdef",
    ".shader",
    ".png",
    ".jpg",
    ".jpeg",
    ".tga",
    ".wav",
    ".mp3",
    ".fbx",
    ".controller",
    ".overrideController",
    ".mask",
    ".mat",
    ".spriteatlas",
    ".ttf",
    ".otf",
}


def repo_root_from_script() -> Path:
    path = Path(__file__).resolve().parent
    for candidate in [path, *path.parents]:
        if (candidate / "Assets").is_dir() and (candidate / "ProjectSettings").is_dir():
            return candidate
    raise RuntimeError("Could not find Unity project root (Assets/ + ProjectSettings/)")


def collect_meta_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix == ".meta":
            files.append(root.resolve())
            continue
        if not root.is_dir():
            continue
        for path in root.rglob("*.meta"):
            if "Library" in path.parts or "Temp" in path.parts:
                continue
            files.append(path.resolve())
    return sorted(set(files))


def parse_guid(meta_path: Path) -> tuple[str | None, str | None]:
    try:
        text = meta_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return None, f"cannot read: {exc}"

    for line in text.splitlines()[:8]:
        match = GUID_RE.match(line)
        if match:
            return match.group(1), None
    return None, "missing guid: line"


def validate_guid(meta_path: Path, guid: str) -> list[str]:
    errors: list[str] = []
    rel = meta_path.as_posix()
    if len(guid) != 32:
        errors.append(f"{rel}: guid length {len(guid)} (expected 32)")
    if not VALID_GUID_RE.match(guid):
        errors.append(f"{rel}: guid must be 32 lowercase hex [0-9a-f] (got {guid!r})")
    return errors


def asset_path_for_meta(meta_path: Path) -> Path:
    name = meta_path.name
    if not name.endswith(".meta"):
        return meta_path
    return meta_path.with_name(name[: -len(".meta")])


def check_pairing(meta_files: list[Path], assets_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for meta_path in meta_files:
        if not meta_path.is_relative_to(assets_root):
            continue
        asset = asset_path_for_meta(meta_path)
        if not asset.exists():
            errors.append(f"{meta_path.relative_to(assets_root).as_posix()}: orphan (no asset)")

    for asset in assets_root.rglob("*"):
        if not asset.is_file():
            continue
        if asset.suffix == ".meta":
            continue
        if asset.name.endswith("~"):
            continue
        meta = Path(str(asset) + ".meta")
        if asset.suffix not in META_EXPECTED_SUFFIXES:
            continue
        if not meta.exists():
            warnings.append(
                f"{asset.relative_to(assets_root).as_posix()}: missing .meta (let Unity import)"
            )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or folders to scan (default: Assets/)",
    )
    parser.add_argument(
        "--no-pairing",
        action="store_true",
        help="Skip orphan/missing .meta pairing checks",
    )
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Treat missing .meta warnings as errors",
    )
    args = parser.parse_args()

    root = repo_root_from_script()
    assets_root = root / "Assets"
    if args.paths:
        scan_roots = [(root / p).resolve() for p in args.paths]
    else:
        scan_roots = [assets_root]

    meta_files = collect_meta_files(scan_roots)
    if not meta_files:
        print("[validate_unity_meta] no .meta files found", file=sys.stderr)
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    guid_to_meta: dict[str, str] = {}

    for meta_path in meta_files:
        guid, parse_err = parse_guid(meta_path)
        if parse_err:
            errors.append(f"{meta_path.as_posix()}: {parse_err}")
            continue
        assert guid is not None
        errors.extend(validate_guid(meta_path, guid.lower()))
        if guid != guid.lower():
            warnings.append(f"{meta_path.as_posix()}: guid should be lowercase")

        key = guid.lower()
        prev = guid_to_meta.get(key)
        if prev:
            errors.append(f"duplicate guid {key}: {prev} and {meta_path.as_posix()}")
        else:
            guid_to_meta[key] = meta_path.as_posix()

    if not args.no_pairing and assets_root.is_dir():
        pair_errors, pair_warnings = check_pairing(meta_files, assets_root)
        errors.extend(pair_errors)
        warnings.extend(pair_warnings)

    for warning in warnings:
        print(f"[warn] {warning}")

    for error in errors:
        print(f"[FAIL] {error}")

    if errors:
        print(f"[validate_unity_meta] {len(errors)} error(s)", file=sys.stderr)
        return 1

    print(f"[ok] {len(meta_files)} .meta file(s) checked")
    if warnings and args.strict_warnings:
        print(f"[validate_unity_meta] {len(warnings)} warning(s) in strict mode", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
