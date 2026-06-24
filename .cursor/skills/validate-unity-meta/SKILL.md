---
name: validate-unity-meta
description: >-
  Validates Unity .meta GUID format (32 lowercase hex), uniqueness, and asset pairing
  under Assets/. Use when creating or editing .meta files, after adding Unity assets
  from the agent, before commit, or when diagnosing missing script types (CS0246).
---

# Validate Unity metadata

## When to use

- Agent created or edited any file under `Assets/**/*.meta`
- User reports `CS0246` / missing `MonoBehaviour` after agent added a script
- Before commit that includes new `Assets/` files or `.meta` changes
- After consolidating scenes/prefabs that reference script GUIDs

## Default policy

**Do not hand-author `.meta` files.** Add the asset; let Unity Editor generate `.meta`.

Only write `.meta` when unavoidable (document why in the PR). Never guess GUIDs.

## Workflow

```
Task Progress:
- [ ] 1. Create/edit asset under Assets/ (prefer no .meta in diff)
- [ ] 2. Unity import (user) OR validate existing .meta if agent touched them
- [ ] 3. Run validate_unity_meta.py
- [ ] 4. Fix [FAIL] before commit
```

### 1. Run validator (griddungeon-game root)

Full `Assets/` scan:

```powershell
python .cursor/skills/validate-unity-meta/scripts/validate_unity_meta.py
```

Changed paths only:

```powershell
python .cursor/skills/validate-unity-meta/scripts/validate_unity_meta.py Assets/Scripts/UI/Views/MyView.cs.meta
python .cursor/skills/validate-unity-meta/scripts/validate_unity_meta.py Assets/UI/Screens/Exploration
```

Strict (missing `.meta` warnings fail too — use after Unity import):

```powershell
python .cursor/skills/validate-unity-meta/scripts/validate_unity_meta.py --strict-warnings
```

GUID + duplicates only (no pairing):

```powershell
python .cursor/skills/validate-unity-meta/scripts/validate_unity_meta.py --no-pairing path/to/file.meta
```

### 2. Interpret output

| Prefix | Meaning |
|--------|---------|
| `[ok]` | All checked meta files valid |
| `[FAIL]` | Block commit — fix GUID length/format, duplicates, orphan `.meta` |
| `[warn]` | Missing `.meta` — normal until Unity imports; re-run after refresh |

### 3. Common fixes

| Failure | Fix |
|---------|-----|
| `guid length 33` | Delete `.meta`; let Unity regenerate, or correct to 32 chars |
| `must be 32 lowercase hex` | Remove invalid characters; use `a-f0-9` only |
| `duplicate guid` | Delete one `.meta`; Unity regenerates a new GUID |
| `orphan (no asset)` | Delete stray `.meta` or restore missing asset |
| `missing .meta` | Open project in Unity; do not invent meta in agent |

## Rule gate

Follow [.cursor/rules/unity-meta-files.mdc](../../rules/unity-meta-files.mdc) whenever touching `Assets/**`.

## Related

- Script: [scripts/validate_unity_meta.py](scripts/validate_unity_meta.py)
- Unity pitfall: broken script import → `unity-common-pitfalls.mdc`
