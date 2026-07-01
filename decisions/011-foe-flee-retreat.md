---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/foe
---
# ADR 011 — FOE Flee & Retreat Cell

**Status:** Accepted  
**Date:** 2026-05-20

## Context

FOE fights should be **escapable**, but fleeing must not let the party stay on the FOE’s cell. If there is no room to step back, retreat is impossible.

## Decision

1. **FOE encounters** (grid contact, mid-battle join, normal FOE fight) allow **Flee** command.
2. On **successful flee**, party is placed **1 cell backward** relative to current **facing** (same rule as exploration step back — no turn).
3. **FOE stays** on its grid cell; fight ends; exploration resumes on the retreat cell.
4. If the **retreat cell** is not walkable (wall, pit, blocked door, etc.) → **Flee disabled** in UI; cannot attempt.
5. **Random encounters** and **boss/event** fights use separate flee rules (FOE retreat push does not apply unless tagged as FOE fight).

## Rejected

| Option | Why |
|--------|-----|
| FOE fights inescapable | User wants escape with positional cost |
| Flee but stay on same cell | Defeats FOE avoidance fantasy |
| Push FOE back instead of party | Party retreats, FOE holds ground |

## Consequences

- `FoeEncounter.CanFlee` → `Grid.CanStepBackward(partyPos, facing)`
- `OnFleeSuccess` → `partyPos = backwardCell`
- Combat UI disables `CmdFlee` when retreat blocked

## Implementation (game)

- **Retreat cell:** `RetreatCellCalculator` (Core); `FoeSystem.CanRetreatFromFoe` for flee enable.
- **FOE-only pushback:** `CombatEntryContext.ShouldMovePartyToRetreatCell` (`Foe != null` + successful flee); random encounters do not move the party.
- **Post-combat placement:** `FoeFleeRetreatPlacement.TryResolvePostFleeCell` → `ExplorationPhaseController` on `Combat → Exploration`.

## Related

- [FOE encounters](../docs/02-systems/foe-encounters.md)
- [02 — Combat](../docs/02-systems/combat.md)
- [02 — Dungeon navigation](../docs/02-dungeon-navigation.md)
