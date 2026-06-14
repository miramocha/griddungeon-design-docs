---
name: stratum-floor-layout-check
description: >-
  Validates Grid Dungeon authored ExplorationFloor ASCII layouts (row width,
  walkability BFS, Act 1 funnel and tutorial gates) using Tools/layout_grid_check.py
  in griddungeon-game. Use when editing S1B1FLayoutBuilder, draft floor ASCII in
  design-docs archive, debugging path bypasses to stairsDown, or before committing
  map layout changes.
---

# Stratum floor layout check

Runs in **griddungeon-game** — see [game repo skill](https://github.com/miramocha/griddungeon-game/blob/main/.cursor/skills/stratum-floor-layout-check/SKILL.md) for full workflow.

```powershell
cd griddungeon-game
python Tools/layout_grid_check.py
python Tools/layout_grid_check.py --floor b2f
python Tools/layout_grid_check.py --floor b3f
```

**Floor assets:** **Floor Painter → Apply** or Unity **Apply s1_B*n*F MVP1 layout** — Python `sync_*_asset_tiles.py` scripts were removed.

MVP1 strata grid: **21×21**.
