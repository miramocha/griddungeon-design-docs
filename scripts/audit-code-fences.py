#!/usr/bin/env python3
"""Count markdown code fences in design-docs vault."""

import os
import re
from collections import defaultdict

EXCLUDE_PARTS = (".cursor", "archive", "github-drafts")


def area(path: str) -> str:
    if path.startswith("docs/02-systems/"):
        return "02-systems"
    if path.startswith("docs/03-content/"):
        return "03-content"
    if path.startswith("docs/04-dev/"):
        return "04-dev"
    if path.startswith("decisions/"):
        return "decisions"
    if path.startswith("docs/plans/"):
        return "plans"
    if path.startswith("docs/refs/"):
        return "refs"
    if path.startswith("docs/"):
        return "docs-root"
    return "other"


def collect_files(exclude_04_dev: bool = False) -> list[str]:
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = [d for d in dirnames if d not in (".git", ".obsidian")]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn).replace("\\", "/")
            norm = path.removeprefix("./")
            if any(x in path for x in EXCLUDE_PARTS):
                continue
            if exclude_04_dev and norm.startswith("docs/04-dev/"):
                continue
            files.append(norm)
    return sorted(files)


def audit(files: list[str], exclude_04_dev: bool = False) -> None:
    area_fences: dict[str, int] = defaultdict(int)
    area_files: dict[str, int] = defaultdict(int)
    lang_fences: dict[str, int] = defaultdict(int)
    file_rows: list[tuple[int, str, dict[str, int]]] = []
    csharp_system: list[tuple[str, int]] = []

    for path in files:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        opens = list(re.finditer(r"^```(\w*)", text, re.M))
        if not opens:
            continue
        langs: dict[str, int] = defaultdict(int)
        for m in opens:
            lang = m.group(1) or "(plain)"
            langs[lang] += 1
            lang_fences[lang] += 1
        n = len(opens)
        a = area(path)
        area_fences[a] += n
        area_files[a] += 1
        file_rows.append((n, path, dict(langs)))
        if a == "02-systems" and langs.get("csharp", 0):
            csharp_system.append((path, langs["csharp"]))

    total = sum(area_fences.values())
    suffix = " (excl 04-dev)" if exclude_04_dev else ""
    print(
        f"TOTAL{suffix}: {total} fence opens in {len(file_rows)} files "
        f"(excl .cursor, archive, github-drafts)"
    )
    print()
    print("BY AREA:")
    for a, n in sorted(area_fences.items(), key=lambda x: -x[1]):
        print(f"  {a:14} {n:4} fences  ({area_files[a]} files)")
    print()
    print("BY LANGUAGE:")
    for lang, n in sorted(lang_fences.items(), key=lambda x: -x[1]):
        print(f"  {lang:14} {n:4}")
    print()
    print("TOP 20 FILES BY FENCE COUNT:")
    for n, path, langs in sorted(file_rows, reverse=True)[:20]:
        ls = ", ".join(f"{k}:{v}" for k, v in sorted(langs.items()))
        print(f"  {n:3}  {path}  [{ls}]")

    # DTO-ish csharp in system docs (pseudo-signatures, sealed class, enum)
    dto_hits: list[tuple[str, int]] = []
    for path in files:
        if not path.startswith("docs/02-systems/"):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        blocks = re.findall(r"^```csharp\n(.*?)^```", text, re.M | re.S)
        if not blocks:
            continue
        dto_hits.append((path, len(blocks)))
    print()
    print("02-SYSTEMS files with ```csharp blocks (count):")
    for path, c in sorted(dto_hits, key=lambda x: -x[1]):
        print(f"  {c}  {path}")
    print()
    print("02-SYSTEMS csharp fence opens:")
    if csharp_system:
        for path, c in sorted(csharp_system):
            print(f"  {c}  {path}")
    else:
        print("  (none)")


if __name__ == "__main__":
    audit(collect_files())
    print()
    print("=" * 60)
    print("SAME AUDIT EXCLUDING docs/04-dev/ (integration guides):")
    print("=" * 60)
    audit(collect_files(exclude_04_dev=True), exclude_04_dev=True)
