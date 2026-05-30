"""
VRoid Fcl_* shape key rename utilities for Blender (bpy).
Run via MCP execute_blender_code or Blender Scripting workspace.

    mapping = build_fcl_mapping(obj.data.shape_keys.key_blocks)
    report = dry_run_mapping(mapping, existing_names=[kb.name for kb in ...])
    apply_shape_key_mapping(obj, mapping)
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

import bpy

CATEGORY_MAP = {
    "ALL": "All",
    "BRW": "Brow",
    "EYE": "Eye",
    "MTH": "Mouth",
    "HA": "Teeth",
}


def cap_first(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def convert_fcl_shape_key(
    name: str,
    prefix_out: str = "vroid",
    category_map: Optional[Dict[str, str]] = None,
    fix_fung: bool = True,
) -> Optional[str]:
    if not name.startswith("Fcl_"):
        return None
    parts = name.split("_")
    if len(parts) < 2:
        return None
    cmap = category_map or CATEGORY_MAP
    out = [prefix_out]
    cat = parts[1]
    out.append(cmap.get(cat, cap_first(cat.lower())))
    for part in parts[2:]:
        if part:
            out.append(cap_first(part))
    result = "".join(out)
    if fix_fung:
        result = result.replace("Fung", "Fang")
    return result


def build_fcl_mapping(
    key_blocks: Iterable,
    only_if_changed: bool = True,
    **convert_kwargs,
) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for kb in key_blocks:
        new = convert_fcl_shape_key(kb.name, **convert_kwargs)
        if not new:
            continue
        if only_if_changed and new == kb.name:
            continue
        mapping[kb.name] = new
    return mapping


def dry_run_mapping(
    mapping: Dict[str, str],
    existing_names: Optional[Iterable[str]] = None,
) -> dict:
    inv: Dict[str, List[str]] = {}
    for old, new in mapping.items():
        inv.setdefault(new, []).append(old)
    duplicates = {k: v for k, v in inv.items() if len(v) > 1}
    conflicts: List[str] = []
    if existing_names is not None:
        existing = set(existing_names)
        for old, new in mapping.items():
            if new in existing and new != old:
                conflicts.append(new)
    return {
        "count": len(mapping),
        "duplicates": duplicates,
        "conflicts": sorted(set(conflicts)),
        "preview": sorted(mapping.items(), key=lambda x: x[1]),
    }


def apply_shape_key_mapping(
    obj: bpy.types.Object,
    mapping: Dict[str, str],
) -> dict:
    if not obj.data or not obj.data.shape_keys:
        return {"error": "no shape keys on object"}
    renamed: List[Tuple[str, str]] = []
    for kb in obj.data.shape_keys.key_blocks:
        new = mapping.get(kb.name)
        if new:
            old = kb.name
            kb.name = new
            renamed.append((old, new))
    return {"object": obj.name, "renamed": renamed, "count": len(renamed)}


def remap_object_fcl_keys(
    object_name: str,
    dry_run_only: bool = False,
    **convert_kwargs,
) -> dict:
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"error": f"object not found: {object_name}"}
    if not obj.data.shape_keys:
        return {"error": f"no shape keys on {object_name}"}
    names = [kb.name for kb in obj.data.shape_keys.key_blocks]
    mapping = build_fcl_mapping(obj.data.shape_keys.key_blocks, **convert_kwargs)
    report = dry_run_mapping(mapping, existing_names=names)
    if dry_run_only:
        return report
    apply_result = apply_shape_key_mapping(obj, mapping)
    return {**report, **apply_result}
