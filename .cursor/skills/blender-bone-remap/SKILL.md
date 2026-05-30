---
name: blender-bone-remap
description: >-
  Remaps and renames Blender armature bones (especially VRoid/VRM rigs) to a
  consistent lowercase convention with .l/.r mirror suffixes, updates vertex
  groups and animation paths, and optional hair strand mirror pairing when the user
  confirms pairs. Use when the
  user asks to rename, clean up, or standardize bones, vertex groups, rig
  naming, VRoid hair bones, or symmetry/mirror bone pairs in Blender.
---

# Blender bone remap (VRoid / custom rigs)

## When to use

- Renaming bones for readability or Blender X-Axis Mirror / Symmetrize
- Migrating VRoid-style names (`Hair1_06`, `UpperLeg_L`, `J_Sec_*`) to a project standard
- Pairing mirrored strands or limbs under shared base names + `.l` / `.r`

Requires a **connected Blender MCP** (`execute_blender_code`) unless the user only wants a mapping plan.

## Before changing anything

1. **Confirm scope** with the user (hair only, main armature, skirt armature, all meshes).
2. **Inspect** the armature: bone list, parents, which meshes have matching vertex groups and non-zero weights.
3. **Dry-run** the full `old → new` map; report duplicates and unmapped bones.
4. **Save** or remind the user to save before applying.

Use AskQuestion when rules are ambiguous (abbreviation expansion, `.l` vs `.L`, `_hairends` handling).

**Before any hair mirror pairing:** VRoid strand numbers in bone names (`Hair1_03`, `Hair2_07_L`) are **not** mirror metadata — they are independent strand ids. **Ask the user** whether any physical strands should be treated as left/right pairs for Blender X-Axis Mirror (see below). Do **not** assume 01↔03 / 02↔04 unless they confirm.

## Naming standard (default)

| Category | Pattern | Examples |
|----------|---------|----------|
| Center (no side) | `{part}` | `root`, `hips`, `spine`, `chest`, `upperChest`, `neck`, `head` |
| Limb / single bone | `{part}.{side}` | `upperLeg.l`, `shoulder.r`, `hand.l` |
| Digit chains | `{finger}.{link}.{side}` | `thumb.2.l`, `index.3.r` |
| Hair (strand-first) | `hair{strand}.{link}.{side}` | `hair06.1.l`, `hair07.7.r` |
| Hair (center strand) | `hair{strand}.{link}` | `hair05.1`, `hair06.3.end` |
| Hair tip bone | `...end` before side | `hair01.4.end.l`, `hair07.7.end.r` |
| Bust / props | `{name}.{n}.{side}` or `.end` | `bust.2.end.l`, `hoodString.2.l` |

**Mirror rule:** Blender symmetrize expects the **same base name** with `.l` / `.r` as the **last** suffix (after `.end` if present).

**Wrong for mirror:** `hair07l.7` (side embedded in strand id)  
**Right:** `hair07.7.l` ↔ `hair07.7.r` (same logical strand, opposite sides)

## VRoid hair: parse old names

Old pattern: `Hair{segment}_{strand}` or `Hair{segment}_{strand}_end` or `Hair{seg}_{strand}_end_{L|R}`.

- First number = link along chain (1 = near head)
- After `_` = **physical strand id** (`01`, `03`, `06`, `07_L`, …) — VRoid does **not** mark “this strand mirrors that one” in the name
- Default remap: `hair{physicalStrand}.{link}` (and `.l`/`.r` only when the **old** name already had `_L`/`_R` or you moved side to the suffix)

## VRoid hair: mirror strands (optional — ask first)

Only if the user wants Blender symmetrize across **paired** bangs/twin strands:

1. **AskQuestion** (or equivalent): “Does this rig use mirrored hair strand pairs? If yes, which physical strand ids map together (e.g. 01↔03, 02↔04)?”
2. If **no** — skip `build_hair_mirror_mapping`; keep distinct `hair03.*`, `hair04.*`, etc.
3. If **yes** — apply their pair list so both physical strands share one logical base + `.l`/`.r`:

