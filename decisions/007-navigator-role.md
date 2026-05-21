# ADR 007 — Navigator Role

**Status:** Accepted  
**Date:** 2026-05-20  
**Amended:** 2026-05-20

## Context

[Union team bar](006-union-team-bar.md) needs a clear **in-world actor** who calls team skills. Core six already fill 3+3 formation; aux slots are for summons/guests. **Navigator** is a swappable party lead **outside** formation who runs Union and grants passives.

## Decision

1. **One active Navigator** per dive; **not** a slot in 3+3 (+ aux) formation.
2. Navigator **executes** Union skills in Union phase; core six **participate** only.
3. Navigator grants **passive auras** to core six while active.
4. **Unlock pool** — Navigators unlock via strata, side quests, events (not recruitment).
5. **Switch** among unlocked Navigators at **Navigator Office** (hub) only — not at Explorers Guild; no mid-dungeon swap.
6. Navigator **no AGI turn**, **not on exploration grid**.
7. Navigator **not targetable** — no enemy or boss may directly interact with Navigator in combat (no HP, damage, status).
8. **Fixed package per Navigator** — aura + Union kit in data; **no** XP, levels, skill points, aura tiers, or equipment.
9. Union bar still **charges from core six actions** only.

## Rejected

| Option | Why |
|--------|-----|
| Navigator in front/back row | Off-formation by design |
| Navigator fills aux slot | Aux reserved for summon/guest |
| Any core member invokes Union | Navigator identity diluted |
| Mid-dungeon Navigator switch | User chose hub only |
| Boss hits Navigator | User chose permanent non-target |
| Guild recruitment for Navigators | Unlock via progression instead |
| Navigator XP / skill points / equipment | User chose unlock-only simplicity |

## Consequences

- `PartyRuntime.ActiveNavigator` + `UnlockedNavigatorIds`
- Targeting system excludes `CombatantKind.Navigator` entirely
- Union UI owned by Navigator controller
- Formation UI: navigator strip separate from 3+3+aux

## Related

- [Navigator](../docs/02-systems/navigator.md)
- [Union](../docs/02-systems/synchro-protocol.md)
- [ADR 006 — Union team bar](006-union-team-bar.md)
