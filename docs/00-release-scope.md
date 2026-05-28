# Release Scope

Phased delivery for **Grid Dungeon**.

| Term | Meaning |
|------|---------|
| **MVP1** | First playable — core EO loop |
| **MVP2** | Gathering/fishing minigames, synthesis, FOE combat patrol + mid-battle join, autopilot |
| **MVP3** | Hub **Side expedition** → non-strata grid maps (full explore + combat) |

MVP2 adds dungeon-side resource play and **autopilot** (pathfind on discovered map tiles) without blocking MVP1.

## MVP1 (first playable)

**Goal:** Hub ↔ one stratum loop with combat, map, FOEs, Synchro Protocol, Navigator.

| In scope | Out of scope |
|----------|----------------|
| Grid exploration + auto-map ([ADR 002](../decisions/002-mapping-model.md)) | Fishing / gather **minigames** |
| FOE step patrol + contact fights ([ADR 003](../decisions/003-foe-step-patrol.md)) | [FOE combat patrol](../decisions/005-foe-combat-patrol.md) + [mid-battle join](../decisions/010-chain-foe-battle.md) (**MVP2**) |
| AGI combat, 6 core + aux layout, Synchro Charge | Synthesis hub |
| Navigator + Protocol ([ADR 006](../decisions/006-union-team-bar.md), [007](../decisions/007-navigator-role.md)) | Full status roster ([combat-status-and-buffs](02-systems/combat-status-and-buffs.md) — subset only) |
| Hub: Explorers Guild, Navigator Office, shop, hospital, inn save | 3D hub walk; hub **menu-driven camera pan** ([hub environment](02-systems/hub-and-services.md#hub-environment-presentation)) — **post-MVP1** |
| **Floor transition vignette** (stairs / hub enter; black + 3D threshold, Cinemachine) | Unique beat per floor pair; hub service camera pans |
| Chest loot; gather **instant loot** (no minigame) | Fishing + gather **minigame** (MVP2) |
| PC input defaults ([ADR 009](../decisions/009-input-bindings-pc.md)) | Rebind UI (can ship defaults only) |

**Full MVP1 checklist:** [mvp1-spec.md](mvp1-spec.md) · [ADR 014](../decisions/014-mvp1-exploration-map.md) · [ADR 015](../decisions/015-mvp1-combat.md)

---

## MVP2

**Goal:** EO-style **material loop** — explore for resources, return to hub, craft/equip.

| Feature | Doc |
|---------|-----|
| **Dungeon gathering minigame** (chop, mine, forage) | [gathering & fishing](02-systems/gathering-and-fishing.md) |
| **Dungeon fishing minigame** (pond/stream tiles) | [gathering & fishing](02-systems/gathering-and-fishing.md) |
| **Synthesis** at hub | [character progression](02-systems/character-progression.md), [hub](02-systems/hub-and-services.md) |
| Gather/fish nodes on map after use | [mapping](02-systems/mapping.md) |
| Gather quests + material drops | [dungeons & encounters](03-content/dungeons-and-encounters.md) |
| **FOE combat patrol** + **mid-battle join** | [ADR 005](../decisions/005-foe-combat-patrol.md), [ADR 010](../decisions/010-chain-foe-battle.md) |
| **Autopilot** — pathfind to discovered map tile | [autopilot](02-systems/autopilot.md), [ADR 021](../decisions/021-autopilot-mvp2.md) |

**Still optional in MVP2:** [cinematic + QTE skills](02-systems/combat-presentation.md), full ailment list, gamepad, pathfind **avoid FOE cells**.

---

## MVP3

**Goal:** Optional **side dungeons** — EO-style grid explore + combat outside the stratum ladder, entered from the hub menu.

| Feature | Doc |
|---------|-----|
| Hub **Side expedition** menu → unlocked `locationId`s | [side dungeons](02-systems/side-dungeons.md), [hub](02-systems/hub-and-services.md) |
| `EnterSideDungeon` (separate from `LeaveHub`) | [game phase](02-systems/game-phase.md), [05 — Class design MVP3 sketch](05-class-design-mvp1.md#mvp3--side-dungeons-sketch) |
| Save/map keys `sd##_F#` | [side dungeons](02-systems/side-dungeons.md), [ADR 022](../decisions/022-side-dungeons-mvp3.md) |
| Placeholder content `sd01` | [side dungeons § sd01](02-systems/side-dungeons.md#placeholder-content--sd01-salvage-annex) |

**Out of MVP3 (stay in Later):** 3D hub walk, open overworld town grid.

---

## Post-MVP1 class unlocks

- **Elementalist**, **Saboteur**, **Overdriver** ([party & classes](02-systems/party-and-classes.md))

## Later (after MVP3)

- Elemental res buffs, leg bind, paralysis
- Camp save consumable, 3D hub
- Codex depth, guest quest lines (beyond side-dungeon instances), multiplayer (out of scope project-wide)

---

## Related docs

- [01 — Core loop](01-core-loop.md)
- [00 — Vision](00-vision.md)
- [README](../README.md)