| User-confirmed pair (example) | Result |
|-------------------------------|--------|
| physical `01` + `03` | `hair01.{link}.l` / `hair01.{link}.r` (not `hair03.*`) |
| physical `02` + `04` | `hair02.{link}.l` / `hair02.{link}.r` |

The 01↔03 / 02↔04 table is a **common project convention**, not something VRoid encodes in export names.

Common typo fix when user asks: `Fung` → `Fang` (shape keys; separate from bones).

## VRoid body: parse old names

| Old | New |
|-----|-----|
| `UpperLeg_L` | `upperLeg.l` |
| `Thumb2_R` | `thumb.2.r` |
| `Bust2_end_L` | `bust.2.end.l` |
| `HoodString2_end_01_L` | `hoodString.2.end.l` |
| `Hood_01` | `hood.1` |

PascalCase + `_L`/`_R` → camelCase + `.{side}` at end.

## What must be updated together

| Data | Match bone names? | Notes |
|------|-------------------|--------|
| Armature bones | Yes | Two-pass via `__tmp__{old}` if collisions possible |
| Vertex groups | Yes (same string as bone) | Often auto-syncs on bone rename in recent Blender; verify |
| Action F-Curves | `pose.bones["Name"]` paths | Old `J_Sec_*` / `J_Bip_*` curves won't auto-fix |
| Constraint subtargets | Yes | Rare on hair; check pose constraints |
| Shape keys | No | Unless explicitly bone-driven |

Rename **only groups with weights** if user wants minimal diff; rename **all** matching groups on deforming meshes for consistency.

**Separate armatures** (e.g. `Skirt.Armature`) need their own map — do not assume main-armature renames apply.

## Workflow

```
Progress:
- [ ] 1. List bones + categorize (hair / body / prop / other armature)
- [ ] 2. Agree naming rules; **ask** whether any hair strands are mirrored pairs (list physical ids); skip pair merge if none
- [ ] 3. Build mapping dict; dry-run (duplicates, unmapped)
- [ ] 4. Apply bones (temp rename → final)
- [ ] 5. Apply vertex groups on scoped meshes
- [ ] 6. Patch F-Curves + constraint subtargets
- [ ] 7. Verify (paired `.l`/`.r` hair only if user requested; weights; pose test)
```

### Apply order (bones)

1. Build complete `mapping: old_name → new_name`
2. Pass 1: `bone.name = f"__tmp__{old}"` for all keys
3. Pass 2: `bone.name = new` from temp
4. Rename vertex groups on each mesh in scope
5. Replace `pose.bones["old"]` in all `bpy.data.actions` fcurves

### Verify

- No bones left matching `^[A-Z]` or `_(L|R)$` (if full cleanup was requested)
- Every `.l` bone has matching `.r` partner where expected
- Sample mesh: weighted groups still exist under new names
- Pose mode: move `.l` bone with X-Axis Mirror enabled

## Phased rollout (recommended)

1. **Hair** on main armature + hair meshes
2. **Body** on main armature + body/clothes meshes
3. **Secondary armatures** (skirt, accessories)
4. **Animation** — retarget or drop stale `J_Sec_*` actions

## Custom groups

Non-bone groups (e.g. `_hairends`) are **not** updated by bone rename. Ask before renaming; map explicitly if needed.

## Utility script

For apply logic and parsers, read and run (via MCP) [scripts/remap_bones.py](scripts/remap_bones.py).

```python
# Minimal MCP usage pattern:
# 1) exec open('path/to/remap_bones.py').read()  OR paste functions
# 2) mapping = build_vroid_hair_mapping(arm) + build_body_mapping(arm)
# 3) Only after user confirms mirror pairs:
#    mapping.update(build_hair_mirror_mapping(arm, pairs=(("01","03"), ("02","04"))))
# 4) apply_mapping(mapping, armature_name='Armature', mesh_names=[...])
```

## Additional reference

- Full convention tables and edge cases: [reference.md](reference.md)
- Worked examples from a VRoid rig: [examples.md](examples.md)

## Out of scope unless asked

- Re-parenting bones, changing roll/rest pose, re-weighting meshes
- VRM export extension metadata (humanoid bone aliases)
- Auto-fixing all historical actions without user confirmation
