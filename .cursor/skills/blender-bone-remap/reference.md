# Bone remap reference

## Hair converter (VRoid → standard)

```python
import re

RE_END_SIDE = re.compile(r'^Hair(\d+)_(\d+)_end_(L|R)$', re.I)
RE_END = re.compile(r'^Hair(\d+)_(.+)_end$', re.I)
RE = re.compile(r'^Hair(\d+)_(.+)$', re.I)

def norm_strand(s):
    if s.endswith('_L'):
        base = s[:-2]
        return f"{base.zfill(2) if base.isdigit() else base.lower()}l"
    if s.endswith('_R'):
        base = s[:-2]
        return f"{base.zfill(2) if base.isdigit() else base.lower()}r"
    if s.isdigit():
        return s.zfill(2)
    return s.lower()

def convert_vroid_hair(old):
    m = RE_END_SIDE.match(old)
    if m:
        return f"hair{m.group(2).zfill(2)}{m.group(3).lower()}.{m.group(1)}.end"
    m = RE_END.match(old)
    if m:
        seg, strand = int(m.group(1)), norm_strand(m.group(2))
        return f"hair{strand}.{seg}.end"
    m = RE.match(old)
    if not m:
        return None
    return f"hair{norm_strand(m.group(2))}.{int(m.group(1))}"
```

## Side suffix at end (fix `hair07l.7`)

```python
RE_SIDED = re.compile(r'^hair(\d+)([lr])\.(\d+)(\.end)?$', re.I)

def side_to_end(old):
    m = RE_SIDED.match(old)
    if not m:
        return None
    strand, side, link, end = m.group(1), m.group(2).lower(), m.group(3), m.group(4) or ''
    return f"hair{strand}.{link}{end}.{side}"
```

## Mirror strand pairs (01↔03, 02↔04)

Strand 03 bones become `hair01.{link}.r`; strand 01 becomes `hair01.{link}.l`. Same for 02↔04 on `hair02.*`.

```python
def link_suffix(name):
    m = re.match(r'^hair\d+\.(.+)$', name)
    return m.group(1) if m else None

# hair01.* -> hair01.{link}.l ; hair03.* -> hair01.{link}.r
# hair02.* -> hair02.{link}.l ; hair04.* -> hair02.{link}.r
```

## Body converter (PascalCase + _L/_R)

```python
def pascal_to_camel(s):
    return s[0].lower() + s[1:] if s else s

# Center: Root, Hips, Spine, Chest, UpperChest, Neck, Head
# Bust(\d+)_end_(L|R) -> bust.{n}.end.{side}
# (Index|Thumb|...)(\d+)_(L|R) -> {finger}.{n}.{side}
# (.+)_(L|R) -> {pascalToCamel}.{side}
# Hood_01 -> hood.1 ; Hood_end_01 -> hood.1.end
# HoodString(\d+)_01_(L|R) -> hoodString.{n}.{side}
```

## Blender mirror troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| Mirror ignores paired bone | Side not final suffix; use `.l`/`.r` at end |
| Wrong strand moves | Strand id differs between pairs; unify base (`hair01` not `hair01` vs `hair03`) |
| Mesh does not follow | Vertex group name ≠ bone name |
| Pose action broken | F-Curves still reference old or `J_Sec_*` paths |

Blender may accept `.L`/`.R` (uppercase) in some tools; ask user if lowercase fails.

## Meshes to scan

```python
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.find_armature():
        # list vertex_groups where name in bone_set or matches 'Hair'/'hair'
```

Report: `bone_named_vgs`, count with non-zero weights, stale groups (old names after remap).

## Separate armatures

Check `obj.modifiers` type `ARMATURE` — each armature needs its own mapping. Skirt rigs often keep `SkirtSide0_01_L` until explicitly remapped.
