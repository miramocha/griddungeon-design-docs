# Hub & Services (Guild town)

Exploration alternates with a **fixed hub** at the labyrinth entrance — not an open overworld. EO's town loop: prepare, dive one stratum, return before overextending.

## Hub locations (MVP1)

| Service | Function |
|---------|----------|
| **Explorers Guild** | Create/recruit **core** characters; register **6-member** party; allocate **skill points**; view class skill trees |
| **Navigator Office** | View **unlocked** Navigators; assign **active** Navigator for next dive; preview aura + Union kit ([navigator](navigator.md)) |
| **Shop** | Buy/sell weapons, armor, consumables |
| **Hospital** | Restore HP/MP; cure **all standard combat ailments/debuffs**; revive fallen members (fee) — see [status & buffs](combat-status-and-buffs.md) |
| **Inn / Camp desk** | Save game (primary save point) |
| **Quest counter** | Accept kill/gather/floor reach quests (optional MVP1) |
| **Synthesis** (**MVP2**) | Fuse dungeon materials → equipment — requires [gathering & fishing](gathering-and-fishing.md) |

No real-time hub walking required for prototype — menu tree is fine.

### Service UI motion

Hub menus use the same **reactive, blocking** bar as combat and exploration ([tech notes — UI reactivity](../04-tech-notes.md#ui-reactivity)).

| Event | UI reaction (MVP1) | Blocks until done |
|-------|-------------------|-------------------|
| Open / close service screen | Panel **fade/slide** | No — navigation only |
| Inn save | Brief **confirm flash** + text | Yes — before another service action |
| Hospital heal / revive | HP/MP bars **lerp**; ailment icons **fade out** | Yes |
| Shop buy / sell | Gold + stock row **pulse**; inventory slot update | Yes |
| Guild assign slot / spend skill point | Portrait **slide** into slot; skill node **highlight** | Yes |
| Navigator Office pick active | Portrait **glow**; aura preview **fade in** | Yes |
| Leave hub → stratum | Transition **fade** (pairs with phase change) | Yes — until exploration phase ready |

### Guild vs Navigator Office

| | **Explorers Guild** | **Navigator Office** |
|---|---------------------|------------------------|
| **Who** | Six **core** guild members | **Navigators** (party leads, off-formation) |
| **Recruitment** | Yes — create/recruit core roster | **No** — unlock via strata / quests / events |
| **Party prep** | Formation, equipment, skill trees | Pick **one active** Navigator + aura/Union preview |
| **In labyrinth** | Fight, explore, earn XP | Union execution + passives only |

Prepare at **both** before entering the stratum (order in UI flexible).

## Macro loop (EO-aligned)

```
Hub → Guild (party/skills) + Navigator Office (active lead) + shop/equip
    → Enter stratum — spawn rule per stratum; Synchro **100%** on exit except S1 before first FOE ([synchro](../02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe))
    → Explore (auto-map) → Fight (random + FOE) → Gather loot
    → Retreat via first-floor stairs up (mouth) or Return thread when low
    → Hospital + shop + guild + Navigator Office → Repeat
```

**New game exception:** Stratum 1 starts with **Act 1 on `s1_B1F`** (movement, no hub yet) — see [S1 campaign intro](../03-content/campaign/s1-intro.md).

## Stratum 1 intro

Full three-act flow, save flags, and entry rules: **[campaign/s1-intro.md](../03-content/campaign/s1-intro.md)**.

**Act 2 (this doc):** first hub visit after Act 1 — unlock services, **Explorers Guild** fills **6 core** slots, **Navigator Office** assigns `guild_handler`, inn save; enable **Enter Stratum 1** when `s1_party_ready`. Hub only — no labyrinth grid, no combat.

**Act 3 from hub:** **Enter Stratum 1** → always **B1F mouth** `(10, 2)`; Synchro **0%** until mid–first FOE on B2F ([synchro § S1 gating](synchro-protocol.md#s1-tutorial-gating-first-foe)).

## Stratum structure

- Labyrinth divided into **strata** (biome-themed zones), each with multiple **floors**.
- Example: Stratum 1 "Fallen District" — floors B1F–B5F (MVP1: B1F–B3F + boss on B3F).
- **Stratum 2+:** hub **Enter Stratum** warps to that stratum’s **warp gate** on its entrance floor ([dungeons](../03-content/dungeons-and-encounters.md#stratum-entry--first-floor-stairs-locked)).
- **First floor mouth stairs up:** return to **hub**, or to **deepest unlocked floor of the previous stratum** (S1 mouth: hub only).
- Hub may **remember deepest unlocked floor** per stratum for resume after tutorial (post-MVP1 tuning).

## Quests (optional MVP1)

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

- [Release scope](../00-release-scope.md)
- [Gathering & fishing (MVP2)](gathering-and-fishing.md)
- [01 — Core loop](../01-core-loop.md)
- [Character progression](character-progression.md)
- [Navigator](navigator.md)
- [Union (team bar)](synchro-protocol.md)
- [03 — Dungeons & encounters](../03-content/dungeons-and-encounters.md)
