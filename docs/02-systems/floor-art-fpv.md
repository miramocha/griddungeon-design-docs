---
tags:
  - path/docs/02-systems
  - type/system
  - scope/required
  - status/shipped
  - domain/exploration
---
# Floor art — FPV corridor props

**Scope:** [Required](../00-release-scope.md#required-first-playable)

**Implementation:** [#102](https://github.com/miramocha/griddungeon-game/issues/102) (wall blocks + runtime load, shipped) · **Populate v1.5:** [#172](https://github.com/miramocha/griddungeon-game/issues/172) (walkable hallway / corner / floor) · **TWC runtime (shipped):** [Epic #344](https://github.com/miramocha/griddungeon-game/issues/344) ([#345](https://github.com/miramocha/griddungeon-game/issues/345) spike → [#346](https://github.com/miramocha/griddungeon-game/issues/346) adapter → [#347](https://github.com/miramocha/griddungeon-game/issues/347) elevation; docs [#55](https://github.com/miramocha/griddungeon-design-docs/issues/55))  
**Follows:** [Editor floor art grid rig #92](https://github.com/miramocha/griddungeon-game/issues/92)  
**Not:** [Map cell art](map-cell-art.md) (2D HUD `MapView`) or [Floor Editor](floor-editor.md) (logic tiles / FOE / export)

## Summary

Artists author **3D corridor props** on the same **20×20** grid as exploration logic (`ExplorationFloor`). **`FloorArtGrid`** (Editor) aligns overlays and snap to `ExplorationWorldSpace.CellCornerToWorld` (10 u/cell). This spec adds:

1. **Populate** — inspector list of wall/block prefabs + button to place one random full-cell prop on each **non-walkable** logic cell (with skips).
2. **Runtime presentation** — instantiate stratum template or custom floor art prefab during exploration so Play Mode shows authored meshes (not per-cell spawn from `ExplorationFloor` in v1).

Logic, collision, map reveal, and encounters remain **`ExplorationFloor` + Core** only ([ADR 002](../../decisions/002-mapping-model.md)).

## TileWorldCreator runtime path

**Shipped:** [Epic #344](https://github.com/miramocha/griddungeon-game/issues/344), [ADR 043](../../decisions/043-twc-fpv-presentation-layer.md). **Setup:** [TWC default notes](../04-dev/twc-default-notes.md).

Replace **3D FPV wall/walkable/ground mesh** generation with [TileWorldCreator v4](https://giantgrey.gitbook.io/tileworldcreator-v4-documentation/api) at **runtime** when `FloorArtStratumDefaults.MeshBackend` is `TileWorldCreator`. Installations **without** the TWC asset use **`MeshBackend = Default`** (built-in prefab populate + blocky terrain/cube) — always supported, not deprecated. `ExplorationFloor` stays layout authority; adapter translates walkable / solid cells to TWC blueprint layers (`AddCellsToLayer` → `GenerateCompleteMap`).

| Topic | Decision |
|-------|----------|
| Scope | **FPV 3D only** — not UITK minimap ([map cell art](map-cell-art.md)) |
| Workflow | Runtime from floor SO — not edit-time-only bake |
| Grid | TWC sub-grid (default **2×2** per logic cell, **5** u TWC cell) on **21×21** floors — match `ExplorationGridMetrics` (**10** u/logic cell) |
| Interactables | Chest/door populate on `FloorArtGrid` lists (Phase 1 path; optional TWC Objects layer later) |
| Elevation | `cellElevationSteps` → runtime `Level_sN` layers ([#347](https://github.com/miramocha/griddungeon-game/issues/347)); see [twc-default-notes § Elevation bridge](../04-dev/twc-default-notes.md#elevation-bridge-347) |
| Built-in populate | `PopulateWallBlocks` / `PopulateWalkableTiles` / blocky terrain when `MeshBackend = Default` |
| Floor Editor | **No required UI change** — FPV Preview for TWC: [#371](https://github.com/miramocha/griddungeon-game/issues/371); mesh retirement: [#370](https://github.com/miramocha/griddungeon-game/issues/370) |
| Map authority | **`ExplorationFloor` → TWC only** — do not use TWC CA/BSP/maze generators as gameplay layout source |
| Mesh backends | **`Default`** (built-in, all installs) \| **`TileWorldCreator`** (optional plugin asmdef) |
| Plugin asmdef | **`GridDungeon.FloorArt.TileWorldCreator`** — omit folder if no asset; Runtime never references vendor TWC asm |

**Types:** `FloorArtMeshBackendKind` (`Default` \| `TileWorldCreator`); `IFloorArtMeshBackend` + registry in `GridDungeon.Runtime`; `FloorArtDefaultMeshBackend` (built-in); TWC impl in optional asmdef `GridDungeon.FloorArt.TileWorldCreator` (`FloorArtTwcMeshBackend`, `FloorArtTwcWalkableMaskBuilder`, `FloorArtTwcElevationTranslator`, `FloorArtTwcHost`).

**Not replaced:** `FloorArtPresenter` lifecycle, `FloorArtCatalog`, `CellElevationGenerator` (Floor Editor), UITK `MapGridPaintCoordinator`.

**Out of epic #344:** Built-in mesh path retirement when all strata on TWC — [#370](https://github.com/miramocha/griddungeon-game/issues/370) (optional, standalone).

## Context

| Layer | Authority | Presentation |
|-------|-----------|----------------|
| Grid rules | `ExplorationFloor` SO, layout builders | — |
| 2D map HUD | `MapSystem` + `MapView` | Sprites / composite walls ([#38](https://github.com/miramocha/griddungeon-game/issues/38)) |
| FPV dungeon | Same walkability as SO | Stratum template prefab or per-floor custom prefab under `FloorArtCatalog` |

**Grid model:** `cell.X` → world **X**, `cell.Y` → world **Z**, north **+Z**; anchor = **cell corner** `(x, 0, z)` ([02 — Dungeon navigation](../02-dungeon-navigation.md)). When the floor asset has `cellElevationSteps`, party/camera **Y** follows step × `elevationStepUnits` via `DungeonExplorer` — not the flat `y = 0` default.

**World scale (at-launch FPV):** Logic grid stays **20×20** cells; each cell is **`10` Unity world units** on XZ (`ExplorationGridMetrics.WorldUnitsPerCell` in game `GridDungeon.Core`). Corner `(0,0)` → world `(0, 0, 0)`; cell `(3, 4)` → `(30, 0, 40)`. FPV eye height default **3** units (`0.3 × cell size`). Floor art prefabs and preview use **`FloorArtGrid.Cell Size = 10`**; legacy assets authored at **1** unit/cell get prop positions expanded at runtime via `FloorArtLayoutSpacing.Apply` (populate + hand-placed generated props only).

**Prior art:** [#92](https://github.com/miramocha/griddungeon-game/issues/92) shipped `FloorArtGrid`, template prefab workflow, walkability/pin gizmos, **Snap Selected To Grid**. `DungeonSceneHost.RenderCell` remains a stub — runtime FPV is **prefab instantiate**, not blobber cell rendering.

## Locked decisions (Populate v1)

| Topic | Decision |
|-------|----------|
| Target cells | `IsWalkable == false` on assigned `ExplorationFloor` |
| Skip | Layout symbol **`X`** (story / tutorial blocker cells) — hand-place art later |
| Prefab model | **One full-cell** block per targeted cell |
| Position | **Cell center** — `FloorArtGrid.GridToCellCenterWorld(x, y)` (center-pivoted prefab) |
| Rotation | **Prefab default** only (random Y spin planned; requires center pivot) |
| Prefab list | Serialized `GameObject[]` (prefab references); **uniform** random |
| Re-run Populate | Destroy only objects marked **auto-generated**, then fill again |
| Auto-generated marker | `FloorArtGeneratedProp` component (or equivalent) on instantiated instances |
| Undo | `Undo.RegisterCreatedObjectUndo` / destroy via Undo on clear |
| Parent | All spawned instances under **`Props`** child of `FloorArtRoot` |
| Lighting / volumes | Under **`FloorArtRoot`** (`Lighting/`, `Volumes/`) — not scene root; mounts with art at runtime ([game README](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scenes/Floors/README.md#lighting-and-volumes)) |
| Later (v1.5+) | Walkable hallway / corner / floor populate ([#172](https://github.com/miramocha/griddungeon-game/issues/172)); gather (`G`), chest (`C`), stairs/entry pins, key markers; modular edge walls; seeded/weighted picks |

## Locked decisions (Populate v1.5 — walkable tiles)

**Tracks:** [game #172](https://github.com/miramocha/griddungeon-game/issues/172). **Complements** Populate v1 wall blocks on `#` — does **not** replace them.

| Topic | Decision |
|-------|----------|
| Wall blocks (`#`) | Unchanged — [#102](https://github.com/miramocha/griddungeon-game/issues/102) **Populate Wall Blocks** |
| Target cells | `IsWalkable == true` on assigned `ExplorationFloor` |
| Classification | 4-bit cardinal mask: which N/E/S/W neighbors are walkable |
| Kinds | `HallwayStraight` (two opposite walkable neighbors), `HallwayCorner` (two adjacent), `FloorDefault` (0, 1, 3, or 4 walkable neighbors — open room, dead-end, T, cross until dedicated art) |
| Position | **Cell center** — `GridToCellCenterWorld` (center-pivoted prefab, 10 u/cell) |
| Rotation | **Y** from mask: straight 0° (N+S) / 90° (E+W); corner 0°/90°/180°/270° for NE/SE/SW/NW pairs |
| Prefabs | Three `GameObject[]` lists on `FloorArtGrid` (hallway, corner, floor); **uniform random** per cell like wall blocks — **not** merged into `m_wallBlockPrefabs` |
| Skip | `HasGatherNode` (`G`); story **`X`** is non-walkable (wall pass only); stairs/key markers manual (future) |
| Marker / clear / Undo | Same as v1 — `FloorArtGeneratedProp`, **Clear Generated Props**, Undo on create/destroy |
| First art | Dev primitives (menu-created cubes/planes); swap for modular kit later |
| Not in v1.5 | Modular N/E/S/W edge segments from `GetSolidEdges` / runtime `WallMask` — FPV v2 |

### Walkable classification (reference)

Neighbor bitmask: `N=1`, `E=2`, `S=4`, `W=8` (walkable neighbor only).

| Mask pattern | Kind | Rotation |
|--------------|------|----------|
| N+S or E+W | HallwayStraight | 0° if N+S; 90° if E+W |
| Two adjacent (L-turn) | HallwayCorner | From opening pair (NE → 0°, etc.) |
| Other | FloorDefault | 0° |

### Editor workflow (v1.5)

1. Assign `ExplorationFloor`; enable **Show Walkable** + **Show Blocked** overlays.
2. **Clear Generated Props** (when re-running either pass).
3. **Populate Wall Blocks** — `#` cells (unchanged).
4. **Populate Walkable Tiles** — `.` corridor / room cells.
5. Optional: **Populate All** (Clear → wall blocks → walkable → chests → doors) in one Undo group.

### Corridor doors (`D`) — FPV populate

| Item | Rule |
|------|------|
| Prefab slot | `FloorArtGrid.Door Prefab` (single template like chest) |
| Editor | **Populate Doors** + dev menu **Create Dev Door Template** |
| Runtime | `FloorArtDoorProp` + `FloorArtDoorResolver`; `PopulateDoors` on floor load |
| Open animation | C# fires Animator **`Open`** trigger once |
| Close animation | **Animator-owned** (`DoorOpening` → `DoorClosing` → `DoorClosed`); cosmetic after `IsInteracted` |
| Open-complete | Animation event **`NotifyOpenComplete`** on open clip (poll fallback like chest) |
| Save revisit | Gameplay-open doors call `ApplyAlreadyOpen()` → closed idle mesh while cell stays passable |

## Locked decisions (Runtime v1)

| Topic | Decision |
|-------|----------|
| Source | **Authored floor art prefab** (stratum template or custom `FloorArtRoot` per floor key) |
| Not in v1 | `DungeonSceneHost` spawning wall prefabs per cell from `ExplorationFloor` at runtime |
| Load trigger | `FloorTransitionPresenter` → `FloorArtPresenter.LoadFloorArt` when floor commits |
| Unload | Previous floor art instance destroyed on floor change or leaving exploration |
| Catalog | `FloorArtCatalog`: `floorKey` → **DefaultTemplate** (stratum prefab + runtime build) or **CustomPrefab** (`FloorArtRoot` prefab) |
| Missing art | Log warning; exploration continues (map + movement); FPV may be empty |
| Alignment | Art root at world origin; corner math matches `ExplorationWorldSpace` / `FloorArtGrid.GridToWorld` |
| Cell size | **`10`** world units per logic cell on new floors; `FloorArtLayoutSpacing` expands legacy **1** u/cell **generated** props at load |
| In-flight load | Cancel pending load when floor changes before mount completes |
| Build | Shipped custom prefabs referenced from `FloorArtCatalog`; stratum template prefab on stratum defaults — **no per-floor scenes in Build Settings** |

## Custom floor art prefab (hero floors)

| Step | Action |
|------|--------|
| Create | **GridDungeon → Floor Art → Templates → Create Custom Floor Art Prefab…** → `{floorKey}.prefab` under `Assets/Content/FloorArt/Prefabs/Floors/` |
| Author | Assign `ExplorationFloor` on **Floor Art Grid**; populate / hand-place under **Props**; **Setup Default Lighting** |
| Register | Accept catalog prompt or add `FloorArtCatalog` row: **Presentation = Custom Prefab**, **Floor art prefab** = asset |
| Runtime | `FloorArtPresenter` instantiates prefab; logic still from `ExplorationFloor` SO only |

Most floors skip this — use **Default template** + TWC/runtime populate with no catalog row.

## Editor — Populate workflow

1. Open **FPV preview** (**GridDungeon → Floor Art → Preview → Open Preview For Floor…**) or edit a **custom floor art prefab** (`Assets/Content/FloorArt/Prefabs/Floors/{floorKey}.prefab`).
2. Assign `ExplorationFloor` on **Floor Art Grid**; enable **Show Blocked Overlay** to verify alignment.
3. Assign **Wall Block Prefabs** list on `FloorArtGrid`.
4. Click **Populate Wall Blocks** (name TBD).
5. Tool iterates `x ∈ [0, width)`, `y ∈ [0, height)`; for each cell:
   - If not walkable **and** not a populate skip → pick random prefab, `Instantiate` under `Props` at cell center, add `FloorArtGeneratedProp`.
6. Hand-edit: move/delete individual props; use **Snap Selected To Grid** for tweaks.
7. Re-run Populate → only removes objects with `FloorArtGeneratedProp`, then regenerates.

### Populate skip rules (v1)

| Rule | Rationale |
|------|-----------|
| `IsWalkable == true` | Walkable floor — walls only for v1 |
| Layout symbol **`X`** | Story/tutorial blocker (e.g. B1F `(10,13)`); impassable but not a generic wall mesh |
| (Future) `FloorArtKeyCellMarker` | Scripted pins — manual art |
| (Future) Gather / stairs pins | Separate auto-fill passes |

**Implementation note:** Skip for `X` can use campaign constants where they exist (e.g. `S1CampaignResolver.B1FBlockerCell`) **and** treat any authored tile that maps from symbol `X` in layout builders as skipped when a symbol lookup is available; otherwise maintain a small static skip list per floor until painter [#75](https://github.com/miramocha/griddungeon-game/issues/75) stores symbol on `FloorTileData`.

## Runtime — Load authored art

```mermaid
sequenceDiagram
    participant EPC as ExplorationPhaseController
    participant Cat as FloorArtCatalog
    participant DV as DungeonSceneHost
    participant Prefab as Floor art prefab

    EPC->>EPC: Load ExplorationFloor (logic)
    EPC->>Cat: Resolve(floorKey)
    alt art registered
        Cat->>DV: LoadFloorArt(prefab)
        DV->>Prefab: Instantiate under DungeonSceneHost
    else missing
        EPC->>DV: Clear / warn
    end
```

- **Prefab instance** under `DungeonSceneHost` transform — stratum template or catalog **CustomPrefab** row.
- **Combat:** `CombatPhaseController` hides `DungeonSceneHost` (existing); floor art root hides with it.
- **Alignment:** Art root at world origin `(0,0,0)`; same as Editor preview and prefab authoring.

## Floor transitions

**Authority:** [ADR 032](../../decisions/032-floor-transition-vignette-mvp1.md) · [floor transition](floor-transition.md)

Shipped **floor transition vignette** (black void + 3D threshold prop + Cinemachine) for stairs and hub stratum entry. Floor art loads **only** through `FloorTransitionPresenter`, in order:

1. Transition starts (`FloorTransitionPresenter`; input/HUD gated via `ExplorationPresentationGate`).
2. `UnloadFloorArt()` for the leaving floor — await complete.
3. Door beat plays (fade from black → vignette → fade to black on `BeatEndFired`).
4. **Commit** delegate (map/foes; spawn per caller — hub spawns in commit before reveal).
5. `LoadFloorArt(enterKey)` under black — await mount or fail.
6. FPV rig attach at spawn — fade in to exploration.

**Authoring / QA:** [authoring floor transition beats](../04-dev/authoring-floor-transition-beats.md). `NotifyThreshold` does **not** commit floor in the current presenter.

**Design rules (locked):**

| Rule | Why |
|------|-----|
| **Single owner** (`FloorTransitionPresenter`) per floor change | Avoid `LoadFloorArt` from both transition and `ExplorationPhaseController` on the same frame. |
| **No overlapping loads** | Prevents stale floor art and wrong mounted `FloorArtRoot`. |
| **Play Mode tests** via `FloorTransitionPlayModeTests` | Transition enter → unload → commit → load; not raw double `LoadFloorArt` on one frame. |
| **Fade-only fallback** if beat asset missing | Floor change must still complete. |

## Out of scope (this feature)

| Item | Track separately |
|------|------------------|
| Modular N/E/S/W wall pieces from `WallMask` | FPV v2 or shared with map art rules |
| Auto-place gather, doors, stairs meshes | Follow-up populate modes (gather skipped in [#172](https://github.com/miramocha/griddungeon-game/issues/172)) |
| `DungeonSceneHost.RenderCell` blobber / per-cell swaps | Optional later |
| Replacing `ExplorationFloor` collision from meshes | Never — logic SO only |

## Implementation checklist (game repo)

### Phase A — Editor Populate

- [x] `FloorArtGrid`: serialize `GameObject[] m_wallBlockPrefabs`
- [x] `FloorArtGeneratedProp` marker type
- [x] `FloorArtPopulate` static/editor service: enumerate cells, skip rules, instantiate, Undo
- [x] `FloorArtGridEditor`: **Populate Wall Blocks** + **Clear Generated Props** buttons; validation (floor assigned, list non-empty)
- [x] Update `Assets/Scenes/Floors/README.md`

### Phase C — Editor Populate v1.5 (walkable tiles) — [#172](https://github.com/miramocha/griddungeon-game/issues/172)

- [x] `FloorArtWalkableTileClassifier` + `GetWalkableTilePlacements` (Core / planner)
- [x] `FloorArtGrid`: hallway / corner / floor prefab slots
- [x] `FloorArtPopulateUtility.PopulateWalkableTiles` + `FloorArtGridEditor` buttons (+ **Populate All**)
- [x] Dev prefabs menu + `FloorArtPopulateTests` (classifier, gather skip)
- [x] Game `Assets/Scenes/Floors/README.md` workflow

### Phase B — Runtime load

- [x] `FloorArtCatalog` SO under `Assets/Content/FloorArt/`
- [x] `FloorArtPresenter`: load/unload by `floorKey` under `DungeonSceneHost`
- [x] `ExplorationPhaseController`: load after floor SO ready; cancel in-flight prefab mount on floor change
- [x] S1 floors use shared stratum template prefab — no per-floor Build Settings entries
- [ ] DevBootstrap F2 manual: visible walls match blocked overlay

## Acceptance criteria

1. With `s1_B1F.asset` assigned, **Populate** fills every `#` wall cell with a prefab from the list at the cell center; cell `(10,13)` (**X**) has **no** generated prop.
2. Second **Populate** removes only generated props, not hand-placed props without the marker.
3. Play Mode on B1F after art is registered: player sees authored wall meshes; movement/collision unchanged from SO.
4. Switching floors unloads prior art; no duplicate roots.
5. No new logic in player assemblies that mutates `ExplorationFloor` tiles.

## Test plan

### Automated

- [x] Edit Mode: `FloorArtPopulateTests` — mock 3×3 floor, skip list, corner math parity (`ExplorationWorldSpace` vs planner), `FloorArtLayoutSpacing.Apply`
- N/A Play Mode batch (Editor open policy)

### Manual (Editor)

1. FPV preview or custom prefab + blocked overlay → **Populate** → compare outer ring to red gizmo cells; confirm no prop at tutorial **X**.
2. Hand-place extra prop under `Props` → **Populate** again → hand prop remains.

### Manual (Play Mode)

- **Scene:** `DevBootstrap.unity` — **F2** exploration on `s1_B1F`
- **Expected:** FPV shows populated corridor art; map still 2D schematic; combat **F3** hides FPV

### Spec / ADRs

- [ADR 002](../../decisions/002-mapping-model.md), [ADR 001](../../decisions/001-grid-movement.md), [02 — Dungeon navigation](../02-dungeon-navigation.md)

## Related docs
- [Floor transition vignette](floor-transition.md) · [ADR 032](../../decisions/032-floor-transition-vignette-mvp1.md)
- [04-tech-notes — Map authoring](../04-tech-notes.md#map-authoring--hud-adr-002)
- [Exploration UI — DungeonSceneHost](exploration-ui.md#phase-system-vs-ui-visibility)
- Game: `Assets/Scenes/Floors/README.md`, [#92](https://github.com/miramocha/griddungeon-game/issues/92), [#102](https://github.com/miramocha/griddungeon-game/issues/102), [#172](https://github.com/miramocha/griddungeon-game/issues/172) (populate walkable tiles), [#344](https://github.com/miramocha/griddungeon-game/issues/344) (TWC runtime epic)
