# ADR 016 — Summon Control (MVP1 Scripted)

**Status:** Accepted (MVP1); **player control — decide later**  
**Date:** 2026-05-20

## Context

Aux slots ([ADR 004](004-auxiliary-slots.md)) can hold **summons** with their own AGI turns. Open question: does the player pick commands each summon turn (like core party), or does the summon run a fixed script?

## Decision (MVP1)

1. **MVP1 summons use a fixed action script** — no player command menu on summon turns.
2. Each summon definition lists **ordered or conditional actions** (simple table), e.g.:
   - Turn 1: Skill A → random enemy
   - Turn 2+: Attack → lowest HP front enemy
3. Summon still appears in **AGI queue**; on its turn the game **auto-resolves** one step from its script.
4. **UI:** Summon turn shows brief log + animation (*“Drone used Volt Burst”*); no Attack/Guard/Skill buttons for the player.
5. **One test summon** in MVP1 — **Summoner-only** skill `deploy_test_drone` (aux back, 3 turns, **2–3 scripted steps** max).

## Decide later (post-MVP1)

| Option | Description |
|--------|-------------|
| **A — Full player control** | Summon turn = same command UI as core (Attack / skills per summon kit) |
| **B — Hybrid** | Player sets **stance** (aggressive / support) once; script picks skills |
| **C — Keep scripted** | Summons remain AI-only; balance via script + duration |

Record choice in a future ADR when playtesting MVP1 summon.

## Guests (unchanged for MVP1)

- **Guests** remain **player-controlled** by default; **NPC guest** flag = AI script (same pattern as summon script).

## Rejected for MVP1

| Option | Why |
|--------|-----|
| Full summon command UI in MVP1 | Doubles combat UI scope; script proves aux + AGI first |
| Summons skip AGI queue | Hides aux in turn strip; harder to read |

## Consequences

- `SummonDefinition.actionScript` — list of `{ actionId, targetRule }` or turn-indexed rows
- `CombatController.ResolveSummonTurn()` — no player input wait
- `Combatant.IsPlayerControlled` → false for MVP1 summons
- Later: if **A** chosen, add `IsPlayerControlled` per summon template and command phase branch

## Related

- [Summons & guests](../docs/02-systems/summons-and-guests.md)
- [MVP1 spec](../docs/mvp1-spec.md)
- [ADR 004 — Auxiliary slots](004-auxiliary-slots.md)
- [ADR 015 — MVP1 combat](015-mvp1-combat.md)
