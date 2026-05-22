# ADR 020 — Team burst naming (retire “Union”)

**Status:** Accepted  
**Date:** 2026-05-21 (amended 2026-05-21 — **Synchro Charge** resource term)  
**Supersedes working name in:** [ADR 006 — Team burst bar](006-union-team-bar.md) (mechanics unchanged)

## Context

MVP1 team burst uses a shared 0–100% bar and Navigator-executed skills ([synchro-protocol.md](../docs/02-systems/synchro-protocol.md), implemented in griddungeon-game #10). **Union** was a placeholder (EO-inspired). We want a high-tech / JRPG label that fits the **Navigator** commander fantasy.

## Shortlist (evaluated)

| Candidate | Player-facing | Bar UI | Skill IDs | Notes |
|-----------|---------------|--------|-----------|--------|
| **Synchro Protocol** | Synchro Protocol | Synchro / Protocol menu | `protocol_*` | Navigator issues protocols; core synchronize — **selected** |
| Resonance | Resonance | Resonance | `resonance_*` | Strong JRPG tone; weak “command” read |
| Grid Link | Grid Link | Link | `link_*` | On-brand; “link” overloaded |
| Signal Lock | Signal Lock | Signal | `signal_*` | Clear at 100%; less grandeur |
| Convergence | Convergence | Convergence | `convergence_*` | Party-as-one; long bar label |

## Decision (locked)

| Field | Value |
|-------|--------|
| **System name** | Synchro Protocol |
| **Team resource (design / docs)** | **Synchro Charge** (0–100% party pool) — parallel to per-character **MP** spent on skills |
| **Team action** | **Protocol** — Navigator executes when charge is 100%; core member spends their AGI turn to invoke |
| **UI meter label** | **Synchro** (short; not “Synchro Charge” on the HUD) |
| **Content ID prefix** | `protocol_` |
| **C# module folder / root type** | `Protocol` (`ProtocolSystem`, `ProtocolResolver`, …) |
| **C# / save field names** | **`SynchroBar`**, **`SynchroBarDelta`** — **no rename** to `SynchroCharge` in MVP1; maps to Synchro Charge in docs ([synchro-protocol.md](../docs/02-systems/synchro-protocol.md)) |
| **MVP1 skill IDs** | `protocol_strike`, `protocol_mend` (was `union_strike`, `union_mend`) |

Presentation:

- Meter: **Synchro 100%** (shows Synchro Charge fill level)
- Command menu: **Protocols** (Navigator kit)
- Combat command: `CombatCommand.Protocol` + skill id

### Resource vs action (locked vocabulary)

| | Core six | Party / Navigator |
|---|----------|-------------------|
| Resource | MP | **Synchro Charge** |
| Action | Skill | **Protocol** |
| Spend | MP per skill | Full charge → 0% on Protocol |

## Consequences

- Full rename in `griddungeon-game` (types, content IDs, save field, input actions, tests).
- Renamed system doc: [synchro-protocol.md](../docs/02-systems/synchro-protocol.md); cross-links updated.
- [ADR 006](006-union-team-bar.md) amended to reference Synchro Protocol; filename retained for link stability (optional rename later).

## Related

- [Synchro Protocol system](../docs/02-systems/synchro-protocol.md)
- [Navigator](007-navigator-role.md)
- [mvp1-spec §4](../docs/mvp1-spec.md#4-mvp1-navigator--synchro-protocol-placeholder-content)
