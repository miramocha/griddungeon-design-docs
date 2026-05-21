# Hub & Services (Guild town)

Exploration alternates with a **fixed hub** at the labyrinth entrance — not an open overworld. EO's town loop: prepare, dive one stratum, return before overextending.

## Hub locations (MVP)

| Service | Function |
|---------|----------|
| **Explorers Guild** | Create/recruit characters, rename, register party, view class skills |
| **Shop** | Buy/sell weapons, armor, consumables |
| **Hospital** | Restore HP/MP; cure status; revive fallen members (fee) |
| **Inn / Camp desk** | Save game (primary save point) |
| **Quest counter** | Accept kill/gather/floor reach quests (optional MVP) |
| **Synthesis** (phase 2) | Fuse materials → equipment (EO crafting loop) |

No real-time hub walking required for prototype — menu tree is fine.

## Macro loop (EO-aligned)

```
Hub → Equip / skills / buy consumables → Enter stratum at saved floor
    → Explore (auto-map) → Fight (random + FOE) → Gather loot
    → Retreat via stairs or Ariadne thread (return item) when low
    → Hospital + shop + guild → Spend XP on skills → Repeat
```

## Stratum structure

- Labyrinth divided into **strata** (biome-themed zones), each with multiple **floors**.
- Example: Stratum 1 "Emerald Grove" — floors B1F–B5F, then stratum boss.
- Hub stair **remembers deepest unlocked floor** per stratum.

## Quests (optional MVP)

| Type | Example reward |
|------|----------------|
| Hunt | Kill N of enemy type | Gold, item |
| Survey | Reach floor | Unlock shop stock |
| Gather | Bring materials | Synthesis unlock |

## Save model (EO-aligned)

- **Save at hub** (inn) — primary.
- **No save in labyrinth** for classic feel; optional **camp item** rare consumable for mid-stratum save (late feature).
- Wipe → GAME OVER → load last hub save; **map data for strata already visited persists**.

## Related docs

- [01 — Core loop](../01-core-loop.md)
- [Character progression](character-progression.md)
- [03 — Dungeons & encounters](../03-content/dungeons-and-encounters.md)
