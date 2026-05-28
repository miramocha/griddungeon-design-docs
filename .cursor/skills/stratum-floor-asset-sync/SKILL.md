---
name: stratum-floor-asset-sync
description: >-
  Regenerates griddungeon-game s1_B1F.asset m_tiles from authored ASCII rows.
  Use after design-docs and game builder layout edits, when Play Mode tiles
  disagree with spec, or when handing off floor content without Unity Apply menu.
---

# Stratum floor asset sync (design-docs)

Runs in **griddungeon-game** only. Update design ASCII first, then mirror rows in the game builder before sync.

**Floor Painter** ([#107](https://github.com/miramocha/griddungeon-game/issues/107)) is the preferred path for layout edits in Unity (**GridDungeon → Content → Floor Painter** → Apply). Use Python/builder sync when `S1B1FLayoutBuilder` rows are authoritative.

**Create Dev Bootstrap** registers floors only — it does **not** overwrite painted `StratumFloor` assets.

## Workflow

1. Layout check green (game repo):

```powershell
cd path/to/griddungeon-game
python Tools/layout_grid_check.py
```

2. Sync asset:

```powershell
python Tools/sync_b1f_asset_tiles.py
```

3. Commit game repo: builder + `Tools/layout_grid_check.py` + `s1_B1F.asset` (+ design-docs ASCII if changed).

Canonical steps: [stratum-floor-asset-sync](https://github.com/miramocha/griddungeon-game/tree/main/.cursor/skills/stratum-floor-asset-sync) in **griddungeon-game**.
