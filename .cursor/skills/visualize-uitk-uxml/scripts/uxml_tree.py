#!/usr/bin/env python3
"""Print an ASCII tree for Unity UI Toolkit UXML (name, class, control text)."""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Unity 6 default UXML namespace
UI_NS = "UnityEngine.UIElements"
CONTROL_TAGS = frozenset(
    {
        "Button",
        "Label",
        "TextField",
        "Toggle",
        "ScrollView",
        "DropdownField",
        "Slider",
        "ProgressBar",
        "Foldout",
        "ListView",
        "TreeView",
        "Template",
        "Instance",
    }
)


def local_tag(tag: str) -> str:
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1]
    if ":" in tag:
        return tag.split(":", 1)[-1]
    return tag


def short_attrs(elem: ET.Element) -> str:
    parts: list[str] = []
    name = elem.attrib.get("name")
    if name:
        parts.append(f'name="{name}"')
    cls = elem.attrib.get("class")
    if cls:
        parts.append(f'class="{cls}"')
    tag = local_tag(elem.tag)
    if tag in {"Button", "Label"}:
        text = elem.attrib.get("text")
        if text:
            parts.append(f'text="{text}"')
    if tag == "Style":
        src = elem.attrib.get("src")
        if src:
            parts.append(f'src="{src}"')
    if tag == "Instance":
        template = elem.attrib.get("template")
        if template:
            parts.append(f'template="{template}"')
    return " ".join(parts)


def format_node(elem: ET.Element, depth: int, prefix: str, is_last: bool) -> list[str]:
    tag = local_tag(elem.tag)
    # ASCII branches — safe on Windows consoles; agents may render Unicode in markdown
    branch = "`-- " if is_last else "+-- "
    indent = prefix + ("    " if is_last else "|   ")
    attr = short_attrs(elem)
    label = f"{tag}"
    if attr:
        label += f"  ({attr})"
    lines = [f"{prefix}{branch}{label}"]

    children = list(elem)
    for index, child in enumerate(children):
        child_last = index == len(children) - 1
        lines.extend(format_node(child, depth + 1, indent, child_last))
    return lines


def parse_uxml(path: Path) -> ET.Element:
    tree = ET.parse(path)
    root = tree.getroot()
    if local_tag(root.tag) != "UXML":
        raise ValueError(f"Not a UXML root: {path}")
    return root


def build_tree(path: Path, max_depth: int | None = None) -> str:
    root = parse_uxml(path)
    header = [f"{path.as_posix()}", ""]
    body: list[str] = []
    children = list(root)
    # Skip <Style> siblings at depth 0 for cleaner trees unless they are only children
    visible = [c for c in children if local_tag(c.tag) != "Style"]
    if not visible:
        visible = children
    for index, child in enumerate(visible):
        if max_depth is not None and max_depth < 1:
            break
        body.extend(
            format_node(child, 0, "", index == len(visible) - 1)
        )
    return "\n".join(header + body)


def main() -> int:
    parser = argparse.ArgumentParser(description="ASCII tree for Unity UXML files.")
    parser.add_argument("paths", nargs="+", type=Path, help="UXML file paths")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Limit depth (1 = immediate children of UXML root)",
    )
    args = parser.parse_args()

    exit_code = 0
    for index, path in enumerate(args.paths):
        if index > 0:
            print()
        try:
            print(build_tree(path.resolve(), args.max_depth))
        except (OSError, ET.ParseError, ValueError) as exc:
            print(f"[FAIL] {path}: {exc}", file=sys.stderr)
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
