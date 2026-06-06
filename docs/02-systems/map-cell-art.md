# Map cell art (2D schematic)

MVP1 exploration map is a **read-only 2D schematic** in UI Toolkit — one visual stack per grid cell, not FPV mesh art. Authority stays in `MapSystem` / `FloorMapState`; `MapView` is presentation only ([ADR 002](../../decisions/002-mapping-model.md), [mapping](mapping.md)).

**Implementation today (#38):** `MapView` paints visited cells with **USS background fills** and per-edge **wall border overlays** (`MapGridCellWallBorders` + `MapGridCellPaint`). Cell glyphs are hidden; **marker overlays** (party, FOE, gather, stairs, story) use `MapCellArtCatalog` sprites anchored to cell layout (`MapGridOverlayAnchor`). Optional per-cell sprite mode remains behind `UsePerCellSpriteRendering` for dev preview. **Do not** ship 16-tile wall autotile PNGs — composite edges only ([game `MapView.cs`](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/UI/Views/MapView.cs)).

**Inspiration (other games):** [Refs — Map UI](../refs/map-ui.md) — screenshot board; locked art rules stay in this doc.

---

## Cell model (runtime)

| Layer | Source | Shown when | Notes |
|-------|--------|------------|-------|
| **Party** | `DungeonExplorer` facing | Party on cell | **Overlay** — `MapPartyMarkerPresenter` (not a cell glyph) |
| **Fog** | `!IsVisited` | Unexplored | Void / fog tint; no floor or edges |
| **Solid mass** | `FloorTileData.IsWalkable == false` | Visited | Authored `#` tiles — impassable rock |
| **Edge walls** | `WallMask` N/E/S/W on **walkable** cell | Visited + mask ≠ `None` | Bump + enter reveal ([ADR 014](../../decisions/014-mvp1-exploration-map.md)); **not** the same as `#` |
| **Alcove (3+ edges)** | Same `WallMask`, `count ≥ 3` | Visited | Walkable floor fill + edge borders (no separate alcove glyph) |
| **Features** | `FeatureState` on cell | Visited + feature known | Stairs as **overlay sprites**; door overlay **deferred** (closed/open tint planned) |
| **Gather** | `HasGatherNode` (ASCII `G`) | Visited (or dev reveal-all) | **Overlay** — `MapGatherMarkersPresenter` · `map-view__marker--gather` |
| **Chest** | `ChestItemId` set / ASCII `C` — **impassable** | Visited + chest known | **Overlay** when wired ([#38](https://github.com/miramocha/griddungeon-game/issues/38)); interact from **adjacent** cell while **facing** chest ([#105](https://github.com/miramocha/griddungeon-game/issues/105)) |
| **Stairs up/down** | `FeatureType.StairsUp` / `StairsDown` | Visited + feature known | **Overlay** — `MapStairsMarkersPresenter` ([ADR 014](../../decisions/014-mvp1-exploration-map.md)) |
| **FOE** | `FoeSystem` / map FOE state | In LOS / last known | **Overlay** — `MapFoeMarkersPresenter` (not cell `F`) |
| **Floor** | Default walkable | Visited, nothing above | `·` glyph in cell label |

### Draw priority

**Cell paint** (`MapGridCellPaint` / `MapView.PaintCellAt`): fog → solid mass → walkable floor/alcove fill → per-edge wall borders (`WallMask`).

**Overlays** (sibling layers above the cell grid; see [exploration UI — Map marker overlays](exploration-ui.md#map-marker-overlays)): gather → stairs → story → FOE → party. Anchored to cell `worldBound` when layout is resolved.

**Campaign blockers** (e.g. B1F tutorial gate `(10,13)`) are **walkability / interaction** rules ([S1 campaign](https://github.com/miramocha/griddungeon-game/issues/33)) — not a separate map icon. ASCII `D` / `X` in blockouts mark designer intent; runtime may show a **door overlay** only after the player discovers/interacts with a `FeatureType.Door` on that cell.

### Walls: composite, not autotiles

| Piece | Count | Role |
|-------|-------|------|
| Floor tile | 1 | Walkable cell base |
| Solid block | 1 | `#` and `X` mass; optional **gate tint** for `X` |
| Edge segment | 1 art, **rotate** N/E/S/W | 0–4 instances per cell from `WallMask` |
| Alcove fill | 0–1 | 3+ revealed edges on floor — fill or reuse solid at **low opacity** |
| Party marker | 1 art, **rotate** N/E/S/W | Overlay — author **north-up**; runtime `rotate` matches glyph degrees |

Do **not** ship 16 PNG wall autotiles for UI; rotate/mirror one segment texture per side. Same rule for **party facing** — one `map_party`, not four directional sprites.

**Internal walls** = `SolidEdges` on `FloorTileData` for walkable cells, not separate tile types ([dungeons legend](../03-content/dungeons-and-encounters.md#map-legend-ascii-blockouts)).

### Doors

| Piece | Role |
|-------|------|
| Floor underlay | Walkable cell |
| Door icon overlay | On walkable cell when `FeatureType.Door` is revealed |
| State | **Tint only** — closed / locked / open (open = hide overlay or desaturate) |

Closed/open tracked in map state ([mapping — auto-reveal](mapping.md#auto-reveal-rules)); icon appears on interact/reveal, not on first floor step unless spec says otherwise.

---

## ASCII blockout vs runtime glyphs

Authoring legend: [dungeons & encounters — Map legend](../03-content/dungeons-and-encounters.md#map-legend-ascii-blockouts).

| Blockout | Runtime (glyph / class today) | Sprite target |
|----------|------------------------------|---------------|
| `#` | `#` · `map-view__cell--wall` | Solid block |
| `X` | `#` or solid + **gate tint** | Solid block + `map-view__cell--gate` |
| `.` | `·` · `map-view__cell--floor` | Floor tile |
| `^` / `v` | `^` / `v` · stairs classes | Stairs up / down icons |
| `F` | FOE **overlay** (not cell glyph) | `MapFoeMarkersPresenter` |
| `C` | Solid mass (`#`-class) — **not walkable**; chest **overlay** when feature wired | `map-view__cell--chest` (planned) |
| `G` | Walkable floor + gather **overlay** when visited | `map-view__marker--gather` |
| `D` | *(not wired)* | Door overlay + state tint |
| `E` / `M` | Party spawn only — not map icons | — |
| Edge walls | `╵╷╶╴│—█` via `WallGlyph` | Rotated edge segment(s) + alcove fill |
| Party | Facing arrow **overlay** | `MapPartyMarkerPresenter` · one `map_party` sprite, **rotate** per `FacingDirection` |

---

## Sprite checklist (MVP1 → MVP2)

Paths are conventions; final names live in the game repo `Assets/UI/Map/` (or atlas SO).

### MVP1 — ship with schematic map

| Asset | Qty | Notes |
|-------|-----|-------|
| `map_floor_tile` | 1 | Walkable base |
| `map_solid_block` | 1 | `#` impassable |
| `map_solid_gate` | 1 | Optional tint variant for `X` / blocked passage |
| `map_wall_edge` | 1 | Rotate 0°/90°/180°/270° for N/E/S/W |
| `map_alcove_fill` | 0–1 | 3+ edges; or reuse solid @ ~40% opacity |
| `map_fog_cell` | 1 | Unvisited void |
| `map_party` | 1 | Authored **facing north**; UITK `rotate` per `FacingDirection` (same degrees as glyph marker) |
| `map_stairs_up` | 1 | Replaces `^` |
| `map_stairs_down` | 1 | Replaces `v` |
| `map_foe` | 1 | Replaces `F` |

### MVP1 — same issue / follow-up (game)

| Asset | Qty | Notes |
|-------|-----|-------|
| `map_door_closed` | 1 | Overlay; tint locked variant |
| `map_door_open` | — | Hide overlay or desaturated floor |

### MVP2+

| Asset | Notes |
|-------|-------|
| `map_chest` / `map_chest_open` | After chest feature wired |
| `map_gather` | Gather node ([ADR 014](../../decisions/014-mvp1-exploration-map.md)) |
| `map_trap` | Optional trap mark |
| Path overlay | Autopilot destination line ([ADR 021](../../decisions/021-autopilot-mvp2.md)) |

---

## Visual tone (municipal underworks)

Locked with [00 — Vision § Tone & setting](../00-vision.md#tone--setting). MVP1 map and HUD use a **warm charcoal + amber-gold** palette — readable schematic (transit / architectural plan), **not** sci-fi neon.

| Token | Hex | Use |
|-------|-----|-----|
| Base | `#14161A` | Panels, fog |
| Surface | `#1E2228` | Cards, map chrome |
| Ink | `#E8EAED` | Primary labels |
| Muted | `#9AA3B2` | Hints, secondary |
| Accent | `#C9A227` | Synchro fill, active turn, stairs down |
| Copper | `#B87333` | Secondary highlight (optional) |
| Ally | `#6B9080` | Party on map / roster (utility green-grey) |
| Threat | `#B85C4A` | FOE (rust, not alarm red) |
| Stairs up | `#8A9BA8` | Cool utility sign |

Implementation: [MapView.uss](https://github.com/miramocha/griddungeon-game/blob/main/Assets/UI/Screens/Exploration/MapView.uss), [CombatHud.uss](https://github.com/miramocha/griddungeon-game/blob/main/Assets/UI/Screens/Combat/CombatHud.uss), [HudOverlay.uss](https://github.com/miramocha/griddungeon-game/blob/main/Assets/UI/Screens/Shared/HudOverlay.uss).

---

## USS tint classes (BEM)

Namespace: `map-view__cell` + modifiers. Today in [MapView.uss](https://github.com/miramocha/griddungeon-game/blob/main/Assets/UI/Screens/Exploration/MapView.uss); extend for sprites (background-image per layer or child `VisualElement`s).

| Class | Applies to | Purpose |
|-------|------------|---------|
| `map-view__cell` | Every cell | Base 16×16 (adjust in USS), center align |
| `map-view__cell--fog` | Unvisited | Fog background + hide glyph |
| `map-view__cell--floor` | Walkable default | Floor tint |
| `map-view__cell--wall` | Solid `#` or edge wall cell | Wall / edge tint |
| `map-view__cell--gate` | `IsBlockedPassage` on visited walkable | Blocked passage `X` — copper tint |
| `map-view__cell--alcove` | Walkable + 3+ revealed edges | Same floor fill as `.` (borders show alcove) |
| `map-view__cell--stairs-up` | `FeatureType.StairsUp` | Utility cool (`#8A9BA8`) |
| `map-view__cell--stairs-down` | `FeatureType.StairsDown` | Amber accent (`#C9A227`) |
| `map-view__cell--door` | *(planned)* | Door overlay base |
| `map-view__cell--door-closed` | *(planned)* | Default closed |
| `map-view__cell--door-locked` | *(planned)* | Key-gated |
| `map-view__cell--door-open` | *(planned)* | Open / desaturated |
| `map-view__cell--foe` | *(legacy cell class)* | FOE uses `map-view__marker` overlay, not cell `--foe` |
| `map-view__cell--party` | *(legacy cell class)* | Party uses `map-view__marker` overlay |
| `map-view__marker--gather` | Gather overlay | `MapGatherMarkersPresenter` |
| `map-view__cell--chest` | *(planned)* | Loot feature |

**Color-friendly rule:** distinguish states with **tint/opacity**, not separate art per door state unless readability fails in playtest.

---

## Implementation notes (game repo)

- **Overlay sprites vs cell grid:** `map_party`, `map_foe`, stairs, and gather art bind through `MapCellArtCatalog` on marker layers — **not** per-cell sprite stacks (UITK texture-slot limit). Party marker **rotates** one north-up `map_party` sprite per `FacingDirection`.
- **Marker overlays:** default **16×16 px** in side panel; **fullscreen** (`M`) scales cells (up to 48px) via `MapGridPainter.ApplyCellDimensions` and hides the party strip. Snapped via `MapGridOverlayAnchor` (layout) with metrics fallback.
- **Fullscreen chrome:** wall border width and marker inset use `map-view--fullscreen-inset-N` modifier classes (2–6px, scales with cell size).
- **Shared cell painter:** `MapGridPainter` used by `MapView` + dev map preview ([#85](https://github.com/miramocha/griddungeon-game/pull/85)).
- **Marker overlays:** `MapGridMarkerAnimator` + `*MarkersPresenter` on layers above the cell grid ([#90](https://github.com/miramocha/griddungeon-game/pull/90)).
- **Layered UI (sprites):** cell underlay + overlay children (gather → hub → foe → party) — same split as today.
- **Save / reveal:** unchanged — `WallMask`, `FeatureState`, `Visited` ([map-reveal-save-format](map-reveal-save-format.md)).
- **Tests:** Edit Mode — `MapGridCellPaintTests`, `MapGridCellWallBordersTests`, `MapGridLayoutMetricsTests`, `MapGridPainterTests`, marker presenter tests; Play Mode via DevBootstrap **F2**.

---

## Related

- [Mapping](mapping.md) · [Map reveal save format](map-reveal-save-format.md)
- [ADR 014 — MVP1 exploration map](../../decisions/014-mvp1-exploration-map.md)
- [04 — Tech notes § Map assets](../04-tech-notes.md#map-cell-art-assets)
- [mvp1-spec § Exploration & map](../mvp1-spec.md#2-systems-checklist)
- Game: [#38](https://github.com/miramocha/griddungeon-game/issues/38) (cell art + door overlay), [#18](https://github.com/miramocha/griddungeon-game/issues/18) (baseline MapView), [#26](https://github.com/miramocha/griddungeon-game/issues/26) (shared painter), [#33](https://github.com/miramocha/griddungeon-game/issues/33) (campaign gates ≠ map icons)
