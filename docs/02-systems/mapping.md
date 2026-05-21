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

- **Always available** in exploration (side panel; fullscreen view optional).
- Grid 1:1 with dungeon cells; north up.
- **Read-only:** pan/zoom only; no edit interactions.
- Party position and facing indicated on the map.

## Auto-reveal rules

| Element | Revealed when |
|---------|----------------|
| **Floor** | Party **enters** cell |
| **Walls** | Party **bumps** blocked side (forward, back, or strafe into wall) OR enters cell and that edge is wall (reveal adjacent wall segments along sight rules — MVP: bump + entered cell perimeter) |
| **Doors** | Party **opens** or **unlocks** door (closed vs open state tracked) |
| **Stairs** | Party **steps on** stairs tile |
| **Chest / gather** | Party **opens** chest or **uses** gather node |
| **FOE** | FOE enters **line of sight**; icon **updates** on step-patrol move |
| **Traps** (optional) | Party **triggers** trap on cell (mark for repeat visits) |

MVP minimum: auto-floor, auto-wall on bump, auto-stairs/doors on interact, auto-FOE pin.

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
