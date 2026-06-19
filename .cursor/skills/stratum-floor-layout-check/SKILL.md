---
name: stratum-floor-layout-check
description: >-
  Validates Grid Dungeon S1 MVP1 floor assets (walkability, funnel paths, exit links)
  via Floor Editor validation and Edit Mode FloorEditorValidationTests.
  Use when editing committed floor assets in Floor Editor, debugging path bypasses
  to stairsDown, or before committing map layout changes.
---

# Stratum floor layout check

## When to use

- Editing `Assets/Content/Floors/s1_B1F.asset`, `s1_B2F.asset`, or `s1_B3F.asset` in **Floor Editor**
- User reports reaching `stairsDown` / `v` without passing tutorial blocker `(10, 13)`
- Before committing layout changes to committed floor assets
- After layout patch — confirm **Floor Editor → Validate** and `FloorEditorValidationTests` agree

**Floor assets:** write tiles with **Floor Editor → Apply** — not Python sync scripts (removed).

## Coordinate system (locked)

| Rule | Value |
|------|--------|
| Grid | **21×21** (`ExplorationGridMetrics.Mvp1FloorGridCells`) |
| Row order in Floor Editor | **North-up** — top row = y=20, bottom row = y=0 (south) |
| Tile index | `x + y * width` (matches `ExplorationFloorLayout.ToIndex`) |
| Impassable | `#` walls; `X` tutorial blocker (`IsBlockedPassage`) until campaign opens cell |
| Campaign cells | `S1CampaignResolver`, `CommittedFloorAssetPaths`, `StoryEventTriggerCatalog` — not duplicated in Python |

## Workflow

1. Edit layout in **Floor Editor** (or tweak asset fields directly when appropriate).
2. **Validate row width** — grid must be **21×21** for MVP1 S1 floors.
3. **Floor Editor → Validate** on the painted grid.
4. Run Unity **Test Runner → Editor → FloorEditor → `FloorEditorValidationTests`** (user-driven; no CLI batch Unity per project rules).

## Built-in regressions (s1_B1F)

`FloorEditorValidationTests` loads committed B1F/B2F/B3F assets. Domain tests (`ExplorationPathGraphTests`, `GatherInteractorTests`, `FoeSystemPatrolTests`, …) assert gameplay against committed floor assets via `Mvp1FloorAssetFixtures` / `S1CampaignResolver`.

## C# parity

Edit Mode uses `FloorLayoutConnectivity` → `MapPathfinder` on `ExplorationFloor` tiles. **Floor Editor → Validate** is floor-agnostic.

## Related

- [Tools/README.md](../../Tools/README.md)
- [floor-editor.md](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/02-systems/floor-editor.md)
- Design ASCII: [archive — s1_B1F (draft)](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/archive/mvp1-s1-floor-layouts-draft.md#s1_b1f--outskirts-gate-intro--gate)
