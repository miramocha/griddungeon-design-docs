---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/combat
  - domain/ui
---
# ADR 045 — Combat Formation Switch

**Status:** Accepted (required slice)  
**Date:** 2026-07-01  
**Related:** [ADR 015](015-mvp1-combat.md) (round flow), [ADR 044](044-eo4-row-targeting-party-promote.md) (promote on kill — parallel), [custom party UI](../docs/04-dev/custom-party-ui.md)

## Context

Etrian Odyssey II lets the party **Switch** — spend a core’s turn to swap two formation slots mid-fight. Grid Dungeon’s hub **Formation** pane already uses pick-two slot UX on `PartyFormationFloater`; combat needs the same pattern as a **turn-cost command** queued in planning and resolved on the acting core’s AGI turn (like **Guard**).

EO IV **row promote** ([#377](https://github.com/miramocha/griddungeon-game/issues/377) / ADR 044) may land in parallel; this ADR locks **Formation** command behavior and documents promote interaction.

## Decision

### 1. Command cost and timing

| Rule | Choice |
|------|--------|
| **Cost** | Turn-cost — consumes the acting **core**’s AGI turn |
| **Queue** | During **command planning** with Attack / Guard / Skill / … |
| **Resolve** | On that core’s **AGI playback** turn (same beat as Guard) |
| **Synchro** | `SynchroGainPerCoreAction` (+0.15) on successful resolve — Guard pattern |
| **AGI queue** | Mid-round Formation does **not** rebuild the AGI queue |

### 2. UX — pick-two on combat floater

1. Player highlights a **living core** and picks **Formation** on the command rail.
2. Combat `PartyFormationFloater` enters **switch-pick** mode (aux dimmed; core slots 0–5 only).
3. **First slot** tap/focus + confirm; **second slot** completes the pick (same rules as hub Formation — empty-slot move, occupied swap, tap same slot cancels selection).
4. Command queues as **Formation** with the two **core indices**; planning advances to the next actor.
5. **Cancel:** `X` / Back clears pick mode without queuing (like target cancel).

**Summons / guests / aux:** Formation is **not** on summon or guest planning menus. **NPC scripted guests** never use Formation.

### 3. Scope — core slots 0–5 only

- Only **core grid slots** `0..5` (`BattleFormation.MaxCoreSlots`).
- **No aux** slot swapping in combat Formation.
- **Corpses** in core slots may be swapped (corpse trade / reposition dead ally).
- **Empty** core slots may be targets (move living member into empty cell).

### 4. Resolve-time rules (`FormationSwapRules` + `BattleFormationSwap`)

At **AGI resolve** (not at queue time):

1. **Revalidate** both indices are core slots `0–5`.
2. **Apply swap** on `BattleState.CoreSlots` — exchange occupants (including `null` and dead combatants).
3. Update **`SlotIndex`** and **`Row`** via shared `CoreSlotMetadata` (same mapping as hub `PartyRuntime`).
4. If the swap is a no-op (same index) or fails validation → turn still consumes; **no formation change** and **no Synchro gain** (see [griddungeon-game #381](https://github.com/miramocha/griddungeon-game/pull/381)).
5. **Dead switcher at AGI:** if the acting core is **dead** when their AGI slot arrives, the turn is **skipped** (existing dead-turn skip) — Formation does not resolve.

**No AGI rebuild:** slot order in the turn queue is unchanged; only roster **positions** update for targeting / UI.

### 5. Persist party order after battle

At **`EndBattle`**, `PartyFormationSync` reorders **`PartyRuntime`** core slots to match **`BattleState`** slot arrangement (by combatant id), then syncs HP / MP / Synchro as today.

Exploration formation after combat reflects in-fight swaps.

### 6. Promote interaction (ADR 044 / #377)

When **party row collapse / promote** exists:

| Beat | Owner |
|------|--------|
| **Enemy kill → promote** | Runs on **kill resolution** / row-collapse beat (before or after damage presentation per ADR 044) |
| **Formation** | Runs on the **queued core’s AGI turn** |

**Order:** Promote from a kill on enemy turn **N** completes before that round’s remaining AGI actions. A Formation queued in **planning** for core **A** resolves on **A**’s AGI slot — may be before or after a promote on the same round depending on AGI order; both apply to `BattleState` independently. **No AGI rebuild** after either.

If promote and Formation target the **same slot** in one round, **resolve order is AGI order** — whichever beat runs first wins that moment’s slot contents; the later beat applies to current state.

Document in tests: promote-then-switch and switch-then-promote on adjacent beats ([#378](https://github.com/miramocha/griddungeon-game/issues/378)).

### 7. Implementation layers

| Layer | Types |
|-------|--------|
| **Core** | `CombatCommand.Switch`, `FormationSwapRules`, `BattleFormationSwap`, `CoreSlotMetadata`, `PartyFormationSync` |
| **Runtime** | `CombatFormationSwapCoordinator`, `CombatController` planning + resolve, `OnFormationChanged` |
| **UI** | `cmd-switch`, `CombatFormationSwapPicker`, floater `--switch-pick` modifier, `TabbedPickerRailHints` |

**DRY:** Hub `PartyFormationCoordinator` uses `FormationSwapRules` for pick-two logic; battle apply uses `BattleFormationSwap`.

## Rejected

| Option | Why |
|--------|-----|
| Free mid-fight Formation (EO IV+) | Scope; turn cost is EO II default |
| Formation aux / guest slots | Core reposition only at launch |
| Rebuild AGI on Formation | Loses queued turn order; EO II keeps queue |
| Instant Formation on menu pick | Must match Guard / Attack resolve on AGI turn |

## Consequences

- [combat.md](../docs/02-systems/combat.md) — `Formation` in core command table
- Implementation: [griddungeon-game #378](https://github.com/miramocha/griddungeon-game/issues/378)
- Epic: [griddungeon-game #380](https://github.com/miramocha/griddungeon-game/issues/380)

## Related

- [Combat](../docs/02-systems/combat.md)
- [Items & inventory — party formation](../docs/02-systems/items-and-inventory.md)
- [ADR 044 — EO IV row targeting / promote](044-eo4-row-targeting-party-promote.md) (when authored)
