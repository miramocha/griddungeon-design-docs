# 00 — Vision

## Elevator pitch

Chart an unknown labyrinth from the first person — one grid step at a time. The **map fills in automatically** as you explore. Avoid or bait **FOEs** on the grid. Manage a six-person guild party, return to town before you're spent, and push deeper into the next stratum.

## Design pillars (Etrian Odyssey–first)

1. **Living map** — Floor, walls, doors, stairs, and FOEs reveal through exploration; map UI is read-only (no drawing tools).
2. **Grid exploration** — Discrete steps and turns; no action combat. Dungeon view + map panel work together.
3. **FOE tension** — Visible threats on the grid; routing around stronger FOEs is valid play.
4. **Guild party build** — Six core slots (3+3), aux summons/guests, swappable **Navigator** (Union + passives, off-formation).
5. **Hub pacing** — Town services between dives; depth is a deliberate choice, not a marathon.

## Inspirations

| Game | Take |
|------|------|
| ***Etrian Odyssey*** | **Primary:** auto-map presentation, FOEs, strata, guild classes, AGI combat, synthesis |
| *Wizardry* | Brutal identity optional; we use EO death/save model instead |
| *SMT / dungeon crawlers* | Weaknesses and buff stacking (light touch, later) |

## Player fantasy

- **Pathfinder** — Read the auto-map, thread FOE patrols, find shortcuts.
- **Guildmaster** — Curate six party slots and skill builds for each stratum.
- **Survivor** — Know when to dive deeper vs return to hub.

## Non-goals (early versions)

- **Manual map drawing tools** (walls, icons, notes, eraser)
- Action combat, QTEs, or real-time party control in battles
- Full 3D hub walk (menu hub is fine for MVP1)
- **Boost/Break** — out of scope; [Union](02-systems/union.md) covers team burst
- Subclass systems until core loop is proven
- **Dungeon gather / fishing minigames** — **MVP2** ([gathering & fishing](02-systems/gathering-and-fishing.md), [release scope](00-release-scope.md))
- Per-character Union gauges (using **team Union bar** instead — see [union](02-systems/union.md))
- Navigator leveling, equipment, or aura tiers ([navigator](02-systems/navigator.md) is unlock-only)

## Out of scope (project)

- **Online multiplayer, co-op, and async shared play** — single-player only
- **Boost/Break** (EO2 Force-style) — replaced by Union + Navigator
- **Exploration TP / step limits** (EO2-style) — unlimited labyrinth movement
- **Console/mobile** as primary — **PC first** ([ADR 008](../decisions/008-campaign-defaults.md))

## Tech target

- **Unity 6** + **URP** + **Input System** ([ADR 012](../decisions/012-unity-6-stack.md)); see [04 — Tech notes](04-tech-notes.md)

## Tone & setting (TBD)

Placeholder: settlement at the edge of a **Yggdrasil-like labyrinth** — one entrance, many strata, ecology changes per depth. Replace with setting brief when art exists.

## Success criteria (MVP1)

See [mvp1-spec.md](mvp1-spec.md) for full checklist. Prototype bar:

- [ ] Explore a test floor in FPV; **map auto-reveals** floor and walls on bump
- [ ] **FOE** appears on map when visible; combat on contact
- [ ] Win a fight with **6 party members** and **AGI turn order** visible
- [ ] Return to hub, save, heal, spend **skill point**, re-enter with **map intact**
- [ ] **Union bar** fills in combat; use one Union skill at 100% before AGI round

## Related docs

- [01 — Core loop](01-core-loop.md)
- [02 — Mapping](02-systems/mapping.md)
- [02 — Dungeon navigation](02-dungeon-navigation.md)
- [02 — Hub & services](02-systems/hub-and-services.md)
