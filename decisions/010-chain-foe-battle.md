# ADR 010 — FOE Mid-Battle Join

> **Scope: Optional feature** — not required for initial release.

**Status:** Accepted  
**Date:** 2026-05-20  
**Amended:** 2026-05-20  
**Depends on:** [ADR 005 — FOE combat patrol](005-foe-combat-patrol.md)

## Context

[FOE combat patrol](005-foe-combat-patrol.md) lets FOEs reach the party cell during combat. Need a rule when FOE and party share a cell mid-fight.

Earlier draft used **post-victory chain FOE** (separate fights). User chose **mid-battle join**, **one FOE at a time**.

## Decision

1. FOE on party cell during combat **joins the current encounter** as an enemy.
2. **Max one FOE join per combat round** (not all FOEs on cell at once).
3. If multiple FOEs eligible same round: join **highest tier** (red > yellow > green); stable id tie-break.
4. Joined FOE acts in AGI queue starting **next combat round** only — **locked** (not the round they join).
5. Process join at **end of round** after FOE patrol, **before** victory check.
6. **No** separate post-victory chain fight for FOEs that could have joined mid-battle.
7. Feature active when `foeCombatPatrol` enabled ([ADR 005](005-foe-combat-patrol.md)); off in MVP1.

## Rejected

| Option | Why |
|--------|-----|
| Post-victory chain (separate fights) | Superseded by mid-battle join |
| Unlimited joins same round | User: one at a time |
| Mid-battle join with no patrol | FOE cannot reach cell without movement |
| Joined FOE acts same round | Rejected — acts **next combat round** (confirmed) |

## Consequences

- `CombatController.EndCombatRound` → `FoeJoinSystem.TryJoinOneFoe()`
- Enemy roster grows mid-fight; UI and AGI queue must support dynamic adds
- Combat log + alert on join

## Related

- [FOE mid-battle join](../docs/02-systems/chain-foe-battle.md)
- [ADR 005](005-foe-combat-patrol.md)
