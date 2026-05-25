# FOE Encounters

Grid **FOEs** — visible on the labyrinth, fought on contact or via [mid-battle join](chain-foe-battle.md). This doc covers **contact, flee, and grid position** rules.

## Starting an FOE fight

| Entry | Trigger |
|-------|---------|
| **Contact** | Party **enters** FOE cell (exploration step) |
| **Mid-battle join** | FOE reaches party cell during combat ([ADR 010](../../decisions/010-chain-foe-battle.md)) |

Fight anchor: party **exploration cell** when combat begins (frozen for fight duration).

## Flee from FOE fights (locked)

FOE encounters are **escapable** ([ADR 011](../../decisions/011-foe-flee-retreat.md)).

### Retreat cell check

Before flee is offered (or on selecting Flee):

```
retreatCell = partyCell + backward(facing)
```

| `retreatCell` | Flee |
|---------------|------|
| **Walkable** | Allowed (subject to normal flee success roll) |
| **Wall / blocked** | **Disabled** — “No escape route” (UI greyed `5` / Flee) |

**Backed to a wall:** party faces FOE, wall behind → retreat cell blocked → **cannot flee**.

### On successful flee

1. Combat ends (FOE fight only — not a wipe).
2. Party moves to **retreatCell** (one step back, **facing unchanged**).
3. **FOE remains** on its cell (still on map, can be fought again).
4. Exploration resumes; FOE patrol / step rules apply again.

```
Before:  [wall][party+FOE same cell?] — contact fight party ON foe cell
         Often: party steps into FOE cell → fight starts
After flee success: party on cell behind where they were, facing same way, FOE still ahead on FOE cell
```

If fight started with party **on** FOE cell: retreat = cell **behind** party (away from FOE along backward axis).

### On failed flee

- Wasted turn (existing flee rules); party cell unchanged.
- FOE still on map.

### Flee not available

| Case | Flee |
|------|------|
| Retreat cell blocked | Disabled |
| Story / boss `noFlee` flag | Disabled |
| Event fights (designer) | Per encounter tag |

## Comparison: random encounters

| | **FOE fight** | **Random encounter** |
|---|---------------|----------------------|
| Flee allowed | Yes (if retreat cell open) | Yes (generic flee rules) |
| Position after flee | **Forced 1 cell back** | Same cell (no grid pushback) |
| FOE on map during | FOE unchanged on cell | N/A |

## Mid-battle join + flee

Joined FOEs are part of the same encounter; flee from an FOE fight uses the same **retreat cell** check from party’s frozen fight anchor and **facing**.

## UI

- Flee disabled state: tooltip **“No escape route behind you.”**
- Optional: show retreat cell highlight on map when Flee hovered (debug/assist mode).

## MVP1 implementation (game)

| Rule | Owner |
|------|--------|
| Retreat cell math | `RetreatCellCalculator` (Core) |
| Walkable retreat check / flee UI enable | `FoeSystem.CanRetreatFromFoe` → `RetreatCellCalculator.IsRetreatCellWalkable` |
| FOE contact vs random flee placement | `CombatEntryContext.ShouldMovePartyToRetreatCell` — **true** only when `Foe != null` and `BattleResult.Flee` |
| Post-flee exploration cell | `FoeFleeRetreatPlacement.TryResolvePostFleeCell` (Core); `ExplorationPhaseController` applies placement on combat end |

Random encounters: flee succeeds but party **stays on fight anchor**. FOE contact: party moves **one cell backward** when retreat cell is walkable ([#94](https://github.com/miramocha/griddungeon-game/pull/94)).

### Tutorial FOE (S1 — `foe_alley_stalker`)

Scripted first FOE on `s1_B2F` — not a normal kill-to-win fight ([campaign S1](../03-content/campaign/s1-intro.md), [synchro § S1 gating](synchro-protocol.md#s1-tutorial-gating-first-foe), [dungeons — B2F](../03-content/dungeons-and-encounters.md#s1_b2f--collapsed-avenues-bind--poison--patrol-foe)):

| Rule | Detail |
|------|--------|
| **Unbeatable** | FOE cannot die until Protocol finisher (`tutorialUnbeatable` until step F) |
| **Crisis** | On trigger (2 core turns OR FOE at HP floor): FOE **scripted AOE** → all living core **HP = 1** (fake wipe, not GAME OVER) |
| **Flee** | `noFlee: true` until tutorial completes |
| **Victory** | Player **`protocol_strike`** kills FOE; then **hub warp** — not retreat-on-B2F ([story events § S1 flow](story-events.md#s1-tutorial-flow-foe_alley_stalker)) |
| **Story** | `s1_b2f_stalker_briefing` (Event cell, pre-fight), `s1_synchro_protocol_unlock` (post-crisis), `s1_tutorial_hub_return` (post-kill) — [ADR 028](../../decisions/028-story-visual-novel-events.md) |
| **Guided HUD** | `s1_combat_guided_protocol` after unlock VN — [guided-tutorial](guided-tutorial.md), [S1 beats](../03-content/campaign/s1-guided-tutorials.md) |
| **Contact** | Same cell rules as normal FOE; encounter group `TutorialFirstFoe` + `CombatTutorialHudRules` (S1 stalker) |

## Related docs

- [02 — Dungeon navigation](../02-dungeon-navigation.md)
- [Mapping — map during combat (consider / explore)](mapping.md#consider--explore--map-during-combat)
- [02 — Combat](combat.md)
- [FOE mid-battle join](chain-foe-battle.md)
- [ADR 011 — FOE flee retreat](../../decisions/011-foe-flee-retreat.md)
