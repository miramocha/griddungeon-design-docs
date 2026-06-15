---
name: stratum-floor-layout-check
description: >-
  Validates Grid Dungeon S1 MVP1 floor assets via Floor Painter validation and
  Edit Mode S1Mvp1FloorAssetTests in griddungeon-game. Use when editing committed
  floor assets, debugging path bypasses to stairsDown, or before committing map layout changes.
---

# Stratum floor layout check

Runs in **griddungeon-game** — see [game repo skill](https://github.com/miramocha/griddungeon-game/blob/main/.cursor/skills/stratum-floor-layout-check/SKILL.md) for full workflow.

1. Edit `Assets/Content/Floors/s1_B*n*F.asset` in **Floor Painter → Apply**.
2. **Floor Painter → Validate** on the grid.
3. Unity **Test Runner → Map → `S1Mvp1FloorAssetTests`** (user-driven).

Python `layout_grid_check.py` and C# `S1B*FLayoutBuilder` were removed — committed floor assets are the layout authority.
