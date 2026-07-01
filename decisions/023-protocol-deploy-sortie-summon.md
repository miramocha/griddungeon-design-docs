---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/synchro
  - domain/combat
---
# ADR 023 — Protocol Deploy (navigator sortie as summon)

**Status:** Accepted  
**Date:** 2026-05-22  
**Amended:** 2026-05-22

## Context

Later skill **`protocol_deploy`** lets the active Navigator join combat in a limited way. An earlier draft placed the Navigator **in** an aux row, which conflicted with [ADR 007](007-navigator-role.md) (off-formation, not targetable) and read as “Navigator fills aux slot” (explicitly rejected there).

**Resolution:** Protocol Deploy does **not** move the Navigator into formation. Like every Protocol ([ADR 006](006-union-team-bar.md)), a **core member spends their AGI turn** to invoke it when Synchro is **100%** (`CombatCommand.Protocol` on that core’s turn). The Navigator has **no AGI turn** and cannot act independently — they **execute** the skill off-formation (voice/portrait, effect authority) while the invoking core’s turn ends after resolve. That Protocol spawn creates a **navigator sortie summon** in an empty aux slot — same occupant type as Summoner deploys ([ADR 004](004-auxiliary-slots.md), [summons & guests](../docs/02-systems/summons-and-guests.md)).

## Decision

1. **`protocol_deploy`** — later; costs **100% Synchro**; **3+** living core participants; bar → 0% after use; invoked on a **core** AGI turn per [synchro-protocol § Timing](../docs/02-systems/synchro-protocol.md#timing--core-turn-action-mvp1) (Navigator does not take that turn).
2. **Spawn** — player picks **empty** aux front or back; skill fails if that row already has a summon or guest.
3. **Combatant** — `CombatantKind.Summon` using a per-Navigator `SummonDefinition` (sortie frame / kit in data); tag `source: ProtocolDeploy` and `linkedNavigatorId` for logic/UI.
4. **Navigator** — stays **off-formation**: executes Protocol, keeps **aura** on core six, **not targetable**, **no AGI turn** on the Navigator entity ([ADR 007](007-navigator-role.md) unchanged).
5. **Sortie summon** — **targetable**; in AGI queue; row rules same as other aux summons; summon actions **do not** charge Synchro.
6. **Control** — follows summon pipeline ([ADR 016](016-summon-control-mvp1.md)): **player-controlled** like other launch summons (minimal kit per sortie `SummonDefinition`).
7. **While sortie is alive** — **no Protocol** (any skill) until the sortie is gone (dismiss, HP 0, or battle end). After the sortie clears and Synchro reaches **100%** again, the party may invoke **another** Protocol in the same battle ([ADR 006](006-union-team-bar.md) recharge loop).
8. **Dismiss** — battle end, summon HP → 0 (recall; Navigator not “dead”), duration expiry, or explicit dismiss action on sortie turn (define in skill data).
9. **UI** — aux slot label **Summon**; portrait/name shows **active Navigator display name** (not a generic “Sortie” label).
10. **Summon sources** — aux summons may come from **Summoner class deploy skills** or **Protocol Deploy** (different channels; same slot rules).

## Rejected

| Option | Why |
|--------|-----|
| Navigator as `CombatantKind` in formation row | Breaks ADR 007 identity and targeting |
| Navigator immune but sortie also immune | Loses risk/reward for deploy |
| Second Protocol while sortie still alive | Cannot stack; after sortie ends, recharge allows another Protocol |
| One Protocol per battle total | Rejected 2026-05-22 — multiple uses when bar refills |
| Aura suspended while sortie out | User locked: aura stays on |
| Generic “Sortie” UI label | User locked: use Navigator name |

## Consequences

- Content: `protocol_deploy` + per-Navigator `sortie_summon_id` → `SummonDefinition`
- `BattleSetup` / `ProtocolSystem`: spawn summon after Protocol resolve; block Protocol only **while** sortie active (not for whole battle)
- Combat UI: aux frame + Navigator name on sortie portrait
- No new `CombatantKind`; no amendment to ADR 007 role rules — only clarifies deploy is summon spawn

## Related

- [Synchro Protocol](../docs/02-systems/synchro-protocol.md)
- [Navigator](../docs/02-systems/navigator.md)
- [Summons & guests](../docs/02-systems/summons-and-guests.md)
- [ADR 004 — Auxiliary slots](004-auxiliary-slots.md)
- [ADR 007 — Navigator role](007-navigator-role.md)
- [ADR 006 — Team bar](006-union-team-bar.md)
- [ADR 016 — Summon control](016-summon-control-mvp1.md)
- [ADR 024 — Protocol Transform](024-protocol-transform.md) — core slot replace; cannot overlap active sortie or active transform
