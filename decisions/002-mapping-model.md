# ADR 002 — Mapping Model

**Status:** Accepted (amended 2026-05-20)  
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

## Related

- [Mapping system](../docs/02-systems/mapping.md)
- [02 — Dungeon navigation](../docs/02-dungeon-navigation.md)
