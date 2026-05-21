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

- **Always available** in exploration (side panel; fullscreen `M`).
- **Fullscreen map:** movement **pass-through** (can still step); pan/zoom mouse on map ([ADR 014](../../decisions/014-mvp1-exploration-map.md)).
- Grid 1:1 with dungeon cells; north up.
- **Read-only:** pan/zoom only; no edit interactions.
- Party position and facing indicated on the map.

### Map UI motion

Exploration HUD uses the same **reactive, blocking** bar as combat ([tech notes — UI reactivity](../04-tech-notes.md#ui-reactivity)). Grid step lerp already blocks movement ([ADR 001](../../decisions/001-grid-movement.md)); map feedback below completes (or runs in the same beat) before the next step is accepted.

| Event | UI reaction (MVP1) | Blocks until done |
|-------|-------------------|-------------------|
| Floor / wall revealed | Cell or edge **fade/stamp in** on map panel | Yes — with step beat |
| Door / stairs discovered | Icon **pop-in** on tile | Yes — with interact beat |
| FOE enters sight | FOE marker **fade in** on map | Yes — before next step if revealed mid-step |
| FOE patrol step | Marker **slides** to new cell | No — ambient; must not block player input |
| Party moves | Party arrow **slides** to new cell; optional facing tick | Yes — with step lerp |
| Chest / gather (MVP1 gather) | Node icon **flash** + loot toast | Yes — before next interact |
| Open fullscreen map (`M`) | Panel **scale/fade** open | No — overlay only |

## Auto-reveal rules

| Element | Revealed when |
|---------|----------------|
| **Floor** | Party **enters** cell |
| **Walls** | **Bump** blocked side → stamp that wall; **enter cell** → reveal floor + wall on all solid edges of cell ([ADR 014](../../decisions/014-mvp1-exploration-map.md)) |
| **Doors** | Party **opens** or **unlocks** door (closed vs open state tracked) |
| **Stairs** | Party **steps on** stairs tile |
| **Chest / gather / fish** | Opens chest (**MVP1**); gather/fish nodes (**MVP2**) — marks node on map |
| **FOE** | FOE enters **line of sight**; icon **updates** on step-patrol move |
| **Traps** (optional) | Party **triggers** trap on cell (mark for repeat visits) |

MVP1 minimum: auto-floor, auto-wall on bump, auto-stairs/doors on interact, auto-FOE pin.

## Fog of war

- Unvisited cells: hidden or shown as unexplored void.
- Visited cells: floor + known walls/doors/features only.
- No perfect reveal of entire floor without walking it.

## Wipe behavior

On party wipe: **keep revealed map** for that floor (unchanged). Optional hard mode: map wipe — not default.

## Difficulty (future)

If mapping feels too easy, tune **fog strictness** or **FOE icon fade** — not manual drawing.

## Related docs

- [02 — Dungeon navigation](../02-dungeon-navigation.md)
- [ADR 002 — Mapping model](../../decisions/002-mapping-model.md)
- [04 — Tech notes](../04-tech-notes.md)
