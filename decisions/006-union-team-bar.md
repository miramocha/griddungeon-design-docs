# ADR 006 — Union Team Bar

**Status:** Accepted  
**Date:** 2026-05-20  
**Working name:** Union (rename later)

## Context

Need a party-wide burst/coordination mechanic distinct from per-character MP skills and deferred Boost/Break. *Etrian Odyssey V* Union skills inspire timing and participant rules; UI uses one **team bar** instead of six personal gauges.

## Decision

1. **Single Union bar** (0–100%) shared by the core party.
2. **100% at hub exit**; persists across fights on a floor; **0% after** any Union skill use until recharged in combat.
3. **Charge** from core members’ combat actions and events (attack, skill, guard, damage taken, kills — see [union.md](../docs/02-systems/union.md)).
4. **Union as a core turn action** when bar is **100%** (optional); uses that character’s AGI turn; Navigator executes ([revision 2026-05-21](https://github.com/miramocha/griddungeon-game/issues/10) — was round-start Union phase).
5. **Participants** — living core members only; skill defines count; aux excluded in MVP1.
6. **Navigator** ([ADR 007](007-navigator-role.md)) **executes** Union; off-formation; not combat-targetable.
7. **Boost/Break** is **out of scope** ([ADR 008](008-campaign-defaults.md)); Union is the team-layer system.

## Rejected (for now)

| Option | Why |
|--------|-----|
| Six personal Union gauges | Higher UI/UX cost; user asked for team bar |
| Union only at round start (EO-style) | MVP1 uses mid-queue on a core turn when bar is full |
| Exploration charging | Keeps tension inside fights |

## Consequences

- `UnionBar` on `PartyRuntime`; `UnionSystem` hooks combat events
- Combat round flow: `TurnPhase` (core may `CombatCommand.Union` when bar full) → `EndRound`
- `UnionSkillDefinition` — participant min/max, effect script

## Related

- [Union system](../docs/02-systems/union.md)
- [Navigator](../docs/02-systems/navigator.md)
- [ADR 007 — Navigator role](007-navigator-role.md)
- [Combat](../docs/02-systems/combat.md)
