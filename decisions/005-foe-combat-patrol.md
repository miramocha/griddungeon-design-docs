# ADR 005 — FOE Movement During Combat (Optional Later)

**Status:** Deferred (**MVP2** — optional per floor flag `foeCombatPatrol: true`)  
**Date:** 2026-05-20  
**Depends on:** [ADR 003 — FOE step patrol](003-foe-step-patrol.md)

## Context

Exploration patrol ([ADR 003](003-foe-step-patrol.md)) advances FOEs on **party grid steps** only. During combat, exploration is frozen and FOEs do not move. Optional later feature: FOEs keep **creeping on the grid** while the party fights, and may **join the fight** when they reach the party cell.

## Terminology

| Term | Meaning |
|------|---------|
| **Turn** | One actor’s action in the AGI queue |
| **Combat round** | All living combatants take one turn; then end-of-round effects |

**FOE patrol during combat uses combat round**, not per-turn.

## Decision (when enabled)

1. **Toggle:** Floor or global flag `foeCombatPatrol: true` (off in MVP1).
2. **When:** At **end of each combat round** — after every living combatant has acted once, before the next round’s queue is built.
3. **Movement:** Each living FOE on the current floor advances **1 cell** along its patrol path (same path data as exploration).
4. **Party position:** Frozen on the exploration cell where combat started; does not move on grid during fight.
5. **Map:** FOE icons update on map panel when visible — **whether the map stays on screen during combat** is not locked (MVP1: `M` toggle only); see [mapping § Consider / explore](../docs/02-systems/mapping.md#consider--explore--map-during-combat).
6. **Mid-battle join:** If FOE on party cell and not in encounter → **one FOE joins** per round ([ADR 010](010-chain-foe-battle.md)).

### End of combat round order

```
Status / summon ticks → FOE patrol → Mid-battle join (max 1) → Victory/wipe → Rebuild queue
```

### On battle end

| Situation | Behavior |
|-----------|----------|
| Victory | All enemies dead (including mid-join FOEs); resume exploration |
| Flee | Party retreats 1 cell back if possible ([ADR 011](011-foe-flee-retreat.md)); FOE stays on cell |
| Wipe | GAME OVER |

## Rejected

| Option | Why |
|--------|-----|
| FOE move per AGI **turn** | Too fast; not chosen |
| Real-time movement during combat | Conflicts with turn-based grid |
| Post-victory chain FOE fights | Superseded by mid-battle join ([ADR 010](010-chain-foe-battle.md)) |

## Interaction with ADR 003

| Mode | FOE advances when |
|------|-------------------|
| **Exploration** (always) | Party displacement steps (`stepsPerMove`) |
| **Combat** (optional) | **End of each combat round** — 1 cell per FOE |

When combat starts, **pause** exploration step patrol; use combat-round rule until battle ends.

## Consequences (implementation)

- `FoeSystem.TickCombatRound()` called from `CombatController.EndCombatRound()`
- `FoeJoinSystem.TryJoinOneFoe()` after patrol ([ADR 010](010-chain-foe-battle.md))
- Dynamic enemy list + AGI queue insert next round

## Related

- [Combat](../docs/02-systems/combat.md)
- [FOE mid-battle join](../docs/02-systems/chain-foe-battle.md)
- [ADR 003 — FOE step patrol](003-foe-step-patrol.md)
- [ADR 010 — FOE mid-battle join](010-chain-foe-battle.md)
