---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/foe
---
# ADR 003 — FOE Step-Based Patrol

**Status:** Accepted  
**Date:** 2026-05-20  
**Aligns with:** *Etrian Odyssey* (step-driven analogue)

## Context

FOEs are visible on the grid before combat. Patrol creates routing puzzles (wait for gap, bait, avoid). Patrol must stay **deterministic** and tied to exploration pace — not a background real-time simulation.

## Decision

FOE movement advances on **party steps**, not real-time timers.

1. **Step counter** — Each party **displacement** into a new cell (forward, backward, strafe left, strafe right) increments `playerStepCount` (turns in place do not count).
2. **Patrol interval** — Each FOE defines `stepsPerMove` (e.g. 2 = move every 2 party steps). When `playerStepCount % stepsPerMove == 0`, that FOE advances one node along its **patrol path** (looping list of cells).
3. **Stationary FOE** — `patrol` path length 1 or `stepsPerMove: 0` / omitted → never moves.
4. **Rendering** — Update dungeon sprite + map icon on move; optional short lerp optional for readability.
5. **Collision** — FOE enters party cell → forced combat. Party enters FOE cell → combat.
6. **Strength tier** — green / yellow / red vs party level (unchanged).

### Example

```yaml
foe:
  id: forest_stalker
  patrol: [[12,8], [12,9], [13,9]]
  stepsPerMove: 3
```

Party takes 3 displacement steps (any mix of forward/back/strafe) → stalker moves `12,8` → `12,9`.

## Rejected

| Option | Why |
|--------|-----|
| Real-time patrol timer | Desyncs from grid logic; unfair if player opens map/menu; harder to test |
| Patrol on turn-in-place | Inflates step count without exploration progress |

## Launch scope

- Implement step counter + patrol resolution in core.
- **Content:** Stratum 1 can use mostly stationary FOEs; B3F+ uses patrol paths.
- One tutorial FOE on B2F with `stepsPerMove: 4` teaches the rhythm.

## Consequences

- `FoeSystem.OnPartyStep()` runs after movement resolves, before encounter roll (order: move party → FOE patrol → trap → random encounter).
- Save stores `playerStepCount` per floor + each FOE `patrolIndex`.
- Playtest tuning: typical `stepsPerMove` range 2–5.

## Optional later

[ADR 005 — FOE movement during combat](005-foe-combat-patrol.md): while party is in battle, FOEs advance **1 cell per combat round** (not per AGI turn; exploration step patrol paused). Off at launch.

## Related

- [02 — Dungeon navigation](../docs/02-dungeon-navigation.md)
- [03 — Dungeons & encounters](../docs/03-content/dungeons-and-encounters.md)
- [ADR 001 — Grid movement](001-grid-movement.md)
- [ADR 005 — FOE combat patrol](005-foe-combat-patrol.md) (deferred)
