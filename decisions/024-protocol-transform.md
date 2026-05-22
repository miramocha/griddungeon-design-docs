# ADR 024 — Protocol Transform (core enhancement)

**Status:** Proposed  
**Date:** 2026-05-22

## Context

Post-MVP1 skill **`protocol_transform`** would let the Navigator **enhance or transform** one **core** party member during combat — distinct from [ADR 023](023-protocol-deploy-sortie-summon.md) **Protocol Deploy**, which adds a **navigator sortie summon** in an **aux** slot without touching the core six layout.

Design questions:

- Is the guild member **replaced in their core slot** by a fixed combat profile, or **morphed in place** (same entity, swapped stats/skills/portrait)?
- How does this relate to **hub bench swap** ([party-and-classes](../docs/02-systems/party-and-classes.md) — recruit bench, swap only at hub) and **in-fight revive** (downed core stays in slot)?

**Not in scope:** pulling a **bench roster** member into the active six mid-fight; Navigator entering a formation row ([ADR 007](007-navigator-role.md)).

## Shared rules (all Protocols + this skill)

Aligned with [ADR 006](006-union-team-bar.md), [ADR 007](007-navigator-role.md), and [ADR 023](023-protocol-deploy-sortie-summon.md):

1. **Invoker** — a **core** member on their AGI turn when Synchro is **100%** (`CombatCommand.Protocol`); that core **spends their turn**; bar → **0%** after resolve.
2. **Executor** — active **Navigator** off-formation (calls the protocol; **no** Navigator AGI turn).
3. **Aura** — Navigator **aura stays on** all living core six during transform (same lock as Deploy).
4. **Protocol lock** — **no second Protocol** (any skill, including Deploy or Transform) while **any** post-MVP1 Protocol “mode” from this battle is active — sortie alive **or** transform active ([ADR 023](023-protocol-deploy-sortie-summon.md) §7). Deploy and Transform are **mutually exclusive** in one fight.
5. **Participants** — living **core** per skill min/max; transformed slot rules below.
6. **Synchro charge** — only **core six** actions charge the bar; transform entity actions follow chosen implementation model.

## Decision (skill scope)

1. **`protocol_transform`** — post-MVP1; Navigator kit and/or guild-unlocked; **3+** living core participants (tune in data).
2. **Target** — player picks **one living core** combatant (front or back slot) to transform; **not** aux, **not** downed, **not** bench roster.
3. **Navigator** — unchanged off-formation ([ADR 007](007-navigator-role.md)); does not become the transformed unit.
4. **Duration** — until battle end, transform HP → 0 (revert rules per model), duration expiry, or explicit **Revert** (define in skill data).
5. **While transform active** — block further Protocol use; same global lock as [ADR 023](023-protocol-deploy-sortie-summon.md).

### Implementation model — pick one before implementation

| Model | Combat slot | Guild member | Combatant identity | Pros | Cons |
|--------|-------------|--------------|-------------------|------|------|
| **A — Slot replace** | Same core index | **Sideline** for fight (stored `characterId`); **fixed transform profile** occupies slot | New `Combatant` or `Kind` with `source: ProtocolTransform`, `replacedCoreId` | Clear “swap out” fantasy; original untouched until revert | Save/sync, XP, equipment, downed/revert edge cases |
| **B — In-place morph** | Same core index | **Same** `characterId` | Same `Combatant`; overlay `TransformProfileId` on stats/skills/portrait | Simpler persistence; still “this character” for narrative | Weaker “replaced by unit” read; revert must restore snapshot |

**Recommendation for spec pass:** default **A** if the fantasy is “fixed unit takes their place”; default **B** if the fantasy is “same hero, powered-up form.” Document choice in `TransformDefinition` content schema when one model is accepted.

**Regardless of model:** transformed unit is **`CombatantKind.Core`** in that slot (still counts toward core six, row targeting, Protocol participation rules). **Not** aux summon ([ADR 004](004-auxiliary-slots.md)).

### Locked product rules (2026-05-22)

| Rule | Value |
|------|--------|
| Second Protocol while transform active | **No** |
| Second Protocol while Deploy sortie active | **No** (ADR 023) |
| Deploy + Transform same battle | **No** (one Protocol mode total) |
| Aura during transform | **On** |
| Hub bench swap mid-fight | **No** (unchanged) |
| Navigator in core row | **No** (unchanged) |

### UI (draft)

- Protocol picker: target **core portrait** + transform preview (stats/skills).
- Transformed slot: distinct frame/VFX; label = **transform profile display name** (or core name + “Transformed” — pick at implementation).
- Navigator strip unchanged (executes, does not move into row).

## Rejected

| Option | Why |
|--------|-----|
| Transform via **bench** member swap | Hub-only roster policy; different system |
| Transform into **aux** slot | Deploy already owns aux channel (ADR 023) |
| Navigator transforms **self** in formation | ADR 007 |
| Multiple simultaneous transforms | Scope; one mode per battle is enough for MVP2+ pass |
| Second Protocol while any mode active | User locked: same as Deploy |

## Consequences (when accepted)

- Content: `protocol_transform` + per-Navigator (or guild) `TransformDefinition` linked to `transform_profile_id`
- `ProtocolSystem`: after resolve, apply transform to `BattleState` + `PartyRuntime`; set `battle.ProtocolModeActive` (or equivalent) until cleared
- Combat UI: target selection, transform overlay, revert on end
- `CombatController`: queue rebuild if AGI/skills change; sync back to `PartyRuntime` on battle end per model A vs B
- Tests: mutual exclusion with Deploy; no Protocol at 100% while mode active; revert restores sideline member (A) or snapshot (B)

## Related

- [ADR 023 — Protocol Deploy](023-protocol-deploy-sortie-summon.md)
- [Synchro Protocol](../docs/02-systems/synchro-protocol.md)
- [Navigator](../docs/02-systems/navigator.md)
- [Party & classes](../docs/02-systems/party-and-classes.md)
- [Combat](../docs/02-systems/combat.md)
- [ADR 006 — Team bar](006-union-team-bar.md)
- [ADR 007 — Navigator role](007-navigator-role.md)
- [00 — Game references § Burst modes](../docs/00-game-references.md) — transform *feel* only; do not replace Synchro + Navigator without ADR
