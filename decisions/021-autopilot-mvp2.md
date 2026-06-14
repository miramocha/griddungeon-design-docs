# ADR 021 — Autopilot (optional)

> **Scope: Optional feature** — not required for initial release.

**Status:** Accepted (MVP2 scope)  
**Date:** 2026-05-21

## Context

Etrian Odyssey **auto-walk** follows **player-drawn paths** on the map. Grid Dungeon has **auto-reveal, read-only map** — no drawing ([ADR 002](002-mapping-model.md)). Players still need to **skip manual stepping** when crossing areas they already explored (hub return, gather routes, backtracking).

At launch: **manual** grid steps + hold-to-repeat only ([ADR 001](001-grid-movement.md)).

## Decision

1. **Defer to MVP2** — no autopilot at launch ([release scope](../docs/00-release-scope.md)).
2. **Autopilot** — on the map, player selects a **revealed walkable** destination; runtime **pathfinds** on discovered floor cells and walks the party along that path one grid step at a time ([autopilot](../docs/02-systems/autopilot.md)).
3. **Discovered-only graph** — path nodes are cells the auto-map has charted as walkable floor on the current `level`; **no** routing through unrevealed/fog tiles.
4. **No player path drawing** — does not amend ADR 002.
5. **Step parity** — each displacement on the path runs full step events (FOE patrol, encounters); not teleport.
6. **Same-level MVP2** — autopilot does not use stairs/jump pads across `level` bands; vertical links are manual.
7. **Cancel** — manual move/turn/interact, `Esc`, new destination click, or combat/hub ends autopilot immediately.

## Alternatives considered

| Option | Rejected because |
|--------|------------------|
| EO-style drawn paths | Conflicts with ADR 002 |
| Teleport to revealed cell | Removes FOE/encounter tension on the route |
| Route through unrevealed cells | Not “explored before”; breaks map-as-knowledge |
| Launch autopilot | Scope creep; tutorial needs deliberate movement |
| Blind forward march toggle | Does not solve backtracking; goal is pathfind to known tiles |

## Consequences

- `AutopilotController` (Runtime): pathfind + next-segment facing; `DungeonExplorer` keeps lerp/events.
- `MapView`: destination pick, path overlay, invalid-click feedback.
- Input: `MapSetAutopilotDestination`, `CancelAutopilot` (map `LMB` + `Esc` defaults).

## Related

- [Autopilot (optional)](../docs/02-systems/autopilot.md)
- [ADR 001 — Grid movement](001-grid-movement.md)
- [ADR 002 — Mapping model](002-mapping-model.md)
- [ADR 014 — launch exploration map](014-mvp1-exploration-map.md)
- [Release scope](../docs/00-release-scope.md)
