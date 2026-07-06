---
tags:
  - path/decisions
  - type/adr
  - scope/optional
  - status/accepted
  - domain/combat
---
# ADR 044 — EO IV row targeting + party auto-promote

**Status:** Accepted (optional — spec only; implementation [#377](https://github.com/miramocha/griddungeon-game/issues/377))  
**Date:** 2026-07-06  
**Related:** [ADR 015](015-mvp1-combat.md) (round flow), [ADR 045](045-combat-formation-switch.md) (Formation resolve order), [combat.md](../docs/02-systems/combat.md)

## Context

Etrian Odyssey IV uses **front/back rows** for both parties. Enemies pick targets probabilistically by row; living back-row party cores **promote** to front when the front row is wiped. Grid Dungeon already collapses **enemy** rows via `EnemyRowCollapse` on kill; **party** auto-promote and EO-style enemy targeting are not shipped ([#377](https://github.com/miramocha/griddungeon-game/issues/377)).

**Today:** `ValidTargetCalculator` hard front-first for party targets; no `PartyRowCollapse`; enemy AI uses front-gate rules from [ADR 015](015-mvp1-combat.md).

## Decision

### 1. Party auto-promote

When **no living cores** remain in the front row (`SlotIndex` 0–2), living back-row cores (`3–5`) **promote** to front:

- **Column order** within each row (mirror `EnemyRowCollapse`).
- Runs on **kill resolution** / row-collapse beat (timing paired with presentation — see [combat.md § UI motion](../docs/02-systems/combat.md#ui-motion--feedback)).
- `BattleState` slot indices update; UI + arena anchors refresh on promote beat.

### 2. Enemy targeting (probabilistic row roll)

Replace hard front-first enemy target pick with EO IV-style roll:

| Roll | Weight | Target pool |
|------|--------|-------------|
| Front row | **75%** | Living party cores in front row |
| Back row | **20%** | Living party cores in back row |
| Random living ally | **5%** | Any living party core |

Within the chosen row, weight by **highest current HP** (ties broken deterministically).

**Hooks (stub at launch):** aggro, taunt, decoy — document extension points; full Vanguard Decoy Sign simulation is out of scope.

### 3. Melee reach

| Attacker | Target |
|----------|--------|
| **Back-row melee** | Cannot hit enemy **back** row — front row must be cleared or skill has `Pierce` / ranged |
| **Front-row melee** | Front-first gate for enemy back row (existing pierce/ranged exceptions per skill) |
| **Symmetric** | Same reach rules when enemies melee party rows |

`Pierce` and ranged `TargetKind` skills bypass row gates per [class-skills](../docs/03-content/class-skills.md).

### 4. Phase 1b (optional follow-up)

EO IV **50% melee damage** when attacker and target are in different rows — optional Phase 1b on [#377](https://github.com/miramocha/griddungeon-game/issues/377).

## Implementation layers (when built)

| Layer | Types |
|-------|--------|
| **Core** | `PartyRowCollapse`, `EnemyPartyTargetPicker`, reach checks in `ValidTargetCalculator` / `ActionResolver` |
| **Runtime** | `CombatController` promote beat after enemy kill; AI target pick |
| **Tests** | `PartyRowCollapseTests`, `EnemyPartyTargetPickerTests` |

## Rejected

| Option | Why |
|--------|-----|
| Keep hard front-first forever | Required slice ships ADR 015 front-gate; EO IV rules are optional ([#377](https://github.com/miramocha/griddungeon-game/issues/377)) |
| Promote on Formation Switch | ADR 045 — separate resolve beat |
| Full aggro simulation at launch | Stub hooks only |

## Consequences

- [combat.md](../docs/02-systems/combat.md) — battle layout, targeting, row collapse cross-links
- [ADR 015](015-mvp1-combat.md) — note enemy hard front-gate superseded by aggro picker when #377 ships
- Implementation: [griddungeon-game #377](https://github.com/miramocha/griddungeon-game/issues/377) (optional — detached from closed epic [#379](https://github.com/miramocha/griddungeon-game/issues/379))

## Related

- [Combat](../docs/02-systems/combat.md)
- [ADR 045 — Formation Switch](045-combat-formation-switch.md)
- [Game references — EO IV rows](../docs/00-game-references.md)
