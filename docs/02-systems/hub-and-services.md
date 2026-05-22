# Hub & Services (Guild town)

Exploration alternates with a **fixed hub** at the labyrinth entrance — not an open overworld. EO's town loop: prepare, dive one stratum, return before overextending.

## Hub locations (MVP1)

| Service | Function |
|---------|----------|
| **Explorers Guild** | Create/recruit **core** characters; register **6-member** party; allocate **skill points**; view class skill trees |
| **Navigator Office** | View **unlocked** Navigators; assign **active** Navigator for next dive; preview aura + Protocol kit ([navigator](navigator.md)) |
| **Shop** | Buy/sell weapons, armor, consumables |
| **Hospital** | Restore HP/MP; cure **all standard combat ailments/debuffs**; revive fallen members (fee) — see [status & buffs](combat-status-and-buffs.md) |
| **Inn / Camp desk** | Save game (primary save point) |
| **Quest counter** | Accept kill/gather/floor reach quests (optional MVP1) |
| **Synthesis** (**MVP2**) | Fuse dungeon materials → equipment — requires [gathering & fishing](gathering-and-fishing.md) |
| **Side expedition** (**MVP3**) | Travel to unlocked **non-strata** grid maps — [side dungeons](side-dungeons.md), [ADR 022](../../decisions/022-side-dungeons-mvp3.md) |

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
| **Party prep** | Formation, equipment, skill trees | Pick **one active** Navigator + aura/Protocol preview |
| **In labyrinth** | Fight, explore, earn XP | Protocol execution + passives only |

Prepare at **both** before entering the stratum (order in UI flexible).

## Macro loop (EO-aligned)

```
Hub → Guild (party/skills) + Navigator Office (active lead) + shop/equip
    → Enter stratum — spawn rule per stratum; Synchro **100%** on exit except S1 before first FOE ([synchro](synchro-protocol.md#s1-tutorial-gating-first-foe))
    → Explore (auto-map) → Fight (random + FOE) → Gather loot
    → Retreat via first-floor stairs up (mouth) or Return thread when low
    → Hospital + shop + guild + Navigator Office → Repeat
    → (MVP3) Side expedition — optional non-strata maps; exit → hub only ([side dungeons](side-dungeons.md))
```

**New game exception:** Stratum 1 starts with **Act 1 on `s1_B1F`** (movement, no hub yet) — see [S1 campaign intro](../03-content/campaign/s1-intro.md).

## Stratum 1 intro

Full three-act flow, save flags, and entry rules: **[campaign/s1-intro.md](../03-content/campaign/s1-intro.md)**.

**Act 2 (this doc):** first hub visit after Act 1 — unlock services, **Explorers Guild** fills **6 core** slots, **Navigator Office** assigns `guild_handler`, inn save; enable **Enter Stratum 1** when `s1_party_ready`. Hub only — no labyrinth grid, no combat.

**Act 3 from hub:** **Enter Stratum 1** → always **B1F mouth** `(10, 2)`; Synchro **0%** until mid–first FOE on B2F ([synchro § S1 gating](synchro-protocol.md#s1-tutorial-gating-first-foe)).

## Stratum structure

- Labyrinth divided into **strata** (biome-themed zones), each with multiple **floors**.
- Example: Stratum 1 "Fallen District" — floors B1F–B5F (MVP1: B1F–B3F + boss on B3F).
- **Stratum entry (locked):** party always starts at the **beginning** of a stratum (entrance floor). **S1:** no warp gate — hub **Enter Stratum 1** → B1F mouth; **S2+:** hub entry only after that stratum’s **warp gate** is unlocked in-world, then warp to the gate cell on the entrance floor ([dungeons](../03-content/dungeons-and-encounters.md#stratum-entry--warp-gates-locked)).
- **First-floor mouth `stairsUp`:** → **hub** only (all strata).

## Quests (optional MVP1)

| Type | Objective | Example reward |
|------|-----------|----------------|
| Hunt | Kill N of enemy type | Gold, item |
| Survey | Reach floor | Unlock shop stock |
| Gather | Bring materials | Synthesis unlock |

## Save model (EO-aligned)

- **Save at hub** (inn) — primary.
- **No save in labyrinth** for classic feel; optional **camp item** rare consumable for mid-stratum save (late feature).
- Wipe → GAME OVER → load last hub save; **map data for strata already visited persists**.

## Hub travel (stratum vs side)

| Destination | Hub action | Entry API (draft) |
|-------------|------------|-------------------|
| **Stratum** labyrinth | **Enter Stratum** *N* | `LeaveHub(stratumId, floorId)` |
| **Side dungeon** (MVP3) | **Side expedition** → pick location | `EnterSideDungeon(locationId, floorId)` |

Strata: warp-gate unlock + beginning-only hub entry (S2+); S1 mouth entry. Side dungeons use **menu entry only** and **hub-only** exit — see [side dungeons](side-dungeons.md).

## Related docs

- [Side dungeons (MVP3)](side-dungeons.md)
- [Release scope](../00-release-scope.md)
- [Gathering & fishing (MVP2)](gathering-and-fishing.md)
- [01 — Core loop](../01-core-loop.md)
- [Character progression](character-progression.md)
- [Navigator](navigator.md)
- [Synchro Protocol (team bar)](synchro-protocol.md)
- [03 — Dungeons & encounters](../03-content/dungeons-and-encounters.md)
