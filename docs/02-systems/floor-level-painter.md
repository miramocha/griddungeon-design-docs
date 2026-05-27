# Floor level painter (Unity Editor)

**Status:** Epic [#75](https://github.com/miramocha/griddungeon-game/issues/75) (game repo)  
**Authority:** [ADR 002 — floor level painter](../decisions/002-mapping-model.md#authoring--floor-level-painter-primary)

Design-time tool only. Players never draw on the map ([ADR 002](../decisions/002-mapping-model.md) — auto-chart on explore).

## Goal

Paint MVP1 dungeon floors in Unity and export **`StratumFloor`** assets without editing `S1B*FLayoutBuilder.k_Rows` in C# or mirroring rows in Python by hand.

## Coordinate system

Logic indices are **cell counts** (0…19). **FPV world scale** (10 Unity units per cell, corner anchor) is authored separately in [floor art FPV](floor-art-fpv.md) — the painter does not change `ExplorationGridMetrics`.

| Rule | Value |
|------|--------|
| Grid | 20×20 for MVP1 strata floors |
| Storage | **North-up** row array (`k_RowsNorthUp[0]` = north edge) |
| Game `y` | **0 = south** — `y = GridSize - 1 - row` |
| Index | `x + y * width` (`StratumFloorLayout.ToIndex`) |

Same as [dungeons — s1_B1F ASCII](../03-content/dungeons-and-encounters.md#s1_b1f--outskirts-gate-intro--gate) and `Tools/layout_grid_check.py`.

## ASCII symbols (MVP1)

| Char | Walkable | Tile flags / notes |
|------|----------|-------------------|
| `#` | No | Wall |
| `X` | No | Tutorial / script blocker |
| `.` | Yes | Open floor |
| `C` | No | **Chest** — `ChestItemId`; party **cannot enter** the cell; **Interact** (`Space` / `Z`) from an adjacent walkable cell while **facing** the chest ([#105](https://github.com/miramocha/griddungeon-game/issues/105)) |
| `G` | Yes | **Gather** — `HasGatherNode`; MVP1 instant loot on interact when on cell ([ADR 014](../decisions/014-mvp1-exploration-map.md)) |
| `v`, `^`, `M`, `E` | Yes | Visual markers; **stairs/entry positions** come from pinned coords on the asset, not from the char alone |

**Walkability (target):** impassable `#`, `X`, and `C` only; all other palette symbols walkable — same rule as `S1B1FLayoutBuilder.IsWalkableSymbol` after [#105](https://github.com/miramocha/griddungeon-game/issues/105). Until that ships, B1F layout code may still treat `C` as walkable gather (legacy); painter palette and export ([#77](https://github.com/miramocha/griddungeon-game/issues/77)) should follow this table.

## Workflow (target)

1. **GridDungeon → Content → Floor Painter** — paint layout ([#76](https://github.com/miramocha/griddungeon-game/issues/76)).
2. Place **entry / gate / stairs** pins ([#77](https://github.com/miramocha/griddungeon-game/issues/77)) → Apply to `Assets/Content/Floors/s1_B*n*F.asset`.
3. **Validate** paths in-editor ([#78](https://github.com/miramocha/griddungeon-game/issues/78)) — parity with `layout_grid_check.py` presets.
4. **Export** ASCII for this doc + optional C# snippet ([#79](https://github.com/miramocha/griddungeon-game/issues/79)).
5. Play Mode: **DevBootstrap F2** + `MapView` / exploration movement.

Until the epic ships, use **Apply s1_B*n*F MVP1 layout** (`StratumFloorDevMenu`) and Python tools per [stratum-floor-layout-check](https://github.com/miramocha/griddungeon-game/tree/main/.cursor/skills/stratum-floor-layout-check).

## Not the same as

| Item | What it is |
|------|------------|
| [#26](https://github.com/miramocha/griddungeon-game/issues/26) | Runtime **HUD** grid refactor (`MapView` + `MapDevPreviewView`) |
| `MapView` | Read-only player map from reveal state |
| FPV floor scenes | Corridor art; optional; does not author collision — [floor-art-fpv.md](floor-art-fpv.md) |

## Epic tracker

| Phase | Issue |
|-------|--------|
| Epic | [#75](https://github.com/miramocha/griddungeon-game/issues/75) |
| 1 Window + paint | [#76](https://github.com/miramocha/griddungeon-game/issues/76) |
| 2 Export asset | [#77](https://github.com/miramocha/griddungeon-game/issues/77) |
| 3 Validate | [#78](https://github.com/miramocha/griddungeon-game/issues/78) |
| 4 Export rows | [#79](https://github.com/miramocha/griddungeon-game/issues/79) |

## Related

- [04-tech-notes — Map authoring](04-tech-notes.md#map-authoring--hud-adr-002)
- [05-class-design — `FloorPainterWindow`](05-class-design-mvp1.md)
