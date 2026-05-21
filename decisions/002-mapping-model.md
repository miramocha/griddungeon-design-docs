# ADR 002 — Mapping Model

**Status:** Accepted (amended 2026-05-21)  
**Aligns with:** *Etrian Odyssey* presentation; **without** manual drawing tools

## Context

EO traditionally uses player-drawn walls. **Drawing tools are out of scope** for this project — mapping must be fully driven by exploration events.

## Decision

1. **Auto-chart floor** on every cell the party enters.
2. **Auto-chart walls** when party bumps a blocked side or when wall edges are revealed entering a cell (implementation detail in tech notes).
3. **Auto-chart doors, stairs, chests, gather nodes** on interact/use.
4. **FOE icons** auto-placed when visible; position updates on step-patrol ([ADR 003](003-foe-step-patrol.md)).
5. **Map UI is read-only** — pan/zoom only; no toolbar.
6. **Map persists** on party wipe for that stratum.

## Rejected / out of scope

| Option | Why |
|--------|-----|
| Manual wall/door/icon drawing | Explicitly excluded from project scope |
| Bump-assist one-click stamp | Was a drawing aid; redundant with auto-wall on bump |
| Free-text map notes | Annotation tool; cut with drawing scope |
| Full floor reveal on entry | No fog tension |

## Consequences

- Save stores `revealedMapLayer` per floor (bitmasks + feature flags), not player strokes
- No map tool tutorial; tutorial teaches **reading** map + FOE icons
- EO "mapping as skill" shifts to **pathfinding / FOE routing** rather than pen accuracy
- Floor scenes include a **map proxy rig** (simple geometry) co-located with FPV layout for editor preview; FPV art is **not** drawn into the minimap

## Technical notes (Unity) — map proxy + minimap camera

**Goal:** EO-style auto-map in the HUD without rendering the FPV dungeon mesh into the minimap.

### Map proxy rig (authoring)

| Piece | Rule |
|-------|------|
| **Geometry** | Per-cell **cubes** (or quads) with **flat unlit colors** — floor, wall segment, door, stairs, etc. |
| **Layer** | **`MapProxy`** only (project layer name; all proxy objects on this layer) |
| **Placement** | **Same grid** as exploration collision / `DungeonView` — designers **overlap** proxy and FPV layout in the Editor and see alignment in Scene view |
| **FPV environment** | Walls, props, lighting on **other layers** (`Default`, dungeon/FPV layers) — **excluded** from minimap camera culling mask |

Proxies are **schematic**, not a second art pass: solid colors, no PBR. Optional shared prefab per cell type (`MapCell_Floor`, `MapCell_WallN`, …).

### Minimap camera → HUD

1. **Orthographic camera** (north-up, 1 unit = 1 cell) renders **only `MapProxy`** into a `RenderTexture`.
2. **Fog / reveal:** `MapSystem` drives proxy visibility (enable renderer, material alpha, or shader mask from `Visited` / `WallMask`) — state stays in Core; proxies are view targets.
3. **UI Toolkit** shows the RT in the exploration HUD; pan/zoom on the UI element and/or ortho size ([ADR 014](014-mvp1-exploration-map.md)).
4. Minimap camera **enabled while map is visible** (continuous RT); optional on-demand render when map hidden for perf.

### Party / FOE markers

**Party arrow** and **FOE icons** are **flat quads** on `MapProxy`, parented to **`PartyPose` / `FOEPose`** at `(x, y, level)` (same pipeline as wall cubes). Minimap camera renders them into the RT; UI Toolkit displays the live RT ([ADR 019](019-floor-verticality.md) — map shows **current `level`** slice in MVP1).

### HUD

UI Toolkit **`Background.FromRenderTexture`** (or equivalent) on the map panel. While the minimap camera is enabled, the texture **updates every frame** — no manual rebake per patrol step.

### Editor preview

- Scene view: proxy cubes + FPV geometry visible together for layout QA.
- Play Mode / minimap: only **minimap camera** output reaches the HUD; player never sees proxy cubes in the main FPV view (FPV camera excludes `MapProxy`, or proxies are disabled/hidden for main camera).

### Authority (unchanged)

`MapRevealCalculator` + `MapSystem` own reveal rules and save data. Proxies and RT are **presentation** only — see [04 — Tech notes § Map system](../docs/04-tech-notes.md#map-system).

### Rejected for this pipeline

| Option | Why |
|--------|-----|
| Minimap renders full FPV meshes | Cost, lighting clutter, wrong scale for EO-style chart |
| Player-editable proxy geometry | Read-only map (decision 5 above) |
| Saving `RenderTexture` to disk | Save bitmasks only |

## Related

- [Mapping system](../docs/02-systems/mapping.md)
- [02 — Dungeon navigation](../docs/02-dungeon-navigation.md)
- [ADR 019 — Floor verticality](019-floor-verticality.md)
