---
name: stratum-floor-layout-check
description: >-
  Validates Grid Dungeon authored ExplorationFloor ASCII layouts (row width,
  walkability BFS, Act 1 funnel and tutorial gates) using Tools/layout_grid_check.py.
  Use when editing S1B1FLayoutBuilder, draft floor ASCII in design-docs archive, debugging
  path bypasses to stairsDown, or before committing map layout changes.
---

# Stratum floor layout check

## When to use

- Editing `S1B1FLayoutBuilder.k_RowsNorthUp`, MVP1 ASCII in [archive draft layouts](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/archive/mvp1-s1-floor-layouts-draft.md), or painted grids in game assets (**layouts not locked**)
- User reports reaching `stairsDown` / `v` without passing tutorial blocker `(10, 13)`
- Before `sync_b1f_asset_tiles` or Unity **Apply s1_B1F MVP1 layout**
- After layout patch — confirm Edit Mode `S1B1FLayoutTests` and this script agree

## Coordinate system (locked)

| Rule | Value |
|------|--------|
| Grid | 20×20 |
| Row order in code | **North-up** — `k_RowsNorthUp[0]` = y=19, last row = y=0 (south) |
| Cell lookup | `row = GRID - 1 - y`, then `rows[row][x]` |
| Tile index | `x + y * width` (matches `ExplorationFloorLayout.ToIndex`) |
| Impassable symbols | `#` (wall), `X` (tutorial blocker until campaign opens cell) |
| Authoritative markers | C# constants (`StairsUp`, `StairsDown`, spawns) — `v`/`^`/`M` in ASCII are visual hints only |

## Workflow

1. Edit layout in **`Assets/Scripts/Runtime/Content/S1B1FLayoutBuilder.cs`** (`k_RowsNorthUp`).
2. **Mirror the same 20 strings** in `Tools/layout_grid_check.py` → `S1_B1F_ROWS` (keep in sync until shared extract exists).
3. **Validate row width** — every string must be **exactly 20** characters (common bug: 21 on north-cap rows).
4. Run checks from **griddungeon-game** repo root:

```powershell
python Tools/layout_grid_check.py
python Tools/layout_grid_check.py --bfs 4,2 10,17
python Tools/layout_grid_check.py --bfs 10,11 10,17
```

5. Exit code **0** = built-in regressions passed; **1** = fix layout before sync/commit.
6. Run Unity **Test Runner → Map → `S1B1FLayoutTests`** (user-driven; no CLI batch Unity per project rules).

## Built-in regressions (s1_B1F)

Script prints `[ok]` / `[FAIL]` for:

- `(10, 16)` walkable — link from `v` alcove to `stairsDown` `(10, 17)`
- North cap walls: `(9,17)`, `(11,17)`, `(9,18)`, `(10,18)`, `(11,18)` not walkable
- Intro `(4,2)` → gate `(10,11)` reachable
- Intro → `stairsDown` **no** static path (west bypass blocked)
- Gate → `stairsDown` **no** static path (`X` at `(10,13)` still impassable in tiles)

Add new checks in `default_checks()` when locking new campaign geometry.

## Ad-hoc BFS

`--bfs START GOAL` uses comma cells, e.g. `4,2` and `10,17`. Prints step path or `no route`.

## C# parity

Edit Mode uses `FloorLayoutConnectivity` in `Assets/Scripts/Runtime/Map/` — delegates to `MapPathfinder` on `ExplorationFloor` tiles (reachability matches this script's BFS). **Floor Painter → Validate** is floor-agnostic (grid size, marker walkability, optional custom path). Locked s1_B*n*F regressions stay in this script and `S1B*FLayoutTests` — not in the painter UI.

## Related

- Asset sync: skill **stratum-floor-asset-sync**
- Scripts: [Tools/README.md](../../Tools/README.md)
- Design ASCII: [archive — s1_B1F (draft)](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/archive/mvp1-s1-floor-layouts-draft.md#s1_b1f--outskirts-gate-intro--gate)
