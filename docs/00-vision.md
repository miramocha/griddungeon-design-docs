# 00 — Vision

## Elevator pitch

Lead a contract crew into an unknown labyrinth as their **Navigator** — on comms, off the formation grid, with no memory of who you were when the dive started. The **map fills in automatically** as the line advances. Avoid or bait **FOEs** on the grid. Direct six cores, return to hub before the channel goes cold, and push deeper as you **rediscover** what your link can do.

## Design pillars (Etrian Odyssey–first)

1. **Living map** — Floor, walls, doors, stairs, and FOEs reveal through exploration; map UI is read-only (no drawing tools).
2. **Grid exploration** — Discrete steps and turns; no action combat. Dungeon view + map panel work together.
3. **FOE tension** — Visible threats on the grid; routing around stronger FOEs is valid play.
4. **Guild party build** — Six core slots (3+3), aux summons/guests, swappable **Navigator** (Synchro Protocol + passives, off-formation).
5. **Hub pacing** — Town services between dives; depth is a deliberate choice, not a marathon.

## Inspirations

| Game | Take |
|------|------|
| ***Etrian Odyssey*** | **Primary:** auto-map presentation, FOEs, strata, guild classes, AGI combat, synthesis |
| ***Mary Skelter: Nightmares*** | **Secondary:** FPV tower crawl, map threats, reactive combat read, hub **place-making** (with EO menu loop) — [game references](00-game-references.md#mary-skelter--hub--base-secondary) |
| *Wizardry* | Brutal identity optional; we use EO death/save model instead |
| *SMT / dungeon crawlers* | Weaknesses and buff stacking (light touch, later) |

Full reference notes (scratchpad, not scope authority): **[00 — Game references](00-game-references.md)**.

## Player fantasy

- **Navigator (primary)** — Blank-state flight lead on guild channel; read the auto-map through the crew feed, thread FOE patrols, and **learn** Synchro / Protocol as the story proves them ([narrative POV](02-systems/narrative-pov.md)).
- **Guildmaster** — Curate six core slots and skill builds between dives (hub); fiction stays Navigator-voiced.
- **Survivor** — Know when to pull the line topside vs push deeper.

Exploration camera follows the **party on the grid**; identity and dialogue remain **Navigator-first person**, not a single core class.

## Non-goals (early versions)

- **Manual map drawing tools** (walls, icons, notes, eraser)
- Action combat, QTEs, or real-time party control in battles
- Full 3D hub walk (MVP1: menu hub; [menu-driven camera pan](02-systems/hub-and-services.md#hub-environment-presentation) is **post-MVP1**)
- **Boost/Break** — out of scope; [Synchro Protocol](02-systems/synchro-protocol.md) covers team burst
- Subclass systems until core loop is proven
- **Dungeon gather / fishing minigames** — **MVP2** ([gathering & fishing](02-systems/gathering-and-fishing.md), [release scope](00-release-scope.md))
- Per-character burst gauges (using **team Synchro Charge** instead — see [synchro-protocol](02-systems/synchro-protocol.md))
- Navigator leveling, equipment, or aura tiers ([navigator](02-systems/navigator.md) is unlock-only)

## Out of scope (project)

- **Online multiplayer, co-op, and async shared play** — single-player only
- **Boost/Break** (EO2 Force-style) — replaced by Synchro Protocol + Navigator
- **Exploration TP / step limits** (EO2-style) — unlimited labyrinth movement
- **Console/mobile** as primary — **PC first** ([ADR 008](../decisions/008-campaign-defaults.md))

## Tech target

- **Unity 6** + **URP** + **Input System** ([ADR 012](../decisions/012-unity-6-stack.md)); see [04 — Tech notes](04-tech-notes.md)

## Tone & setting

**One line:** A guild-licensed crew maps a living **undercity** beneath a familiar metropolis — concrete, water, and things that were never meant to stay down there.

**Municipal underworks (MVP1 art direction):** Modern, grounded, **not sci-fi**. Strata read as **infrastructure + neglect** (maintenance tunnels, flood channels, sealed transit) rather than castle fantasy or cyberpunk. FOE and place names stay urban (`alley_stalker`, `gutter_crow`, **Flooded Underpass**). Hub **guild** = city **contract crew**, not medieval order.

**Yggdrasil-like labyrinth** structure stays: one gate, many strata, ecology shifts per depth ([dungeons](03-content/dungeons-and-encounters.md)).

**UI:** Warm charcoal panels, off-white type, **amber-gold** accents (Synchro / active turn) — schematic map like a **transit or architectural plan**, not neon HUD ([map cell art](02-systems/map-cell-art.md#visual-tone-municipal-underworks)).

## Success criteria (MVP1)

See [archive/mvp1-spec.md](archive/mvp1-spec.md) for full checklist. Prototype bar:

- [ ] Explore a test floor in FPV; **map auto-reveals** floor and walls on bump
- [ ] **FOE** appears on map when visible; combat on contact
- [ ] Win a fight with **6 party members** and **AGI turn order** visible
- [ ] New game: B1F movement tutorial → hub party setup → tutorial dive from B1F gate
- [ ] Return to hub via **in-world** paths only (gate stairs, items, exits/gates, events, defeat) — not pause menu; pause → **quit to title**
- [ ] After hub return: save, heal, re-enter with **map intact**; spend **skill points** in hub or in labyrinth when not in combat / story / cutscene
- [ ] **Synchro** tutorial: B2F FOE crisis AOE → VN → guided `protocol_strike` → hub warp

## Related docs

- [Narrative POV — Navigator, blank state](02-systems/narrative-pov.md)
- [00 — Game references](00-game-references.md)
- [01 — Core loop](01-core-loop.md)
- [02 — Mapping](02-systems/mapping.md)
- [02 — Dungeon navigation](02-dungeon-navigation.md)
- [02 — Hub & services](02-systems/hub-and-services.md)
