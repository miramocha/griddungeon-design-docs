# ADR 002 � Mapping Model

**Status:** Accepted (amended 2026-05-21)  
**Aligns with:** *Etrian Odyssey* presentation; **without** manual drawing tools

## Context

EO traditionally uses player-drawn walls. **Drawing tools are out of scope** for this project � mapping must be fully driven by exploration events.

## Decision

1. **Auto-chart floor** on every cell the party enters.
2. **Auto-chart walls** when party bumps a blocked side or when wall edges are revealed entering a cell (implementation detail in tech notes).
3. **Auto-chart doors, stairs, chests, gather nodes** on interact/use.
4. **FOE icons** auto-placed when visible; position updates on step-patrol ([ADR 003](003-foe-step-patrol.md)).
5. **Map UI is read-only** � pan/zoom only; no toolbar.
6. **Map persists** on party wipe for that stratum.

## Rejected / out of scope

| Option | Why |
|--------|-----|
| Manual wall/door/icon drawing **in-game** | Explicitly excluded from project scope |
| Bump-assist one-click stamp | Was a drawing aid; redundant with auto-wall on bump |
| Free-text map notes | Annotation tool; cut with drawing scope |
| Full floor reveal on entry | No fog tension |
| **Minimap camera ? `RenderTexture` as primary HUD** | Superseded by floor painter + 2D map ([amendment 2026-05-21](#technical-notes-unity--authoring--runtime-map)) |

## Consequences

- Save stores `revealedMapLayer` per floor (bitmasks + feature flags), not player strokes
- No map tool tutorial; tutorial teaches **reading** map + FOE icons
- EO "mapping as skill" shifts to **pathfinding / FOE routing** rather than pen accuracy
- **Floor layout** is authored in a **level painter** ? `ExplorationFloor` assets; runtime HUD is **2D** from data + reveal state
- **FPV dungeon scenes** remain separate presentation; they do not feed the player map texture

## Technical notes (Unity) � authoring & runtime map

**Goal:** EO-style auto-map in the HUD � schematic 2D chart, not a render of the FPV corridor.

### Authoring � Floor Editor (primary)

| Piece | Rule |
|-------|------|
| **Tool** | Unity **Editor** floor painter (custom window) � design-time only; not player-facing |
| **Output** | `ExplorationFloor` ScriptableObject per floor (`gridWidth`/`gridHeight`, tiles, **edge walls**, features, FOE spawns, patrol paths) |
| **Preview** | 2D grid canvas inside the painter (walkable, walls, icons) � **single source of truth** for layout QA |
| **FPV scene** | Optional separate scene/prefab for corridor art; aligned to the same grid, **not** baked into the HUD map |

Painter replaces hand-editing huge tile arrays in the Inspector and replaces **MapProxy + minimap camera** as the main authoring/preview path.

**Launch:** one test floor may be filled manually in a `ExplorationFloor` asset until the painter ships; runtime still uses **2D `MapView`**, not RT.

### Runtime � 2D map HUD (primary)

1. **`MapSystem`** holds revealed state (`Visited`, `WallMask`, features, `FoeIcons`) � unchanged authority.
2. **`MapView`** (UI Toolkit) draws the chart from `IReadOnlyFloorMapState` + floor style from `ContentDatabase` / `ExplorationFloor`:
   - **Cells/edges:** floor tiles and wall segments revealed so far (fog hides unrevealed).
   - **Party / FOE:** icons at grid `(x, y, level)` � UI elements or stamped sprites on the 2D layer ([ADR 019](019-floor-verticality.md) � at launch, map shows party�s **current `level`**).
3. **Refresh on dirty:** rebuild or patch the 2D view when reveal changes, party moves, or FOE updates � **no** minimap `RenderTexture` in the main path.
4. **Pan/zoom** on the map `VisualElement` ([ADR 014](014-mvp1-exploration-map.md)).

Implementation options (either is fine): per-cell `VisualElement` grid, or one `Texture2D` blit from a cell atlas � pick per perf/style in the game repo.

### Collision alignment

Walkability and wall blocking use the **same `ExplorationFloor` data** the painter writes (`DungeonExplorer` ? `IsWalkable` / edge query) � not mesh colliders, not the 2D HUD ([dungeon navigation](../docs/02-dungeon-navigation.md)).

### Deferred � MapProxy + minimap camera (optional)

Orthographic camera rendering **`MapProxy`** cubes into a `RenderTexture` for the HUD is **deferred / debug-only**:

- Optional 3D schematic preview in Scene view
- **Not** required for shipping map UI once the floor painter + 2D `MapView` exist

If used: `MapProxy` layer, FPV excludes it; same grid alignment rules as before.

### Authority (unchanged)

`MapRevealCalculator` + `MapSystem` own reveal rules and save data. Painter and `MapView` are **authoring / presentation** only � see [04 � Tech notes � Map system](../docs/04-tech-notes.md#map-system).

## Related

- [Mapping system](../docs/02-systems/mapping.md)
- [02 � Dungeon navigation](../docs/02-dungeon-navigation.md)
- [ADR 019 � Floor verticality](019-floor-verticality.md)
- [release scope](../docs/00-release-scope.md)
