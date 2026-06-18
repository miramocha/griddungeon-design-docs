# Floor Editor (Unity Editor)

**Status:** Epic [#75](https://github.com/miramocha/griddungeon-game/issues/75) (game repo)  
**Authority:** [ADR 002 — Floor Editor](../decisions/002-mapping-model.md#authoring--floor-editor-primary)

Design-time tool only. Players never draw on the map ([ADR 002](../decisions/002-mapping-model.md) — auto-chart on explore).

## Goal

Paint launch dungeon floors in Unity and export **`ExplorationFloor`** assets.

**Layout authority (2026-06):** **Draft — not locked.** During iteration, serialized `Assets/Content/Floors/s1_B*n*F.asset` (Floor Editor **Save** / Load) is runtime truth. Design ASCII lives in [archive — at launch S1 floor layouts (draft)](../archive/mvp1-s1-floor-layouts-draft.md). `S1B*FLayoutBuilder` is dev reset only — not spec authority.

## Coordinate system

Logic indices are **cell counts** (0…19). **FPV world scale** (10 Unity units per cell, corner anchor) is authored separately in [floor art FPV](floor-art-fpv.md) — the painter does not change `ExplorationGridMetrics`.

| Rule | Value |
|------|--------|
| Grid | 20×20 at launch strata floors |
| Storage | **North-up** row array (`k_RowsNorthUp[0]` = north edge) |
| Game `y` | **0 = south** — `y = GridSize - 1 - row` |
| Index | `x + y * width` (`ExplorationFloorLayout.ToIndex`) |

Same as [archive — s1_B1F ASCII](../archive/mvp1-s1-floor-layouts-draft.md#s1_b1f--outskirts-gate-intro--gate) and `Tools/layout_grid_check.py` (draft reference until layout lock).

## ASCII symbols

| Char | Walkable | Tile flags / notes |
|------|----------|-------------------|
| `#` | No | Wall |
| `X` | No | Tutorial / script blocker |
| `.` | Yes | Open floor |
| `C` | No | **Chest** — `ChestConfig` (`chestId`, facing for FPV art, fixed `itemId` + `quantity`); party **cannot enter** the cell; **Interact** (`Space` / `Z`) from an orthogonally adjacent walkable cell while **facing** the chest ([#105](https://github.com/miramocha/griddungeon-game/issues/105)) |
| `G` | Yes | **Gather** — `HasGatherNode`; instant loot at launch on interact when on cell ([ADR 014](../decisions/014-mvp1-exploration-map.md)) |
| `H`, `E`, `M`, `S` | Yes | **Role markers** — spawn start (`S`), story gate (`M`), hub return (`H`), inter-floor exit (`E`); direction + floor target live on **exit bindings** in the cell inspector ([#107](https://github.com/miramocha/griddungeon-game/issues/107), [ADR 040](../../decisions/040-floor-exit-topology-graph.md)). **`H` and `S`/`M` are unique per floor**; **multiple `E` per floor** allowed — one `FloorExitLink` row per `H`/`E` cell. **`H`** and **`S`** (B1F) expose **Target facing** in Edit Cell (same rotate UX as **`E`**); hub **`Direction`** stays internal **`Up`** — not authorable. Spawn facing persists on `ExplorationFloor.partyEntrySpawnFacing`. |

**Walkability (shipped):** impassable `#`, `X`, and `C` only; all other palette symbols walkable — same rule as `FloorEditorLayoutSymbols` export ([#105](https://github.com/miramocha/griddungeon-game/issues/105), [#77](https://github.com/miramocha/griddungeon-game/issues/77)).

## Markers vs parallel pin store ([#107](https://github.com/miramocha/griddungeon-game/issues/107))

| Layer | Authority |
|-------|-----------|
| **Grid char** | Authoring truth for entry/exits — `S` / `M` / `H` / `E` on cells |
| **Painter UI** | Marker palette tools write those chars; exit bindings (direction, target floor, spawn) in cell inspector; coord summary **derived** from grid scan on refresh |
| **`ExplorationFloor` asset** | Runtime exploration reads serialized coords + tiles — **not** ASCII scan at play time |
| **Anti-pattern** | Parallel pin coord store (e.g. `FloorEditorPinState`) — removed; grid is the only painter state for markers |

When gate and hub entrance share a cell (canonical B1F), only `H` appears on the grid; Apply sets `partyEntryGate` to the `H` cell when `M` is absent. Hub return is **never** authored via `E` — use `H` only.

## Multi-exit markers and topology graph

**Target model ([ADR 040](../../decisions/040-floor-exit-topology-graph.md)):** scalar `stairsUp` / `stairsDown` are replaced by **`FloorExitLink[]`** on each `ExplorationFloor`. Painter and optional Graph Toolkit topology compile into the same array.

| Layer | Authority |
|-------|-----------|
| **Grid `^` / `v`** | **Where** each exit sits — multiple markers per floor |
| **Painter Save** | Emits one `FloorExitLink` per binding (`exitId`, `cell`, `direction`, full `target*`) from **Edit Cell** inspector or paint markers |
| **Floor Connector** (editor-only, [#253](https://github.com/miramocha/griddungeon-game/issues/253), [ADR 041](../../decisions/041-floor-connector-toolkit-wiring.md)) | **Compile** replaces full `exitLinks[]` per `locationId` (cells + targets) — **no runtime graph** |
| **`ExplorationFloor` asset** | Runtime reads `exitLinks[]` only |

**Orthogonal:** quest / flag **gating** of pins and events is [ADR 031](../../decisions/031-floor-event-pin-condition-graph.md) — not fields on exit links. Campaign **hub entry** spawn stays in per-stratum policy ([ADR 025](../../decisions/025-campaign-exploration-target.md)).

**Launch migration:** S1 floors keep one `^` and one `v` each; migration ticket [#250](https://github.com/miramocha/griddungeon-game/issues/250) compiles today’s scalar coords into link rows before multi-exit painter UI ([#252](https://github.com/miramocha/griddungeon-game/issues/252)).

## Workflow

1. **GridDungeon → Content → Floor Editor** (UI Toolkit) — header **mode toolbar** (Paint Wall, Edit Cell, FOE, Events, Floor Data, Elevation, Random Encounters) + scrollable tools pane; **New** creates an `ExplorationFloor` under `Assets/Content/Floors/`; **Paint Wall** for bulk `#`/`.` layout, **Border walls** / **Fill all walls** / **Fill all floors**, and Generate/Transmute maze tools; **Edit Cell** for per-cell types (markers, chest, gather, blocker) and exit targets; **FOE** for spawn placement and metadata (patrol paths on asset for v1); **Events** for exploration story-event triggers (parallel store — not an ASCII `!` on the grid); **Floor Data** for **Location id** and **Floor id**; **Elevation** for per-cell elevation steps, step units, blocky terrain, and randomize/clear; **Random Encounters** assigns a shared `RandomEncounterTableDefinition` id on the floor (rate + weighted groups live on the table asset).
2. **New:** pick path (default `NewExplorationFloor.asset`; rename to e.g. `s1_B5F` before save if desired) → asset created with parsed Location / Floor id → session seeded with **Border walls** on a 20×20 grid → paint → **Save** writes layout to disk.
3. **Paint Wall:** drag-fill walls and floors; use **Border walls**, **Fill all walls**, or **Fill all floors** for bulk layout; use **Maze** panel below palette to Generate or Transmute a layout.
4. **Floor Data:** edit **Location id** and **Floor id**; use header row **Content database** + **Register** (under New / Load / Save) to add the floor to a database list; **Save** persists the asset file (grid layout still comes from Paint Wall / Edit Cell).
5. **Elevation:** edit **step units**, **blocky terrain**, **generation mode** (PerCell, PlateauStamp, FixedChunk, FractalNoise, RidgedNoise), seed/min/max, then **Apply** (current seed), **Randomize** (new seed + apply), or **Clear**; map pane shows a **step heatmap** (blue low → amber high) with **step numbers** on each cell while this tab is active. **FractalNoise** / **RidgedNoise** use seeded fractal value noise (octaves + redistribution) before quantizing to integer steps. **Seal cliff walls** (manual): after elevation is applied, converts walkable cells to `#` when cardinal step delta exceeds **Max walkable step delta** (default 2 — e.g. 0↔2 walkable, 0↔4 sealed). **Seal cliff cell** picks **Higher step** (default) or **Lower step** on each steep edge; skips role markers (`S`/`M`/`H`/`E`), gather, and chest. **Save** writes `cellElevationSteps`, `elevationStepUnits`, and `useBlockyTerrain` on the floor asset (layout `#` changes commit with the rest of the grid on Save). Algorithm detail: [elevation-generation.md](elevation-generation.md).
6. **Edit Cell:** select a cell → **Cell type** for `S` / `M` / `H` / `E`, chest, gather, blocker, or single-cell wall/floor fixes → set **Target facing** on `H`, `S` (B1F), and `E` (floor targets) via enum + rotate row; grid shows a facing badge on those markers in Edit Cell → **Save** to `Assets/Content/Floors/s1_B*n*F.asset`.
7. **FOE mode:** select a walkable cell, click **Add FOE** to create a spawn (or select an existing spawn to edit). Edit fields in the side panel, then **Save**. Existing patrol paths load from the asset unchanged; waypoint editing is not in the Floor Editor yet. Grid **F** badges and red spawn borders appear **only in FOE mode** (hidden in Paint Wall, Edit Cell, Events, Floor Data, Elevation, Random Encounters, and pick-spawn).
8. **Events mode:** select a walkable cell, click **Add Event**, pick an existing `StoryEventDefinition` id from **ContentDatabase**, then **Save**. Triggers persist on `ExplorationFloor.m_storyEventTriggers[]` (cell + `storyEventId` + optional flag arrays); the underlying tile stays walkable (`.`, `G`, etc.) — not an ASCII `!` on the painted grid. Grid **!** badges and purple borders appear **only in Events mode**. Runtime exploration map still shows the `!` marker at authored cells when the trigger is pending. Prerequisite flag authoring on triggers is YAML / inspector for now (no full Events-mode flag UI yet).
9. **Random Encounters mode:** pick or create a `RandomEncounterTableDefinition` in the side panel (table **ObjectField**, **New**, **Open**). Floor asset stores **`randomEncounterTableId` only** — edit **base rate** and **weighted encounter groups** on the table asset (UITK inspector mirrors Loot Table pattern). **Save** writes the floor assignment; register table + floor rows via header **Content database** + **Register**. Runtime: `ExplorationPhaseController` loads table from `ContentDatabase`; S1 Act 1 B1F movement tutorial forces rate **0** via `S1CampaignResolver.GetEffectiveEncounterRate` ([enemy-roster § FOE vs random](../03-content/enemy-roster.md#foe-vs-random-placement-per-floor)).
10. **Target spawn picker:** with an **`E`** cell selected in Edit Cell, set **Target = Floor** and choose the destination floor key, then **Pick on target floor**. The map pane loads that floor asset (read-only); click a walkable cell and **Confirm spawn** to stage **Target spawn X/Y** on that exit. **Cancel pick** restores the source floor grid without losing unsaved edits. Exit field edits stage immediately; **Save** writes bindings to the asset.
11. **3D walls (optional):** open `Assets/Scenes/Floors/s1_B*n*F.unity` → **Floor Art Grid → Populate Wall Blocks** → save scene ([floor-art-fpv.md](floor-art-fpv.md)).
12. Play Mode: **DevBootstrap F2** + `MapView` / exploration movement. **Save during Play Mode** refreshes runtime walkability via Floor Editor sync; exit/re-enter Play Mode after Edit Mode Save.

**Create Dev Bootstrap** registers launch floors in `ContentDatabase` and **does not overwrite** existing `ExplorationFloor` assets ([#107](https://github.com/miramocha/griddungeon-game/issues/107)). Edit or reset layouts in **GridDungeon → Content → Floor Editor** — destructive repaints overwrite the committed floor asset.

Layout path validation: `Tools/layout_grid_check.py` / [stratum-floor-layout-check](https://github.com/miramocha/griddungeon-game/tree/main/.cursor/skills/stratum-floor-layout-check) (CI / regression — not in Floor Editor window).

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

**Later (idea):** quest- and flag-gated pins / triggers — compile from a Graph Toolkit floor graph to `ExplorationFloor` rules; see [ADR 031](../../decisions/031-floor-event-pin-condition-graph.md). Launch ships static pins + C# triggers; gating graph is not required for [#109](https://github.com/miramocha/griddungeon-game/issues/109).

**Exit topology (parallel track):** stratum **connectivity graph** compiles `FloorExitLink[]` — see [ADR 040](../../decisions/040-floor-exit-topology-graph.md) and [game #249](https://github.com/miramocha/griddungeon-game/issues/249). Distinct from ADR 031 event gating.

## Related

- [04-tech-notes — Map authoring](04-tech-notes.md#map-authoring--hud-adr-002)
- [05-class-design — `FloorEditorWindow`](05-class-design.md)
- [ADR 040 — Floor exit topology graph](../../decisions/040-floor-exit-topology-graph.md)
- [ADR 041 — Floor Connector (GTK wiring)](../../decisions/041-floor-connector-toolkit-wiring.md)
