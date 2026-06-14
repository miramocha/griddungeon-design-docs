# ADR 006 — Team burst bar (Synchro Protocol)

**Status:** Accepted  
**Date:** 2026-05-20  
**Display name:** [Synchro Protocol](020-team-burst-naming.md) (locked 2026-05-21; was working name **Union**)

## Context

Need a party-wide burst/coordination mechanic distinct from per-character MP skills and deferred Boost/Break. *Etrian Odyssey V* Union skills inspire timing and participant rules; UI uses one **team meter** (**Synchro**) for **Synchro Charge** instead of six personal gauges ([ADR 020](020-team-burst-naming.md)).

## Decision

1. **Single Synchro Charge pool** (0–100%) shared by the core party.
2. **100% at hub exit** (when Synchro is unlocked); persists across fights on a floor; **0% after** any Protocol use until recharged in combat. **S1 tutorial exception:** locked until mid-fight unlock in unbeatable first FOE on B2F — see [synchro-protocol § S1 gating](../docs/02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe).
3. **Gain** from core members’ combat actions and events (attack, skill, guard, damage taken, kills — see [synchro-protocol.md](../docs/02-systems/synchro-protocol.md)).
4. **Protocol as a core turn action** when charge is **100%** (optional); uses that character’s AGI turn; Navigator executes ([issue #10](https://github.com/miramocha/griddungeon-game/issues/10)). **Multiple Protocols per battle** are allowed when Synchro **recharges** to 100% again; blocked only while Deploy sortie or Transform is active ([ADR 023](023-protocol-deploy-sortie-summon.md), [ADR 024](024-protocol-transform.md)).
5. **Participants** — living core members only; skill defines count; aux excluded at launch.
6. **Navigator** ([ADR 007](007-navigator-role.md)) **executes** Protocols; off-formation; not combat-targetable.
7. **Boost/Break** is **out of scope** ([ADR 008](008-campaign-defaults.md)); Synchro Protocol is the team-layer system.

## Rejected (for now)

| Option | Why |
|--------|-----|
| Six personal burst gauges | Higher UI/UX cost; user asked for team bar |
| Burst only at round start (EO-style) | Launch uses mid-queue on a core turn when bar is full |
| Exploration charging | Keeps tension inside fights |

## Consequences

- `SynchroBar` on `PartyRuntime` (Synchro Charge 0..1); `ProtocolSystem` hooks combat events
- Combat round flow: `TurnPhase` (core may `CombatCommand.Protocol` when bar full) → `EndRound`
- `ProtocolSkillDefinition` — participant min/max, effect script

## Related

- [Synchro Protocol](../docs/02-systems/synchro-protocol.md)
- [ADR 020 — Naming](020-team-burst-naming.md)
- [Navigator](../docs/02-systems/navigator.md)
- [ADR 007 — Navigator role](007-navigator-role.md)
- [Combat](../docs/02-systems/combat.md)
