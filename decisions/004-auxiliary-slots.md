---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/combat
---
# ADR 004 — Auxiliary Combat Slots (+1 Front / +1 Back)

**Status:** Accepted  
**Date:** 2026-05-20

## Context

Core party is **6 guild members (3+3)**. Design needs optional combat allies — **summons** from skills and **guests** from quests — without expanding persistent roster or grid exploration.

## Decision

1. Add **one auxiliary slot per row**: aux front, aux back.
2. Each aux slot holds **at most one** entity: either a **summon** or a **guest** (never two in one slot).
3. **Core 6** unchanged for exploration, save, XP, hospital.
4. **Summons** — temporary, no XP, combat-only unless skill specifies otherwise. Sources: **Summoner** deploy skills later), later **Protocol Deploy** navigator sortie ([ADR 023](023-protocol-deploy-sortie-summon.md)), rare items / boss mechanics.
5. **Guests** — script/quest-spawned, player- or AI-controlled per encounter definition, no XP.
6. **Turn order:** aux units included in AGI queue like party members.
7. **Max combatants:** 8 (6 core + 2 aux).

## Rejected

| Option | Why |
|--------|-----|
| 7th+8th core roster slots | Bloats guild, EO-like 6 is enough |
| Summons as invisible buffs | Loses row targeting clarity |
| Guests on exploration grid | Scope explosion |

## Consequences

- Combat UI needs 4+4 row layout with aux styling
- `Combatant` type: `Core | Summon | Guest`
- Save stores aux state only during active combat (or quest guest flags)

## Related

- [Summons & guests](../docs/02-systems/summons-and-guests.md)
- [Party & classes](../docs/02-systems/party-and-classes.md)
- [Combat](../docs/02-systems/combat.md)
- [ADR 023 — Protocol Deploy sortie summon](023-protocol-deploy-sortie-summon.md)
