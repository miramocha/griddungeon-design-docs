# Release Scope

Feature delivery for **Grid Dungeon**. **Implementation status** lives on the [Codename: GridDungeon project board](https://github.com/users/miramocha/projects/3) — filter by `required` / `optional` issue labels.

| Term | Meaning |
|------|---------|
| **Required** | First playable — hub ↔ stratum loop, combat, map, FOEs, Synchro Protocol, Navigator |
| **Optional** | Shippable later without blocking the required slice |
| **Later** | Deferred polish, extra classes, full systems, accessibility |

> **Legacy terminology:** Older docs and ADRs say **MVP1** (= required), **MVP2/MVP3** (= optional). [archive/mvp1-spec.md](archive/mvp1-spec.md) is a historical snapshot only.

---

## Required (first playable)

**Goal:** Hub ↔ one stratum loop with combat, map, FOEs, Synchro Protocol, Navigator.

| In scope | Out of scope |
|----------|----------------|
| Grid exploration + auto-map ([ADR 002](../decisions/002-mapping-model.md)) | Fishing / gather **minigames** (optional) |
| FOE step patrol + contact fights ([ADR 003](../decisions/003-foe-step-patrol.md)) | [FOE combat patrol](../decisions/005-foe-combat-patrol.md) + [mid-battle join](../decisions/010-chain-foe-battle.md) (optional) |
| AGI combat, 6 core + aux layout, Synchro Charge | Synthesis hub (optional) |
| Navigator + Protocol ([ADR 006](../decisions/006-union-team-bar.md), [007](../decisions/007-navigator-role.md)) | Full status roster ([combat-status-and-buffs](02-systems/combat-status-and-buffs.md) — subset only) |
| Hub: Explorers Guild, Navigator Office, shop, hospital, inn save | 3D hub walk; hub **menu-driven camera pan** ([hub environment](02-systems/hub-and-services.md#hub-environment-presentation)) — **later** |
| **Floor transition vignette** (stairs / hub enter; black + 3D threshold, Cinemachine) | Unique beat per floor pair; hub service camera pans |
| Chest loot; gather **instant loot** (no minigame) | Fishing + gather **minigame** (optional) |
| PC input defaults ([ADR 009](../decisions/009-input-bindings-pc.md)) | Rebind UI (defaults-only OK for required slice) |

**Locked rules:** [ADR 014](../decisions/014-mvp1-exploration-map.md) (exploration & map) · [ADR 015](../decisions/015-mvp1-combat.md) (combat)

**Content slice:** Stratum 1 B1F–B3F vertical slice — [dungeons & encounters](03-content/dungeons-and-encounters.md), [S1 intro](03-content/campaign/s1-intro.md), [01 — Core loop](01-core-loop.md)

---

## Optional features

Optional work does not block the required slice. Grouped by theme; each feature doc notes scope at the top.

### Material loop (gather, fish, synthesis)

**Goal:** EO-style **material loop** — explore for resources, return to hub, craft/equip.

| Feature | Doc |
|---------|-----|
| **Dungeon gathering minigame** (chop, mine, forage) | [gathering & fishing](02-systems/gathering-and-fishing.md) |
| **Dungeon fishing minigame** (pond/stream tiles) | [gathering & fishing](02-systems/gathering-and-fishing.md) |
| **Synthesis** at hub | [character progression](02-systems/character-progression.md), [hub](02-systems/hub-and-services.md) |
| Gather/fish nodes on map after use | [mapping](02-systems/mapping.md) |
| Gather quests + material drops | [dungeons & encounters](03-content/dungeons-and-encounters.md) |

**Also optional in this wave:** [cinematic + QTE skills](02-systems/combat-presentation.md), full ailment list, gamepad, pathfind **avoid FOE cells**.

### FOE combat patrol + mid-battle join

| Feature | Doc |
|---------|-----|
| **FOE combat patrol** + **mid-battle join** | [ADR 005](../decisions/005-foe-combat-patrol.md), [ADR 010](../decisions/010-chain-foe-battle.md), [chain FOE battle](02-systems/chain-foe-battle.md) |

### Autopilot

| Feature | Doc |
|---------|-----|
| **Autopilot** — pathfind to discovered map tile | [autopilot](02-systems/autopilot.md), [ADR 021](../decisions/021-autopilot-mvp2.md) |

### Side dungeons

**Goal:** Optional **side dungeons** — EO-style grid explore + combat outside the stratum ladder, entered from the hub menu.

| Feature | Doc |
|---------|-----|
| Hub **Side expedition** menu → unlocked `locationId`s | [side dungeons](02-systems/side-dungeons.md), [hub](02-systems/hub-and-services.md) |
| `EnterSideDungeon` (separate from `LeaveHub`) | [game phase](02-systems/game-phase.md), [05 — Class design § side dungeons sketch](05-class-design.md#mvp3--side-dungeons-sketch) |
| Save/map keys `sd##_F#` | [side dungeons](02-systems/side-dungeons.md), [ADR 022](../decisions/022-side-dungeons-mvp3.md) |
| Placeholder content `sd01` | [side dungeons § sd01](02-systems/side-dungeons.md#placeholder-content--sd01-salvage-annex) |

**Out of side-dungeon scope (stay in Later):** 3D hub walk, open overworld town grid.

---

## Later

Deferred after the required slice and optional feature waves.

| Item | Notes |
|------|--------|
| **Guided tutorial coach** — Act 1 movement pages, B2F Protocol coach, pause-menu codex ([#88](https://github.com/miramocha/griddungeon-game/issues/88)) | Required slice uses story VN ([#87](https://github.com/miramocha/griddungeon-game/issues/87)) + Protocol HUD gate ([#35](https://github.com/miramocha/griddungeon-game/issues/35)) — [guided tutorial](02-systems/guided-tutorial.md) |
| Gamepad, rebind UI | [input bindings](02-systems/input-bindings.md) |
| Exploration animation speed UI (presets in [ADR 018](../decisions/018-exploration-animation-speed.md)) | Normal timings shipped in code |
| Reduce UI motion (accessibility) | — |
| Leg bind, paralysis, burn, speed buffs | [combat status & buffs](02-systems/combat-status-and-buffs.md) |
| Traps, encounter suppress | — |
| **Protocol Deploy** / **Protocol Transform** | [ADR 023](../decisions/023-protocol-deploy-sortie-summon.md), [ADR 024](../decisions/024-protocol-transform.md) |
| Hub **menu-driven camera pan** | [hub environment](02-systems/hub-and-services.md#hub-environment-presentation) |
| Multi-level map layer toggle in HUD | — |
| MapProxy + minimap camera (debug 3D preview) | Deferred / optional |
| **Class unlocks:** Elementalist, Saboteur, Overdriver | [party & classes](02-systems/party-and-classes.md) |
| Elemental res buffs, camp save consumable, 3D hub | — |
| Codex depth, guest quest lines, multiplayer | Multiplayer out of scope project-wide |

---

## Tuning (locked structure)

Numbers can move in data without ADR change:

- Synchro Charge % per action, Protocol skill power, encounter rates, `stepsPerMove`, shop prices
- `partyBagSlotCount` (default **30**) — [items & inventory](02-systems/items-and-inventory.md)

---

## Related docs

- [01 — Core loop](01-core-loop.md)
- [00 — Vision](00-vision.md)
- [README](../README.md)
- [archive/mvp1-spec.md](archive/mvp1-spec.md) — historical checklist (do not update)
