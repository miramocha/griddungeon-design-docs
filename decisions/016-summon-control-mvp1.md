# ADR 016 — Summon Control (MVP1 Player)

**Status:** Accepted (MVP1)  
**Date:** 2026-05-20  
**Amended:** 2026-05-22 — MVP1 uses **player control** (was scripted); avoids throwaway `SummonScriptRunner` path.  
**Amended:** 2026-05-31 — Summon commands queued in **command planning** with cores, before AGI playback ([ADR 015](015-mvp1-combat.md) round flow).

## Context

Aux slots ([ADR 004](004-auxiliary-slots.md)) can hold **summons** with their own AGI turns. Summons need a command model for MVP1 that matches the long-term UX (player picks actions) without building scripted AI that will be removed.

## Decision (MVP1)

1. **MVP1 summons are player-controlled** — Attack, Guard, and **skill IDs on `SummonDefinition`** (not full class trees). No Item / Flee on summon planning unless added later.
2. **Command planning (before AGI):** Player assigns **one command per living core**, then **one per living player summon** (and player guests without an AI script), in roster order (cores first, then aux). Highlight advances like cores; commands live in `PartyCommandBatch`. When every required actor has a command, combat **auto-commits** and AGI playback runs ([combat § Round flow](../docs/02-systems/combat.md)).
3. **AGI playback:** Each actor (core, summon, enemy) executes its **queued** command on its AGI slot. **No live command menu** on summon turns during playback.
4. **`deploy_test_drone`** (Summoner core turn) spawns `test_drone` on aux **back**, **3** rounds. Drone kit: **Attack** + `volt_burst`. A summon that **does not exist** at planning start (e.g. deployed same round) is **not** in that round’s planning batch; it enters planning on the **next** round after it is on the field.
5. Summon still appears in **AGI queue**; turn strip + party roster show aux during planning and playback.
6. **UI:** Command panel + roster highlight the active planning target (core or summon). Synchro / Protocol **not** offered for summon planning.
7. **Do not implement** MVP1 `SummonScriptRunner` auto-resolve for **player** summons. Keep runner only for **NPC guest AI** when `actionScript` is set.

### Deploy (core turn)

- **`deploy_test_drone`** may be **queued** while aux back is occupied (e.g. player expects current drone to die before the summoner’s AGI turn). On **resolve**, if the slot is still occupied: **fail**, **no MP spent**, player feedback ([mvp1-class-skills](../docs/03-content/mvp1-class-skills.md#locked-implementation-rules)).

## Rejected for MVP1

| Option | Why |
|--------|-----|
| Scripted summon turns only | Throwaway; player control is the target UX anyway |
| Full summon skill trees | Scope; one test drone kit is enough |
| Summons skip AGI queue | Harder to read turn order |
| Live summon menu on AGI slot (mid-playback pick) | Split attention during playback; planning batch matches core UX |

## Post-MVP1 (optional)

| Option | Description |
|--------|-------------|
| **Stance hybrid** | Player sets aggressive / support once; AI picks from kit |
| **Protocol Deploy sortie** | Navigator sortie summon ([ADR 023](023-protocol-deploy-sortie-summon.md)) — may share player-control rules |
| **Mid-round planning** | After deploy in AGI, optional prompt to queue new summon before rest of queue |

## Consequences

- `SummonDefinition`: `skillIds[]` (or equivalent) for combat menu; **`actionScript` not used** for MVP1 player summons
- `PartyCommandBatch`: cores + planning aux (summon / player guest)
- `CombatController`: `UsesCommandPlanning`; `ExecuteQueuedAuxTurn` on AGI slot
- `Combatant.IsPlayerControlled` → **true** for MVP1 summons
- `volt_burst`: `SkillDefinition` row; on **drone** skill list, not Summoner guild tree
- Implementation: [griddungeon-game #11](https://github.com/miramocha/griddungeon-game/issues/11), [#52](https://github.com/miramocha/griddungeon-game/issues/52)

## Guests (unchanged for MVP1)

- **Guests** with **no** `actionScript` → same **command planning** path as summons.
- **NPC guest** with script → AI on AGI turn (`SummonScriptRunner`).

## Related

- [Summons & guests](../docs/02-systems/summons-and-guests.md)
- [MVP1 class skills](../docs/03-content/mvp1-class-skills.md)
- [MVP1 spec](../docs/mvp1-spec.md)
- [ADR 004 — Auxiliary slots](004-auxiliary-slots.md)
- [ADR 015 — MVP1 combat](015-mvp1-combat.md)
- [Game #11](https://github.com/miramocha/griddungeon-game/issues/11) — `deploy_test_drone` (acceptance: planning-phase summon commands)
