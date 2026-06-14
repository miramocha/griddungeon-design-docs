---
name: stratum-floor-asset-sync
description: >-
  Regenerates s1_B1F.asset m_tiles from authored ASCII rows via
  Tools/sync_b1f_asset_tiles.py. Use after S1B1F layout edits, when Play Mode
  tiles disagree with S1B1FLayoutBuilder, or when handing off floor content without
  opening Unity Apply menu.
---

# Stratum floor asset sync (s1_B1F)

## When to use

- After changing `S1B1FLayoutBuilder` / `S1_B1F_ROWS` in Python
- `s1_B1F.asset` walkability stale vs builder (Play Mode shows wrong walls)
- User asks to update floor **asset metadata** without running **GridDungeon → Content → Apply s1_B1F MVP1 layout**

**Prefer Floor Painter** when authoring layout in the Editor: **GridDungeon → Content → Floor Painter** → **Apply** writes tiles and marker coords ([#107](https://github.com/miramocha/griddungeon-game/issues/107)). **MVP1 S1 layouts are draft** — serialized `s1_B*n*F.asset` is runtime authority until lock ([archive](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/archive/mvp1-s1-floor-layouts-draft.md)).

**Create Dev Bootstrap** does **not** call Apply s1_B1F MVP1 layout — it only registers floors if missing ([#107](https://github.com/miramocha/griddungeon-game/issues/107)).

**Scope (MVP1):** `Assets/Content/Floors/s1_B1F.asset` only. B2F/B3F: Floor Painter Apply or **Apply s1_B*n*F MVP1 layout** menu.

## Prerequisites

1. **`S1_B1F_ROWS` matches** `S1B1FLayoutBuilder.k_RowsNorthUp` (20 strings × 20 chars).
2. **Layout check green** — run skill **stratum-floor-layout-check** first:

```powershell
python Tools/layout_grid_check.py
```

Do not sync if exit code is 1.

## Workflow

From **griddungeon-game** repo root:

```powershell
python Tools/sync_b1f_asset_tiles.py
```

- Rewrites `m_tiles` (400 entries: `IsWalkable`, `HasGatherNode` from `C`/`G` symbols)
- Preserves `m_stairsUp`, `m_stairsDown`, party entry fields, encounter tables
- Prints: `Updated .../s1_B1F.asset (400 tiles)`

## After sync

| Step | Action |
|------|--------|
| Git | Commit `S1B1FLayoutBuilder.cs`, `Tools/layout_grid_check.py`, `s1_B1F.asset` together |
| Unity | Let Editor reimport asset; optional: **Apply s1_B1F MVP1 layout** only when intentionally resetting to builder |
| 3D art | Re-run **Populate Wall Blocks** on `s1_B1F.unity` if wall mesh layout changed |
| Tests | User runs **Test Runner → Map → `S1B1FLayoutTests`** |

## Alternative (Editor)

| Tool | Use |
|------|-----|
| **Floor Painter → Apply** | Painted grid → asset (markers + tiles) |
| **Apply s1_B1F MVP1 layout** | Overwrites asset from `S1B1FLayoutBuilder` — destructive reset |

## Related

- Validation: skill **stratum-floor-layout-check**
- [Tools/README.md](../../Tools/README.md)
- [floor-level-painter.md](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/02-systems/floor-level-painter.md)
