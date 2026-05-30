# Bone remap examples (VRoid-style rig)

## Hair strand 06 (center, 3 links)

| Old | New |
|-----|-----|
| `Hair1_06` | `hair06.1` |
| `Hair2_06` | `hair06.2` |
| `Hair3_06` | `hair06.3` |
| `Hair3_06_end` | `hair06.3.end` |

## Hair strand 07 (side, long chain)

| Old | New |
|-----|-----|
| `Hair1_07_L` | `hair07.1.l` |
| `Hair7_07_L` | `hair07.7.l` |
| `Hair7_07_end_L` | `hair07.7.end.l` |

After side-at-end fix: same names (already correct if mapped from `hair07l.7` → `hair07.7.l`).

## Optional: mirrored strands 01 + 03 (only if user confirms)

VRoid names `Hair1_01` and `Hair1_03` as separate strands — **not** labeled as mirrors. Default pass: `hair01.1` and `hair03.1`. Apply this table **only** when the user wants 01↔03 paired for Blender symmetrize:

| Old (physical strand) | New (shared logical pair) |
|-----------------------|---------------------------|
| `Hair1_01` | `hair01.1.l` |
| `Hair1_03` | `hair01.1.r` |
| `Hair4_01_end` | `hair01.4.end.l` |
| `Hair4_03_end` | `hair01.4.end.r` |

## Body samples

| Old | New |
|-----|-----|
| `UpperLeg_L` | `upperLeg.l` |
| `FaceEye_R` | `faceEye.r` |
| `Thumb2_L` | `thumb.2.l` |
| `Bust2_end_L` | `bust.2.end.l` |
| `HoodString2_end_01_L` | `hoodString.2.end.l` |

## Phased session summary

1. Hair VRoid names → `hair{strand}.{link}`
2. Side embedded in strand → `hair07.7.l`
3. *(Optional, user-confirmed)* Mirror pairs 01/03, 02/04 → shared `hair01.*` / `hair02.*` + `.l`/`.r`
4. Body 70 bones → lowercase + `.l`/`.r`
5. Skirt armature — pending separate pass

## Custom vertex group

`_hairends` on hair meshes: not renamed with bones; optional `hair.ends` if user requests.
