# Floor level painter (Unity Editor)

**Status:** Epic [#75](https://github.com/miramocha/griddungeon-game/issues/75) (game repo)  
**Authority:** [ADR 002 — floor level painter](../decisions/002-mapping-model.md#authoring--floor-level-painter-primary)

Design-time tool only. Players never draw on the map ([ADR 002](../decisions/002-mapping-model.md) — auto-chart on explore).

## Goal

Paint (launch) dungeon floors in Unity and export **`ExplorationFloor`** assets.

**Layout authority (2026-06):** **Draft — not locked.** During iteration, serialized `Assets/Content/Floors/s1_B*n*F.asset` (Floor Painter **Apply** / import) is runtime truth. Design ASCII lives in [archive — (launch) S1 floor layouts (draft)](../archive/mvp1-s1-floor-layouts-draft.md). `S1B*FLayoutBuilder` is dev reset only — not spec authority.

## Coordinate system

Logic indices are **cell counts** (0…19). **FPV world scale** (10 Unity units per cell, corner anchor) is authored separately in [floor art FPV](floor-art-fpv.md) — the painter does not change `ExplorationGridMetrics`.

| Rule | Value |
|------|--------|
| Grid | 20×20 at launch strata floors |
| Storage | **North-up** row array (`k_RowsNorthUp[0]` = north edge) |
| Game `y` | **0 = south** — `y = GridSize - 1 - row` |
| Index | `x + y * width` (`ExplorationFloorLayout.ToIndex`) |

Same as [archive — s1_B1F ASCII](../archive/mvp1-s1-floor-layouts-draft.md#s1_b1f--outskirts-gate-intro--gate) and `Tools/layout_grid_check.py` (draft reference until layout lock).

## ASCII symbols (launch)

| Char | Walkable | Tile flags / notes |
|------|----------|-------------------|
| `#` | No | Wall |
| `X` | No | Tutorial / script blocker |
| `.` | Yes | Open floor |
| `C` | No | **Chest** — `ChestItemId`; party **cannot enter** the cell; **Interact** (`Space` / `Z`) from an adjacent walkable cell while **facing** the chest ([#105](https://github.com/miramocha/griddungeon-game/issues/105)) |
| `G` | Yes | **Gather** — `HasGatherNode`; (launch) instant loot on interact when on cell ([ADR 014](../decisions/014-mvp1-exploration-map.md)) |
| `v`, `^`, `M`, `E` | Yes | **Role markers** — intro (`E`), gate (`M`), exit up (`^`), exit down (`v`); Apply scans the grid and writes entry coords + **`FloorExitLink[]`** ([#107](https://github.com/miramocha/griddungeon-game/issues/107), [ADR 040](../../decisions/040-floor-exit-topology-graph.md)). **Multiple `^` / `v` per floor** allowed — one link row per marker cell. |

**Walkability (target):** impassable `#`, `X`, and `C` only; all other palette symbols walkable — same rule as `S1B1FLayoutBuilder.IsWalkableSymbol` after [#105](https://github.com/miramocha/griddungeon-game/issues/105). Until that ships, B1F layout code may still treat `C` as walkable gather (legacy); painter palette and export ([#77](https://github.com/miramocha/griddungeon-game/issues/77)) should follow this table.

## Markers vs parallel pin store ([#107](https://github.com/miramocha/griddungeon-game/issues/107))

| Layer | Authority |
|-------|-----------|
| **Grid char** | Authoring truth for entry/stairs — `E` / `M` / `^` / `v` on cells |
| **Painter UI** | Marker palette tools write those chars; coord summary **derived** from grid scan on refresh |
| **`ExplorationFloor` asset** | Runtime exploration reads serialized coords + tiles — **not** ASCII scan at play time |
| **Anti-pattern** | Parallel pin coord store (e.g. `FloorPainterPinState`) — removed; grid is the only painter state for markers |

When gate and hub stairs share a cell (canonical B1F), only `^` appears on the grid; Apply sets `partyEntryGate` to the `^` cell when `M` is absent.

## Multi-exit markers and topology graph

**Target model ([ADR 040](../../decisions/040-floor-exit-topology-graph.md)):** scalar `stairsUp` / `stairsDown` are replaced by **`FloorExitLink[]`** on each `ExplorationFloor`. Painter and optional Graph Toolkit topology compile into the same array.

| Layer | Authority |
|-------|-----------|
| **Grid `^` / `v`** | **Where** each exit sits — multiple markers per floor |
| **Painter Apply** | Emits one `FloorExitLink` per marker (`exitId`, `cell`, `direction`); may leave `target*` empty until topology compile |
| **Stratum topology graph** (editor-only, [#253](https://github.com/miramocha/griddungeon-game/issues/253)) | Fills `targetFloorKey`, `targetSpawnCell`, `targetFacing`; validates paired up/down between floors — **no runtime graph** |
| **`ExplorationFloor` asset** | Runtime reads `exitLinks[]` only |

**Orthogonal:** quest / flag **gating** of pins and events is [ADR 031](../../decisions/031-floor-event-pin-condition-graph.md) — not fields on exit links. Campaign **hub entry** spawn stays in per-stratum policy ([ADR 025](../../decisions/025-campaign-exploration-target.md)).

**(launch) migration:** S1 floors keep one `^` and one `v` each; migration ticket [#250](https://github.com/miramocha/griddungeon-game/issues/250) compiles today’s scalar coords into link rows before multi-exit painter UI ([#252](https://github.com/miramocha/griddungeon-game/issues/252)).

## Workflow

1. **GridDungeon ? Content ? Floor Painter** (UI Toolkit) — paint layout ([#76](https://github.com/miramocha/griddungeon-game/issues/76), [#107](https://github.com/miramocha/griddungeon-game/issues/107)).
2. Place **entry / gate / stairs** with marker tools (`E` / `M` / `^` / `v` on cells) ? **Apply** to `Assets/Content/Floors/s1_B*n*F.asset` ([#77](https://github.com/miramocha/griddungeon-game/issues/77)).
3. **3D walls (optional):** open `Assets/Scenes/Floors/s1_B*n*F.unity` ? **Floor Art Grid ? Populate Wall Blocks** ? save scene ([floor-art-fpv.md](floor-art-fpv.md)).
4. **Validate** paths in-editor ([#78](https://github.com/miramocha/griddungeon-game/issues/78)) — parity with `layout_grid_check.py` presets.
5. Play Mode: **DevBootstrap F2** + `MapView` / exploration movement. **Apply during Play Mode** refreshes runtime walkability via Floor Painter sync; exit/re-enter Play Mode after Edit Mode Apply.

**Create Dev Bootstrap** registers (launch) floors in `ContentDatabase` and **does not overwrite** existing `ExplorationFloor` assets ([#107](https://github.com/miramocha/griddungeon-game/issues/107)). To reset a floor to canonical builder ASCII, use **GridDungeon ? Content ? Apply s1_B*n*F (launch) layout** (`ExplorationFloorDevMenu`) — destructive to painted layouts.

Legacy Python/builder path (CI / regression only): [stratum-floor-layout-check](https://github.com/miramocha/griddungeon-game/tree/main/.cursor/skills/stratum-floor-layout-check) on `S1B*FLayoutBuilder` rows — not the day-to-day authoring path.

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
| ~~4 Export rows~~ | [#79](https://github.com/miramocha/griddungeon-game/issues/79) — **cancelled** (Unity asset is source of truth; no ASCII export to docs) |

**Follow-up epic:** [#109](https://github.com/miramocha/griddungeon-game/issues/109) — story Event cells (`!`) + `storyEventId` on floor assets ([#110](https://github.com/miramocha/griddungeon-game/issues/110)–[#113](https://github.com/miramocha/griddungeon-game/issues/113)).

**Later (idea):** quest- and flag-gated pins / triggers — compile from a Graph Toolkit floor graph to `ExplorationFloor` rules; see [ADR 031](../../decisions/031-floor-event-pin-condition-graph.md). (launch) ships static pins + C# triggers; gating graph is not required for [#109](https://github.com/miramocha/griddungeon-game/issues/109).

**Exit topology (parallel track):** stratum **connectivity graph** compiles `FloorExitLink[]` — see [ADR 040](../../decisions/040-floor-exit-topology-graph.md) and [game #249](https://github.com/miramocha/griddungeon-game/issues/249). Distinct from ADR 031 event gating.

## Related

- [04-tech-notes — Map authoring](04-tech-notes.md#map-authoring--hud-adr-002)
- [05-class-design — `FloorPainterWindow`](05-class-design.md)
- [ADR 040 — Floor exit topology graph](../../decisions/040-floor-exit-topology-graph.md)
