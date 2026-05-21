# ADR 005 — FOE Movement During Combat (Optional Later)

**Status:** Deferred (optional later)  
**Date:** 2026-05-20  
**Depends on:** [ADR 003 — FOE step patrol](003-foe-step-patrol.md)

## Context

Exploration patrol ([ADR 003](003-foe-step-patrol.md)) advances FOEs on **party grid steps** only. During combat, exploration is frozen and FOEs do not move. Optional later feature: FOEs keep **creeping on the grid** while the party fights, adding pressure and map awareness.

## Terminology

| Term | Meaning |
|------|---------|
| **Turn** | One actor’s action in the AGI queue |
| **Combat round** | All living combatants take one turn; then end-of-round effects |

**FOE patrol during combat uses combat round**, not per-turn.

## Decision (when enabled)

1. **Toggle:** Floor or global flag `foeCombatPatrol: true` (off in MVP).
2. **When:** At **end of each combat round** — after every living combatant has acted once, before the next round’s queue is built.
3. **Movement:** Each living FOE on the current floor advances **1 cell** along its patrol path (same path data as exploration).
4. **Party position:** Frozen on the exploration cell where combat started; does not move on grid during fight.
5. **Map:** FOE icons update on map panel if visible (read-only map still shown optional).
6. **No mid-battle join (default):** FOE entering the party’s cell during combat **does not** add enemies to the current fight. Resolve on battle end (see below).

### On battle end (combat patrol enabled)

| Situation | Proposal |
|-----------|----------|
| FOE not on party cell | Resume exploration; FOE positions persisted |
| FOE on party cell after win | Optional **chain battle** — start FOE fight immediately (TBD) |
| FOE on party cell after flee | Player escapes; FOE remains on cell (blocking) |
| Party wipe | GAME OVER; FOE positions saved |

Chain battles are **not** MVP; document here for when combat patrol ships.

## Rejected

| Option | Why |
|--------|-----|
| FOE move per AGI **turn** | Too fast in long fights; harder to read; not the chosen design |
| Mid-battle FOE join | Out of scope unless chain battles added at fight end |
| Real-time movement during combat | Conflicts with turn-based grid |

## Interaction with ADR 003

| Mode | FOE advances when |
|------|-------------------|
| **Exploration** (always) | Party displacement steps (`stepsPerMove`) |
| **Combat** (optional) | **End of each combat round** — 1 cell per FOE |

When combat starts, **pause** exploration step patrol; use combat-round rule until battle ends.

## Consequences (implementation)

- `FoeSystem.TickCombatRound()` called from `CombatController.EndCombatRound()` only
- UI: subtle FOE slide on map / dungeon overlay during battle (optional)
- Long fights = FOEs can surround party cell — raises stakes for optional chain FOE fights

## Related

- [Combat](../docs/02-systems/combat.md)
- [02 — Dungeon navigation](../docs/02-dungeon-navigation.md)
- [ADR 003 — FOE step patrol](003-foe-step-patrol.md)
