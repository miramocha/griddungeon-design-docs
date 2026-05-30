---
name: vroid-shapekey-remap
description: >-
  Renames VRoid Fcl_* shape keys on Blender meshes to lower camelCase vroid*
  names with expanded category abbreviations, typo fixes, and optional scope
  limits. Use when cleaning up VRoid face expressions, Fcl shape keys,
  vroid-prefixed keys, or shape key naming on face.main / VRM avatars in Blender.
---

# VRoid shape key remap

## When to use

- Cleaning VRoid-exported `Fcl_*` shape keys on face or body meshes
- Standardizing to `vroid{Category}{Name}` lower camelCase (e.g. `vroidBrowAngry`)
- Fixing known VRoid typos (`Fung` → `Fang`) during rename

Requires **Blender MCP** (`execute_blender_code`) or running [scripts/remap_shapekeys.py](scripts/remap_shapekeys.py) in Blender.

## Before changing anything

1. **Confirm mesh** (e.g. `face.main`) and **scope** — `Fcl_*` only vs all shape keys.
2. **List** current shape keys; count `Fcl_*` vs ARKit / custom / Japanese keys.
3. **Dry-run** mapping; report duplicates and keys that would be skipped.
4. **Ask** when rules are unclear (abbreviation table, typo scope, side suffix style).

Use AskQuestion for: category expansion vs abbreviated, non-`Fcl` keys, `Fung`→`Fang` scope.

## Default naming standard

**Input:** `Fcl_{CAT}_{Part}_{Part}...` or `Fcl_{CAT}_{Part}_{L|R}`

**Output:** `vroid` + expanded category + capitalized parts (lower camelCase)

| VRoid `CAT` | Expanded | Example in → out |
|-------------|----------|----------------|
| `ALL` | `All` | `Fcl_ALL_Neutral` → `vroidAllNeutral` |
| `BRW` | `Brow` | `Fcl_BRW_Angry` → `vroidBrowAngry` |
| `EYE` | `Eye` | `Fcl_EYE_Close_L` → `vroidEyeCloseL` |
| `MTH` | `Mouth` | `Fcl_MTH_A` → `vroidMouthA` |
| `HA` | `Teeth` | `Fcl_HA_Hide` → `vroidTeethHide` |
| (other) | Capitalize segment | `Fcl_XYZ_Foo` → `vroidXyzFoo` |

**Rules:**

- Prefix `Fcl_` → `vroid` (not `Vroid` / `vroid_`)
- Split on `_`; drop empty segments
- Each segment after category: first letter upper, rest as-is (`Close` + `L` → `CloseL`)
- **Typo:** replace `Fung` with `Fang` in the **full result string** (covers `SkinFung`, `Fung1`, etc.)
- **`Basis`** and non-`Fcl_*` keys: **do not rename** unless user explicitly includes them

## Side / mirror notes

VRoid uses `_L` / `_R` as final underscore segments (`Fcl_EYE_Close_L` → `vroidEyeCloseL`), not `.l` / `.r` dots. That differs from the bone remap skill; do not mix conventions unless the user asks.

Shape key mirror in Blender is separate from bone X-Mirror; confirm whether the user wants ARKit pairs renamed later.

## Workflow

```
Progress:
- [ ] 1. Find target mesh object(s) and shape key count
- [ ] 2. Agree scope (Fcl only?) and category/typo rules
- [ ] 3. Build mapping; dry-run (duplicates, conflicts with existing names)
- [ ] 4. Rename key_blocks on mesh data (shape_keys)
- [ ] 5. Verify drivers, actions, NLA, mesh keys referencing shape key names
- [ ] 6. User saves .blend
```

### Apply (shape keys only)

```python
for kb in obj.data.shape_keys.key_blocks:
    new = convert_fcl_shape_key(kb.name)
    if new:
        kb.name = new
```

Renaming a shape key **does not** auto-update:

- Drivers with `key_blocks["OldName"]` in `data_path`
- Shape keys referenced in other objects’ drivers or geometry nodes
- Exported VRM blend shape names (re-export needed)

Search actions/drivers after bulk rename if expressions break.

## Phased scope (typical)

1. **`Fcl_*` on `face.main`** (VRoid expressions + visemes)
2. Leave ARKit (`browInnerUp`, `eyeBlinkLeft`, …) and custom (`_mouthPress+…`) unless requested
3. Leave Japanese / Live2D-style keys (`あ`, `まばたき`, …) unless requested

## Utility script

See [scripts/remap_shapekeys.py](scripts/remap_shapekeys.py) for `convert_fcl_shape_key`, `build_mapping`, `dry_run`, `apply_shape_key_mapping`.

## Additional reference

- Abbreviation table and edge cases: [reference.md](reference.md)
- Full face.main examples: [examples.md](examples.md)

## Out of scope unless asked

- Changing shape key **values** or merging duplicate shapes
- Renaming bones (use **blender-bone-remap** skill)
- Auto-fixing all drivers in the file without checking
