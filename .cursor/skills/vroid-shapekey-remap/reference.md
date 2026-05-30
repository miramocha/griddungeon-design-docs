# VRoid shape key reference

## Parser (default)

```python
CATEGORY_MAP = {
    "ALL": "All",
    "BRW": "Brow",
    "EYE": "Eye",
    "MTH": "Mouth",
    "HA": "Teeth",
}

def cap_first(s: str) -> str:
    return s[0].upper() + s[1:] if s else s

def convert_fcl_shape_key(name: str, prefix_out: str = "vroid") -> str | None:
    if not name.startswith("Fcl_"):
        return None
    parts = name.split("_")
    # parts[0] == "Fcl", parts[1] == category
    out = [prefix_out]
    cat = parts[1]
    out.append(CATEGORY_MAP.get(cat, cap_first(cat.lower())))
    for part in parts[2:]:
        out.append(cap_first(part))
    result = "".join(out)
    return result.replace("Fung", "Fang")
```

## Segment patterns

| Pattern | Example |
|---------|---------|
| Full face | `Fcl_ALL_Joy` → `vroidAllJoy` |
| Brow | `Fcl_BRW_Surprised` → `vroidBrowSurprised` |
| Eye + side | `Fcl_EYE_Joy_R` → `vroidEyeJoyR` |
| Mouth viseme | `Fcl_MTH_O` → `vroidMouthO` |
| Mouth skin | `Fcl_MTH_SkinFung_L` → `vroidMouthSkinFangL` |
| Teeth + index | `Fcl_HA_Fung2_Up` → `vroidTeethFang2Up` |
| Teeth short | `Fcl_HA_Short_Low` → `vroidTeethShortLow` |

## Dry-run checks

```python
def dry_run(names, converter=convert_fcl_shape_key):
    mapping = {}
    for n in names:
        new = converter(n)
        if new:
            mapping[n] = new
    # duplicates in target names
    inv = {}
    for old, new in mapping.items():
        inv.setdefault(new, []).append(old)
    dups = {k: v for k, v in inv.items() if len(v) > 1}
    # conflict: new name already exists as a different key
    existing = set(names)
    conflicts = [new for new in mapping.values() if new in existing and new not in mapping]
    return mapping, dups, conflicts
```

## Drivers / animation

After rename, grep drivers:

```python
for obj in bpy.data.objects:
    if not obj.animation_data:
        continue
    for d in obj.animation_data.drivers:
        if "key_blocks" in d.data_path:
            # check for old Fcl_ names in data_path
            ...
```

VRoid `.vrm` / Unity exports use blend shape names from export time — plan a re-export after rename.

## Customization hooks

| User request | Adjustment |
|--------------|--------------|
| Keep abbreviations | `CATEGORY_MAP[cat] = cat` or `cap_first(cat.lower())` |
| `vroid_` snake prefix | Join with `_` instead of camelCase |
| No typo fix | Remove `.replace("Fung", "Fang")` |
| Include all keys | Separate pass; do not use `Fcl_` guard |

## Related skills

- **blender-bone-remap** — armature bones, vertex groups, `.l`/`.r` at end
