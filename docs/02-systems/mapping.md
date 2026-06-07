# Mapping

The labyrinth **reveals itself** as the party explores. There are **no manual drawing tools** (no wall/door/icon toolbar, eraser, or map notes). The map panel is **read-only** — a record of what the party has already discovered.

## Design goal

> "Watch the labyrinth fill in as you survive it."

Mapping stays central for **navigation and FOE tracking**, but skill expression is **routing and exploration**, not cartography minigames.

## Out of scope

- Wall / door / stair / loot **drawing tools**
- Player-placed icons or text notes
- Map edit mode, eraser, bump-assist stamp buttons
- Mis-mapping due to player drawing errors

## Map UI

- **Implementation wiring:** [exploration UI](exploration-ui.md) — `ExplorationHudView` → `map-view-mount` → `MapView` (event subscriptions, input, phase visibility).
- **Presentation:** **2D schematic** in UI Toolkit from `StratumFloor` + revealed state — authored via **floor level painter** → SO, not FPV mesh or minimap camera ([ADR 002](../../decisions/002-mapping-model.md#technical-notes-unity--authoring--runtime-map)).
- **Always available** in exploration (side panel; fullscreen `M`).
- **Fullscreen map:** movement **pass-through** (can still step); pan/zoom mouse on map ([ADR 014](../../decisions/014-mvp1-exploration-map.md)).
- Grid 1:1 with dungeon cells at the party’s current **`level`** band; north up ([ADR 019](../../decisions/019-floor-verticality.md)). Other height bands: same rules when visited; layer toggle post-MVP1 optional.
- **Read-only:** pan/zoom only; no edit interactions.
- Party position and facing indicated on the map.
- **Combat (MVP1):** Map **not** in the default combat layout; **`M`** toggles read-only floor map ([game phase](game-phase.md), [input bindings](input-bindings.md)). See [§ Consider / explore — map during combat](#consider--explore--map-during-combat).

### Map UI motion

Exploration HUD uses the same **reactive, blocking** bar as combat ([tech notes — UI reactivity](../04-tech-notes.md#ui-reactivity)). Grid step lerp already blocks movement ([ADR 001](../../decisions/001-grid-movement.md)); map feedback below completes (or runs in the same beat) before the next step is accepted.

**Implementation today:** cell grid is painted imperatively via `MapGridPainter` inside `MapView`; **party / FOE / gather / hub-gate** use overlay presenters + `MapGridMarkerAnimator` ([#90](https://github.com/miramocha/griddungeon-game/pull/90), [#94](https://github.com/miramocha/griddungeon-game/pull/94)). Full read-model + `ExplorationMapPresenter` refactor: [exploration UI appendix](exploration-ui.md#appendix--future-map-read-model-refactor).

| Event | UI reaction (MVP1) | Blocks until done |
|-------|-------------------|-------------------|
| Floor / wall revealed | Cell or edge **fade/stamp in** on map panel | Yes — with step beat |
| Door / stairs discovered | Icon **pop-in** on tile | Yes — with interact beat |
| FOE enters sight | FOE marker **fade in** on map | Yes — before next step if revealed mid-step |
| FOE patrol step | Marker **slides** to new cell | No — ambient; must not block player input |
| Party moves | Party arrow **slides** to new cell; optional facing tick | Yes — with step lerp |
| Chest (MVP1) | Chest overlay **flash** + loot toast — opened from **adjacent** cell while **facing** chest ([#105](https://github.com/miramocha/griddungeon-game/issues/105)) | Yes — before next interact |
| Gather (MVP1) | Gather overlay **flash** + loot toast | Yes — before next interact |
| Open fullscreen map (`M`) | Panel **scale/fade** open | No — overlay only |

## Auto-reveal rules

| Element | Revealed when |
|---------|----------------|
| **Floor** | Party **enters** cell → chart every cell in **radius-2 circle** around party (Euclidean; includes adjacent walls) |
| **Walls** | **Bump** blocked side → stamp that wall; **enter cell** → solid perimeter edges for each newly charted cell in the radius-2 circle ([ADR 014](../../decisions/014-mvp1-exploration-map.md)) |
| **Doors** | Party **opens** or **unlocks** door (closed vs open state tracked) |
| **Stairs** | Party **steps on** stairs tile |
| **Chest** | Party **Interact** on adjacent walkable cell **facing** impassable chest tile — loot once; cell stays blocked ([#105](https://github.com/miramocha/griddungeon-game/issues/105)) |
| **Gather** | Gather node **overlay when visited**; MVP1 instant loot ([ADR 014](../../decisions/014-mvp1-exploration-map.md)) |
| **Fish** | Fish nodes (**MVP2**) |
| **FOE** | FOE enters **line of sight**; icon **updates** on step-patrol move |
| **Traps** (optional) | Party **triggers** trap on cell (mark for repeat visits) |

MVP1 minimum: auto-floor, auto-wall on bump, auto-stairs/doors on interact, auto-FOE pin.

## Fog of war

- Unvisited cells: hidden or shown as unexplored void.
- Visited cells: floor + known walls/doors/features only.
- No perfect reveal of entire floor without walking it.

## Wipe behavior

On party wipe: **keep revealed map** for that floor (unchanged). Optional hard mode: map wipe — not default.

## Consider / explore — map during combat

**Status:** Not locked — MVP1 ships **toggle-only** (`M`); showing the map **by default** during fights is under evaluation.

### Why explore this

When [FOE combat patrol](../../decisions/005-foe-combat-patrol.md) and [mid-battle join](chain-foe-battle.md) ship (MVP2+), FOEs can **advance on the grid each combat round** while the party fights. With the map hidden, players may miss:

- A second FOE **creeping toward** the fight anchor
- Whether **flee** is still viable relative to walls and incoming patrol ([foe-encounters](foe-encounters.md#flee-from-foe-fights-locked))
- EO-style tension: “another stalker on the map” while you are already in a fight

**MVP1:** Patrol + mid-battle join are **off** ([ADR 015](../../decisions/015-mvp1-combat.md)) — ambient grid threat is low, so a combat-only `M` toggle is acceptable for scope.

### Options (not decided)

| Option | Pros | Cons |
|--------|------|------|
| **A — Persistent side map** (exploration-style panel) | Always-on FOE icons and party anchor; strongest threat read | Shrinks combat command/arena space; FPV is already hidden — panel may feel disconnected from the arena |
| **B — Compact tactical strip** | Small schematic + party/FOE dots only | Extra layout + art; may duplicate arena focus |
| **C — `M` toggle only (current MVP1)** | Clean combat HUD; no layout cost | Easy to forget; no ambient “incoming FOE” read |
| **D — Threat ping only** | Badge/icon when a FOE is within N cells of anchor | Minimal chrome; weak for route and flee planning |

### Implementation notes (if we adopt A or B)

- `MapView` today lives on the **`ExplorationHud`** GameObject only ([exploration UI](exploration-ui.md), [class design § View controllers](../05-class-design-mvp1.md#view-controllers)); combat would need shared or embedded `MapView` + `Map` input map while `Combat` map stays primary.
- FOE markers should reflect **patrol step** and **in-combat / joining** state ([chain-foe-battle](chain-foe-battle.md)); updates must **not** block combat input (ambient slide, same as exploration patrol).
- Arena stays **slot-based** ([combat scene](combat-scene.md)) — map shows **grid** threat, not live battle positions.

### Recommendation for next pass

Revisit when enabling **`foeCombatPatrol`** on at least one test floor; playtest **A** vs **C** before writing a new ADR. If threat read is sufficient with pings, prefer **D** over full side panel.

## Autopilot (MVP2)

**Map click** on a **revealed walkable** cell sets destination; party **pathfinds** over discovered floor on the current `level` and walks the route ([autopilot](autopilot.md), [ADR 021](../../decisions/021-autopilot-mvp2.md)). Uses charted map state only — no player path drawing ([ADR 002](../../decisions/002-mapping-model.md)).

---

## Map cell art (2D schematic)

Locked **cell stack**, **composite walls** (edge segments + alcove — not 16 autotiles), **door overlay** tints, sprite checklist, and USS classes: **[map-cell-art.md](map-cell-art.md)**.

**Cell labels** (`MapView.PaintCellAt` via `MapGridPainter`): fog → solid `#` → revealed `WallMask` edges (3+ → `█`) → features (**stairs only** in cells) → floor `·`. Party, FOE, gather, and B1F hub-gate are **not** painted into cell labels — they live in sibling overlay layers (see [exploration UI — Map marker overlays](exploration-ui.md#map-marker-overlays)).

**Overlay layers** (bottom → top under `map-view-grid-host`): gather → hub entrance (B1F `stairsUp` when visited) → FOE → party. `MapGridMarkerAnimator` handles fade/slide tweens; FOE patrol slides are **ambient** (do not block input).

`FeatureType.Door` exists in data; **door glyph/overlay not wired** on cells. Campaign tutorial blockers (e.g. B1F `(10,13)`) are walkability gates ([game #33](https://github.com/miramocha/griddungeon-game/issues/33)), not map icons.

---

## Related docs

- [Refs — Map UI (other games)](../refs/map-ui.md) — inspiration screenshots (not spec authority)
- [Map cell art](map-cell-art.md) — sprites, tints, ASCII vs runtime table
- [Map reveal save format](map-reveal-save-format.md) — packing visited cells and wall bitmasks for `SaveGame`
- [02 — Dungeon navigation](../02-dungeon-navigation.md)
- [Autopilot (MVP2)](autopilot.md)
- [FOE encounters](foe-encounters.md) · [Chain / mid-battle FOE](chain-foe-battle.md)
- [Exploration UI](exploration-ui.md) — HUD composition and bind lifecycle
- [Combat scene](combat-scene.md) · [Game phase](game-phase.md)
- [ADR 002 — Mapping model](../../decisions/002-mapping-model.md)
- [ADR 005 — FOE combat patrol](../../decisions/005-foe-combat-patrol.md) · [ADR 014 — MVP1 exploration map](../../decisions/014-mvp1-exploration-map.md)
- [ADR 019 — Floor verticality](../../decisions/019-floor-verticality.md)
- [04 — Tech notes](../04-tech-notes.md)
