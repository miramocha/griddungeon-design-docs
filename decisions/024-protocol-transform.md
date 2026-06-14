# ADR 024 — Protocol Transform (core slot replace)

**Status:** Accepted  
**Date:** 2026-05-22  
**Amended:** 2026-05-22 (Protocol recharge loop)

## Context

Later skill **`protocol_transform`** lets the Navigator **replace** one **core** party member in their formation slot with a **fixed transform profile** for a limited time — distinct from [ADR 023](023-protocol-deploy-sortie-summon.md) **Protocol Deploy**, which spawns a **navigator sortie summon** in an **aux** slot.

**Not in scope:** bench roster swap mid-fight ([party-and-classes](../docs/02-systems/party-and-classes.md)); Navigator entering a formation row ([ADR 007](007-navigator-role.md)); mid-dungeon Navigator swap (hub only — active kit fixed for the dive).

**Practical:** Deploy then Transform in one battle requires **both** skills on the **same** Navigator’s kit ([synchro-protocol § Kit + hub lock](../docs/02-systems/synchro-protocol.md#kit--hub-lock-practical)); content should usually grant **one** mode Protocol per Navigator.

## Shared rules (all Protocols + this skill)

Aligned with [ADR 006](006-union-team-bar.md), [ADR 007](007-navigator-role.md), and [ADR 023](023-protocol-deploy-sortie-summon.md):

1. **Invoker** — a **core** member on their AGI turn when Synchro is **100%** (`CombatCommand.Protocol`); that core **spends their turn**; bar → **0%** after resolve.
2. **Executor** — active **Navigator** off-formation (calls the protocol; **no** Navigator AGI turn).
3. **Aura** — Navigator **aura stays on** all living core six during transform.
4. **Protocol lock** — **no Protocol** while **transform is active** or while a **Deploy sortie is alive** ([ADR 023](023-protocol-deploy-sortie-summon.md)). When the mode ends and Synchro reaches **100%** again, the party may invoke **another** Protocol in the same battle (Strike, Mend, Deploy, Transform, etc.). Deploy and Transform **must not overlap** (no sortie + transform at once); they may both occur in one fight **sequentially** after recharge.
5. **Participants** — **3+** living core members at invoke time (tune in data); transform target may be **any** living core including the invoker.
6. **Synchro Charge gain** — transform profile actions in a core slot **do** add charge (still `CombatantKind.Core`).

## Decision

### Skill

1. **`protocol_transform`** — later; in active **Navigator’s Protocol kit only** (not guild skill tree).
2. **Target** — player picks **one living core** (any front/back slot, including self); **not** aux, **not** downed, **not** bench.
3. **Navigator** — off-formation; does not become the transform profile ([ADR 007](007-navigator-role.md)).

### Implementation model — slot replace (locked)

**Model A — slot replace** (rejected **B — in-place morph** for this feature).

| Step | Rule |
|------|------|
| **On resolve** | Snapshot sidelined guild member (`characterId`, HP, MP, statuses, equipment refs) off-slot; **transform profile** occupies the **same core index** as `CombatantKind.Core` with `source: ProtocolTransform`, `replacedCoreId`. |
| **During transform** | Profile uses **hybrid** player control — limited command menu (attack + transform kit skills; not full class tree). |
| **Duration** | **`duration_turns`** per `TransformDefinition`; auto-revert when expired. |
| **Early end** | **Revert** command on transform profile’s turn (hybrid menu). |
| **HP → 0** | **Revert safe** — transform ends immediately; **original guild member** restored from snapshot (HP/MP/status as stored at transform start unless data overrides). |
| **After revert** | Original is a **normal core** — Medic revive and targeting rules apply same fight. |
| **Battle end** | If still transformed, revert safe before syncing to `PartyRuntime` / save. |

**One active transform at a time.** After **Revert**, duration, or HP→0 revert safe, Synchro may recharge; **another** Transform (or any Protocol) is allowed when bar is **100%** and no sortie/transform is blocking.

### UI (locked)

- Protocol flow: pick target **core portrait** + transform preview.
- Active slot: transform profile **display name** + subtitle **“via [CoreName]”**.
- Navigator strip unchanged.

### Content

- Per-Navigator `transform_profile_id` → `TransformDefinition` (stats, hybrid skill ids, `duration_turns`, VFX).
- `protocol_transform` in that Navigator’s fixed Protocol list when unlocked.

## Rejected

| Option | Why |
|--------|-----|
| **B — In-place morph** | User chose slot replace (fixed unit fantasy) |
| Guild-unlocked transform profiles | User chose Navigator kit only |
| Transform via **bench** swap | Hub-only roster policy |
| Transform into **aux** slot | ADR 023 owns aux channel |
| Navigator in core row | ADR 007 |
| One Protocol per battle total | Rejected 2026-05-22 — multiple uses when bar refills |
| Overlapping transform + sortie | Cannot run Deploy sortie and Transform at once |
| Full player menu on profile | User chose hybrid |
| Pure scripted profile turns | User chose hybrid |
| Transform HP 0 → both permanently down | User chose revert safe |

## Consequences

- Content: `protocol_transform` + `TransformDefinition` per Navigator
- `ProtocolSystem` / `BattleState`: sideline snapshot, apply profile; block Protocol only **while** transform active
- `CombatController`: hybrid menu for profile; queue rebuild on transform/revert; restore snapshot on revert/end
- Combat UI: target picker, dual-name label, Revert action
- Tests: no Protocol during active transform/sortie; second Protocol after recharge; revert safe; sequential Deploy then Transform OK

## Related

- [ADR 023 — Protocol Deploy](023-protocol-deploy-sortie-summon.md)
- [Synchro Protocol](../docs/02-systems/synchro-protocol.md)
- [Navigator](../docs/02-systems/navigator.md)
- [Party & classes](../docs/02-systems/party-and-classes.md)
- [Combat](../docs/02-systems/combat.md)
- [ADR 006 — Team bar](006-union-team-bar.md)
- [ADR 007 — Navigator role](007-navigator-role.md)
