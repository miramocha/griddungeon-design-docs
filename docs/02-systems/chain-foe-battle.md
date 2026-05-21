# FOE Mid-Battle Join

When [FOE combat patrol](combat.md#optional-later-foe-movement-during-combat) is on ([ADR 005](../../decisions/005-foe-combat-patrol.md)), a grid FOE can **enter the current fight** instead of waiting for a separate encounter after victory.

> Formerly drafted as post-victory “chain FOE”; superseded by [ADR 010](../../decisions/010-chain-foe-battle.md).

## Scenario

```
Party fights random encounter on cell A (exploration frozen)
    → End of combat round: FOE patrol moves onto cell A
    → That FOE joins the ongoing battle as an enemy
    → Only one FOE joins per round; fight continues in one encounter
```

## Locked rules

| Rule | Detail |
|------|--------|
| **Mid-battle join** | **Yes** — FOE adds to **current** encounter |
| **One at a time** | **Max 1 FOE join per combat round** |
| **No post-victory chain** | No second FOE fight after win for the same overlap; resolve inside the battle |
| **Requires patrol** | FOE must reach party cell via [ADR 005](../../decisions/005-foe-combat-patrol.md) (or start fight on FOE cell via normal contact) |

## Trigger

At **end of combat round**, after [FOE patrol tick](../../decisions/005-foe-combat-patrol.md), before victory check:

1. For each living FOE on the party’s exploration cell **not already in this encounter**:
2. Select **at most one** to join this round (see priority below).
3. Spawn that FOE’s enemy group into the battle (usually the FOE’s authored group).
4. FOE **removed from grid** as an independent map entity while in fight (returns on flee/wipe rules if needed — stays dead on victory).

If **multiple FOEs** share the cell same round: **one joins**; others wait for a **later round** if still on cell and fight continues.

### Join priority (same round, same cell)

| Priority | Pick |
|----------|------|
| 1 | Highest tier (red > yellow > green) |
| 2 | Tie-break: lowest `foeInstanceId` (stable) |

## Joined FOE in combat

| Topic | Rule |
|-------|------|
| **Formation** | Added to **enemy side** (front row first empty, else back) |
| **AGI** | **Locked:** first turn is **next combat round** — no action the round it joins |
| **Loot / XP** | Included in encounter rewards on victory |
| **Codex** | Counts as FOE fight for drops/XP tuning |
| **UI** | Combat log: `«FOE name» joined the battle!` ; portrait slides in |
| **Map** | FOE icon on map follows “in combat” state or hides until resolved — **visibility during fight** under explore ([mapping § Consider / explore](mapping.md#consider--explore--map-during-combat)) |

## End-of-round order (updated)

```
1. [Status / buff end-of-round ticks](combat-status-and-buffs.md#timing-model); summon duration −1
2. Optional FOE patrol (ADR 005) — 1 cell per FOE
3. Mid-battle join check — max 1 FOE
4. Wipe / victory check
5. If continuing: rebuild AGI queue for next round
```

## Victory / flee / wipe

| End | Behavior |
|-----|------------|
| **Victory** | All enemies dead (including mid-join FOEs); one reward screen; resume exploration on cell A |
| **Flee** | Party moves **1 cell back** if walkable; flee **disabled** if wall behind ([foe-encounters](foe-encounters.md)) |
| **Wipe** | GAME OVER |

No extra FOE fight after victory for FOEs that already joined mid-battle.

## When ADR 005 off (floor flag)

- FOEs **do not move** during combat → mid-battle join **disabled**.
- FOEs still start fights via **exploration contact** only.

**MVP1:** Patrol + join **off** — stub `TryMidBattleFoeJoin()`; enable in **MVP2** with `foeCombatPatrol` per [ADR 015](../../decisions/015-mvp1-combat.md).

## UI / presentation

- Brief alert banner when join occurs (tier color).
- Turn order strip updates **next round** with new enemy chevrons.
- Optional: cinematic `Fixed` join VFX for red-tier FOEs only.

## Resolved

- Joined FOE acts **next combat round** (not join round).

## Balance notes

- Long fights near patrolling FOEs escalate danger organically.
- Cap of **1 join / round** prevents instant multi-FOE dogpile.
- Designer: avoid stacking many patrol paths on one choke cell without intent.

## Related docs

- [ADR 005 — FOE combat patrol](../../decisions/005-foe-combat-patrol.md)
- [ADR 010 — FOE mid-battle join](../../decisions/010-chain-foe-battle.md)
- [02 — Combat](combat.md)
- [03 — Dungeons & encounters](../03-content/dungeons-and-encounters.md)
