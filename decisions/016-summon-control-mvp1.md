# ADR 016 — Summon Control (MVP1 Player)

**Status:** Accepted (MVP1)  
**Date:** 2026-05-20  
**Amended:** 2026-05-22 — MVP1 uses **player control** (was scripted); avoids throwaway `SummonScriptRunner` path.

## Context

Aux slots ([ADR 004](004-auxiliary-slots.md)) can hold **summons** with their own AGI turns. Summons need a command model for MVP1 that matches the long-term UX (player picks actions) without building scripted AI that will be removed.

## Decision (MVP1)

1. **MVP1 summons are player-controlled** on their AGI turn — same command phase as core ([combat](../docs/02-systems/combat.md), [#34](https://github.com/miramocha/griddungeon-game/issues/34) skeleton).
2. **Command set is minimal** per summon: **Attack**, **Guard**, and **skill IDs listed on `SummonDefinition`** (not full class trees). No Item / Flee on summon turns unless added later.
3. **`deploy_test_drone`** (Summoner core turn) spawns `test_drone` on aux **back**, **3** rounds. Drone kit: **Attack** + `volt_burst` ([MVP1 class skills](../docs/03-content/mvp1-class-skills.md#summon-kit-test_drone)).
4. Summon still appears in **AGI queue**; `CombatController` sets **`IsWaitingForPlayer`** for `CombatantKind.Summon` (and Core).
5. **UI:** Command panel + turn strip highlight the **acting summon** portrait; Synchro / Protocol **not** offered on summon turns.
6. **Do not implement** MVP1 `SummonScriptRunner` auto-resolve for player summons. Keep runner only for **NPC guest AI** if needed, or delete summon path from it.

### Deploy (core turn)

- **`deploy_test_drone`** on occupied aux back: **fail cast**, **no MP spent**, player feedback ([mvp1-class-skills](../docs/03-content/mvp1-class-skills.md#locked-implementation-rules)).

## Rejected for MVP1

| Option | Why |
|--------|-----|
| Scripted summon turns only | Throwaway; player control is the target UX anyway |
| Full summon skill trees | Scope; one test drone kit is enough |
| Summons skip AGI queue | Harder to read turn order |

## Post-MVP1 (optional)

| Option | Description |
|--------|-------------|
| **Stance hybrid** | Player sets aggressive / support once; AI picks from kit |
| **Protocol Deploy sortie** | Navigator sortie summon ([ADR 023](023-protocol-deploy-sortie-summon.md)) — may share player-control rules |

## Consequences

- `SummonDefinition`: `skillIds[]` (or equivalent) for combat menu; **`actionScript` not used** for MVP1 player summons
- `CombatController.SubmitPlayerAction`: accept **Summon** (and **Guest** when player-controlled), not Core-only
- `Combatant.IsPlayerControlled` → **true** for MVP1 summons
- `volt_burst`: `SkillDefinition` row; on **drone** skill list, not Summoner guild tree
- Implementation: [griddungeon-game #52](https://github.com/miramocha/griddungeon-game/issues/52)

## Guests (unchanged for MVP1)

- **Guests** remain **player-controlled** by default; **NPC guest** flag = AI script (may use `SummonScriptRunner` or enemy AI pattern).

## Related

- [Summons & guests](../docs/02-systems/summons-and-guests.md)
- [MVP1 class skills](../docs/03-content/mvp1-class-skills.md)
- [MVP1 spec](../docs/mvp1-spec.md)
- [ADR 004 — Auxiliary slots](004-auxiliary-slots.md)
- [ADR 015 — MVP1 combat](015-mvp1-combat.md)
- [Game #11](https://github.com/miramocha/griddungeon-game/issues/11) — `deploy_test_drone` (update acceptance to match this ADR)
