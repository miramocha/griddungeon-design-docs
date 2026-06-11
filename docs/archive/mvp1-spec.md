> **Archived** — MVP1/MVP2 terminology replaced by required/optional features. This doc preserved for historical reference.

# MVP1 â€” Implementation Spec

Single checklist for the **first playable**. Locked exploration/combat rules: [ADR 014](../decisions/014-mvp1-exploration-map.md), [ADR 015](../decisions/015-mvp1-combat.md). Scope table: [release scope](00-release-scope.md).

**Status (synced 2026-06-03):** Core explore/combat/save/campaign and S1 floor assets are in. **ContentDB** ([#12](https://github.com/miramocha/griddungeon-game/issues/12)), **class skill rules** ([#52](https://github.com/miramocha/griddungeon-game/issues/52)), **summon** ([#11](https://github.com/miramocha/griddungeon-game/issues/11)), and **combat skill picker** ([#138](https://github.com/miramocha/griddungeon-game/issues/138)) are done. **Blocking first playable:** [#31](https://github.com/miramocha/griddungeon-game/issues/31) XP+loot Â· skill epics [#130](https://github.com/miramocha/griddungeon-game/issues/130) / [#131](https://github.com/miramocha/griddungeon-game/issues/131) (field + trees) Â· [#15](https://github.com/miramocha/griddungeon-game/issues/15) vertical slice. **Guided tutorial coach** ([#88](https://github.com/miramocha/griddungeon-game/issues/88)) â€” **post-MVP1**; MVP1 teaches S1 via story VN ([#87](https://github.com/miramocha/griddungeon-game/issues/87)) + `CombatTutorialHudRules` ([#35](https://github.com/miramocha/griddungeon-game/issues/35)). See [Â§7 skill epics](#skill-system-epics-adr-034--035).

---

## 1. Player-facing loop (MVP1)

```
New game: s1_B1F movement tutorial (no enemies, blocked path â†’ gate Event VN â†’ stairs â†’ hub)
  â†’ Hub Act 2: Guild party (6 core), Navigator, save
  â†’ Enter Stratum 1 at B1F gate (no warp gate; Synchro taught on **unbeatable** B2F FOE)
  â†’ Explore B1Fâ€“B3F (FPV + auto-map + FOE on B2F+)
  â†’ Random fights + FOE contact â†’ battle arena
  â†’ Win / flee â†’ loot / XP â†’ retreat via gate stairs â†’ hub
  â†’ Defeat stratum 1 boss on B3F (MVP1 vertical slice goal)
  â†’ Hub heal / save / equip
```

**Not in MVP1:** synthesis, gather **minigame**, fishing, **FOE combat patrol / mid-battle join**, **autopilot**, **combat skill cinematics / QTE**, gamepad, 3D hub walk, multiplayer.

**In MVP1 (presentation):** short **floor transition vignette** on stairs / hub stratum entry ([floor transition](02-systems/floor-transition.md), [ADR 032](../decisions/032-floor-transition-vignette-mvp1.md)) â€” not full combat cinematics.

---

## 2. Systems checklist

### Exploration & map ([ADR 014](../decisions/014-mvp1-exploration-map.md))

| # | Requirement | Doc |
|---|-------------|-----|
| âœ… | WASD + QE strafe/turn, ~0.32s step lerp (Normal), hold-to-repeat | [ADR 001](../decisions/001-grid-movement.md) |
| â¬œ | Exploration animation speed preset (Slow / Normal / Fast / Very Fast) â€” **UI deferred** post-MVP1; Normal timings shipped in code | [ADR 018](../decisions/018-exploration-animation-speed.md) |
| âœ… | Auto-map, no drawing | [ADR 002](../decisions/002-mapping-model.md) |
| âœ… | Wall: bump + cell perimeter reveal | [ADR 014](../decisions/014-mvp1-exploration-map.md) |
| âœ… | Map fullscreen â€” movement pass-through | [ADR 014](../decisions/014-mvp1-exploration-map.md) |
| âœ… | FOE step patrol + grid sprite | [ADR 003](../decisions/003-foe-step-patrol.md) |
| âœ… | FOE contact â†’ fight; flee + retreat cell | [ADR 011](../decisions/011-foe-flee-retreat.md) |
| âœ… | FOE respawn on hub return | [ADR 008](../decisions/008-campaign-defaults.md) |
| âœ… | Gather node: one-click instant loot (no minigame) | [ADR 014](../decisions/014-mvp1-exploration-map.md) |
| âœ… | Exploration pause (`Esc`, resume / quit â€” no save) | [game #27](https://github.com/miramocha/griddungeon-game/issues/27), [input-bindings](02-systems/input-bindings.md) |
| âœ… | `StratumFloor` **B1F** (`s1_B1F`) â€” Act 1/3 modes, blockers | [game #14](https://github.com/miramocha/griddungeon-game/issues/14), [dungeons â€” MVP1 Â§](03-content/dungeons-and-encounters.md#mvp1--stratum-1-b1fb3f) |
| âœ… | `StratumFloor` **B2F** floor asset â€” patrol FOE spawn; bind/poison **data** via ContentDB | [game #29](https://github.com/miramocha/griddungeon-game/issues/29) Â· tables [#12](https://github.com/miramocha/griddungeon-game/issues/12) |
| âœ… | `StratumFloor` **B3F** â€” boss FOE | [game #30](https://github.com/miramocha/griddungeon-game/issues/30) |
| âœ… | 2D `MapView` from floor data + reveal (no minimap RT) | [ADR 002](../decisions/002-mapping-model.md), [game #18](https://github.com/miramocha/griddungeon-game/issues/18) |
| â¬œ | Map cell art â€” composite walls, door overlay, sprites | [map-cell-art](02-systems/map-cell-art.md), [game #38](https://github.com/miramocha/griddungeon-game/issues/38) |
| âœ… | Shared map grid painter (dedupe MapView + dev preview) | [game #26](https://github.com/miramocha/griddungeon-game/issues/26) |
| â¬œ | Floor verticality + jump pads â€” **deferred**; flat B1Fâ€“B3F OK | [ADR 019](../decisions/019-floor-verticality.md) |
| âœ… | **Floor transition vignette** â€” black + 3D threshold, Cinemachine, serialized art load | [floor transition](02-systems/floor-transition.md), [ADR 032](../decisions/032-floor-transition-vignette-mvp1.md) Â· epic [#114](https://github.com/miramocha/griddungeon-game/issues/114) ([#115](https://github.com/miramocha/griddungeon-game/issues/115)â€“[#118](https://github.com/miramocha/griddungeon-game/issues/118), [#120](https://github.com/miramocha/griddungeon-game/issues/120)) |
| âœ… | FPV floor art load/unload by `floorKey` | [floor art FPV](02-systems/floor-art-fpv.md), [game #102](https://github.com/miramocha/griddungeon-game/issues/102) |
| âœ… | FPV populate walkable tiles (hallway / corner / floor) | [floor art FPV Â§ v1.5](02-systems/floor-art-fpv.md#locked-decisions-populate-v15--walkable-tiles), [game #172](https://github.com/miramocha/griddungeon-game/issues/172) |

### Combat ([ADR 015](../decisions/015-mvp1-combat.md))

| # | Requirement | Doc |
|---|-------------|-----|
| âœ… | Battle arena + enemy slots (not FPV fight) | [ADR 013](../decisions/013-combat-scene-rendering.md) |
| âœ… | 6 core + 0â€“2 aux; Navigator off-formation | [ADR 004](../decisions/004-auxiliary-slots.md), [007](../decisions/007-navigator-role.md) |
| âœ… | AGI queue UI; Protocol on core turn at Synchro Charge 100% | [ADR 006](../decisions/006-union-team-bar.md), [ADR 020](../decisions/020-team-burst-naming.md) |
| âœ… | Enemy front + back rows (6 slots max, **3+3**) | [ADR 015](../decisions/015-mvp1-combat.md) |
| âœ… | Fixed camera + Fixed skills only | [combat presentation](02-systems/combat-presentation.md) |
| âœ… | Damage + status MVP1 subset | [combat](02-systems/combat.md), [status](02-systems/combat-status-and-buffs.md) |
| âœ… | Command planning â€” queue all living cores before AGI playback | [game #58](https://github.com/miramocha/griddungeon-game/issues/58), [combat Â§ UI](02-systems/combat.md#ui-requirements) |
| âœ… | **Back** during planning (`R`/`Esc`, LIFO) | [game #61](https://github.com/miramocha/griddungeon-game/issues/61) |
| âœ… | Protocol skills `protocol_strike` / `protocol_mend` (combat rules) | [game #10](https://github.com/miramocha/griddungeon-game/issues/10) |
| âœ… | Player **target selection** (mouse + valid highlights) | [game #60](https://github.com/miramocha/griddungeon-game/issues/60), [combat Â§ targeting](02-systems/combat.md#command-planning--targeting) |
| âœ… | **Stale queued target** UI + AGI retarget | [game #65](https://github.com/miramocha/griddungeon-game/issues/65) |
| â¬œ | Enemy **row collapse** + full melee/pierce targeting rules | [game #56](https://github.com/miramocha/griddungeon-game/issues/56) Â· partial in `ValidTargetCalculator` |
| âœ… | FOE combat patrol **off** (MVP2) | [ADR 005](../decisions/005-foe-combat-patrol.md) deferred |
| â¬œ | 8 enemy types + 1 boss encounter group â€” **roster authored** ([design #2](https://github.com/miramocha/griddungeon-design-docs/issues/2) closed) | [mvp1-enemy-roster](../03-content/enemy-roster.md) Â· ship in [game #12](https://github.com/miramocha/griddungeon-game/issues/12) |
| â¬œ | MVP1 class skill **rules** + Summoner `deploy_scout_drone` | [game #52](https://github.com/miramocha/griddungeon-game/issues/52), [#11](https://github.com/miramocha/griddungeon-game/issues/11), [ADR 016](../decisions/016-summon-control-mvp1.md) |
| â¬œ | **Skill use picker** (combat Skill â†’ tabbed modal; default **All**) | epic [#131](https://github.com/miramocha/griddungeon-game/issues/131) ([#135](https://github.com/miramocha/griddungeon-game/issues/135)â€“[#139](https://github.com/miramocha/griddungeon-game/issues/139); field [#140](https://github.com/miramocha/griddungeon-game/issues/140) phase 2) Â· [ADR 035](../decisions/035-skill-use-picker.md) |
| â¬œ | Post-battle **XP + loot** (core party) | [game #31](https://github.com/miramocha/griddungeon-game/issues/31), [progression](02-systems/character-progression.md) |
| âœ… | Combat HUD skeleton (AGI strip, commands, HP) | [game #34](https://github.com/miramocha/griddungeon-game/issues/34) |
| âœ… | Combat HUD reactive + Synchro tutorial presentation | [#35](https://github.com/miramocha/griddungeon-game/issues/35) Â· epic [#19](https://github.com/miramocha/griddungeon-game/issues/19) |
| âœ… | **Story events (VN)** â€” `StoryEventRunner` + four S1 scenes | [#87](https://github.com/miramocha/griddungeon-game/issues/87) Â· [ADR 028](../decisions/028-story-visual-novel-events.md) Â· [story-events](02-systems/story-events.md) |
| âœ… | S1 teach (MVP1) â€” story VN + Protocol HUD gate only; full guided coach **post-MVP1** | [#87](https://github.com/miramocha/griddungeon-game/issues/87) Â· [#35](https://github.com/miramocha/griddungeon-game/issues/35) Â· coach deferred [#88](https://github.com/miramocha/griddungeon-game/issues/88) Â· [ADR 029](../decisions/029-guided-tutorial.md) |
| âœ… | Hub + exploration HUD (party strip, service motion) | [game #36](https://github.com/miramocha/griddungeon-game/issues/36) |
| âœ… | S1 intro blockers + FOE patrol/encounters/gather wiring | [game #20](https://github.com/miramocha/griddungeon-game/issues/20) Â· [PR #91](https://github.com/miramocha/griddungeon-game/pull/91), [hub](02-systems/hub-and-services.md#stratum-1-intro) |

### Hub & progression

| # | Requirement | Doc |
|---|-------------|-----|
| âœ… | Inn save, hospital, shop, Guild + **Navigator Office** (services + UX) | [game #13](https://github.com/miramocha/griddungeon-game/issues/13), [hub](02-systems/hub-and-services.md) |
| âœ… | **SaveGame** JSON persist (inn, map, FOE, S1 campaign flags) | [game #32](https://github.com/miramocha/griddungeon-game/issues/32), [map save format](02-systems/map-reveal-save-format.md) |
| âœ… | **Campaign:** S1 flags, new-game bootstrap, spawn routing | [game #33](https://github.com/miramocha/griddungeon-game/issues/33), [campaign/s1-intro](03-content/campaign/s1-intro.md) Â· S2+ resolver split [ADR 025](../decisions/025-campaign-exploration-target.md) (stub) |
| â¬œ | Skill **trees** â€” spend points hub + labyrinth when safe | epic [#130](https://github.com/miramocha/griddungeon-game/issues/130) ([#132](https://github.com/miramocha/griddungeon-game/issues/132)â€“[#134](https://github.com/miramocha/griddungeon-game/issues/134)) Â· [ADR 034](../decisions/034-skill-point-allocation-outside-combat.md) Â· design âœ… [party](02-systems/party-and-classes.md) |
| âœ… | Stats: HP, MP, STR, TEC, AGI, VIT, LUC | [progression](02-systems/character-progression.md) |
| âœ… | 1 Navigator + 2 Protocol skills (MVP1 kit) | [navigator](02-systems/navigator.md), [synchro-protocol](02-systems/synchro-protocol.md) |
| â¬œ | 3 skills per class minimum â€” **kits authored** ([design #3](https://github.com/miramocha/griddungeon-design-docs/issues/3) closed) | [MVP1 class skills](../03-content/class-skills.md) Â· ship in [game #12](https://github.com/miramocha/griddungeon-game/issues/12) |
| â¬œ | Weapon + 3 armor + 1 accessory â€” **IDs locked** ([design #4](https://github.com/miramocha/griddungeon-design-docs/issues/4) closed) | [locked table](02-systems/character-progression.md#mvp1-equipment-locked) Â· [game #12](https://github.com/miramocha/griddungeon-game/issues/12) |
| â¬œ | **Party inventory + equip** â€” fixed bag, category tabs, shop/loot/chest | [items & inventory](02-systems/items-and-inventory.md) Â· [ADR 036](../decisions/036-party-inventory-model.md) Â· [design #22](https://github.com/miramocha/griddungeon-design-docs/issues/22) Â· epic [game #151](https://github.com/miramocha/griddungeon-game/issues/151) |

### Tech ([ADR 012](../decisions/012-unity-6-stack.md))

| # | Requirement |
|---|-------------|
| âœ… | Unity 6 + URP + Input System + Shader Graphâ€“first |
| âœ… | `GamePhaseController` + hub / explore / combat phase controllers ([ADR 017](../decisions/017-game-phase-controller.md)) |
| âœ… | `CombatSimulator` unit tests for damage + AGI order |
| âœ… | PC default bindings (exploration `A/D` strafe + `Q/E` turn; combat focus + `Z`/`X` per [ADR 026](../decisions/026-combat-menu-focus-navigation.md)) | [game #3](https://github.com/miramocha/griddungeon-game/issues/3), [#63](https://github.com/miramocha/griddungeon-game/issues/63), [ADR 009](../decisions/009-input-bindings-pc.md) |
| âœ… | Combat menu focus navigation (command bar + targeting Path B) | [ADR 026](../decisions/026-combat-menu-focus-navigation.md), [game #68](https://github.com/miramocha/griddungeon-game/issues/68), [#69](https://github.com/miramocha/griddungeon-game/issues/69), [#70](https://github.com/miramocha/griddungeon-game/issues/70) |

---

## 3. Content slice (Stratum 1 MVP1)

| Floor | Goal |
|-------|------|
| **B1F** | Shared map: Act 1 movement (0 enemies, blockers); Act 3 gate entry, **0 FOE**, stairs down |
| **B2F** | First bind/poison enemies, 1 FOE |
| **B3F** | Stratum boss FOE + stairs (MVP1 â€œwinâ€) |

**Layouts (ASCII + YAML):** [dungeons & encounters â€” MVP1 Â§](03-content/dungeons-and-encounters.md#mvp1--stratum-1-b1fb3f) Â· [campaign S1 intro](03-content/campaign/s1-intro.md) Â· [design-docs #1](https://github.com/miramocha/griddungeon-design-docs/issues/1) (authoritative, closed).

**Enemies & groups:** [mvp1-enemy-roster](../03-content/enemy-roster.md) Â· [design-docs #2](https://github.com/miramocha/griddungeon-design-docs/issues/2) (closed â€” ship via game #12).

**Floor assets (game):** B1F [#14](https://github.com/miramocha/griddungeon-game/issues/14) Â· B2F [#29](https://github.com/miramocha/griddungeon-game/issues/29) Â· B3F [#30](https://github.com/miramocha/griddungeon-game/issues/30) â€” all closed.

**Vertical slice:** [game #15](https://github.com/miramocha/griddungeon-game/issues/15) â€” end-to-end hub â†’ B3F boss â†’ hub.

Defer B4Fâ€“B5F polish until loop proven.

---

## 4. MVP1 Navigator & Synchro Protocol

| Asset | MVP1 |
|-------|------|
| **Navigator** | `guild_handler` â€” unlocked day one; aura: Synchro gain +5% |
| **Protocol skills** | `protocol_strike` (damage), `protocol_mend` (heal all living core) |

Authority: [navigator](02-systems/navigator.md), [synchro-protocol](02-systems/synchro-protocol.md), [class design â€” MVP1 IDs](../05-class-design.md#mvp1-content-ids-locked). Protocol **rules** [#10](https://github.com/miramocha/griddungeon-game/issues/10) done; Synchro HUD [#35](https://github.com/miramocha/griddungeon-game/issues/35) done; S1 **VN** [#87](https://github.com/miramocha/griddungeon-game/issues/87) done; guided **coach** [#88](https://github.com/miramocha/griddungeon-game/issues/88) **post-MVP1** Â· [synchro Â§ S1](02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe).

Full Navigator roster unlocks post-MVP1.

---

## 5. Explicitly deferred (not blocking MVP1)

| Item | When |
|------|------|
| FOE combat patrol + mid-battle join ([005](../decisions/005-foe-combat-patrol.md), [010](../decisions/010-chain-foe-battle.md)) | MVP2 |
| **Autopilot** â€” pathfind on discovered tiles ([ADR 021](../decisions/021-autopilot-mvp2.md)) | MVP2 |
| Gather/fish **minigame**, synthesis | MVP2 |
| Cinematic / QTE skills | MVP2 optional |
| **Guided tutorial coach** â€” Act 1 movement pages, B2F Protocol coach, pause-menu codex ([#88](https://github.com/miramocha/griddungeon-game/issues/88), [ADR 029](../decisions/029-guided-tutorial.md)) | Post-MVP1 â€” MVP1 uses VN ([#87](https://github.com/miramocha/griddungeon-game/issues/87)) + Protocol-only HUD ([#35](https://github.com/miramocha/griddungeon-game/issues/35)) |
| Gamepad, rebind UI | Post-MVP1 |
| Exploration animation speed UI (presets in [ADR 018](../decisions/018-exploration-animation-speed.md)) | Post-MVP1 |
| Reduce UI motion (accessibility) | Post-MVP1 |
| Leg bind, paralysis, burn, speed buffs | Post-MVP1 |
| Traps, encounter suppress | Post-MVP1 |
| **Protocol Deploy** / **Protocol Transform** ([023](../decisions/023-protocol-deploy-sortie-summon.md), [024](../decisions/024-protocol-transform.md)) | Post-MVP1 |
| Guest (`MVP1+`) | Stretch |
| Floor level painter (Editor â†’ `StratumFloor`) | **Done** â€” epic [#75](https://github.com/miramocha/griddungeon-game/issues/75) closed ([#76](https://github.com/miramocha/griddungeon-game/issues/76)â€“[#79](https://github.com/miramocha/griddungeon-game/issues/79), [#107](https://github.com/miramocha/griddungeon-game/issues/107)). Story `!` cells: [#109](https://github.com/miramocha/griddungeon-game/issues/109)â€“[#113](https://github.com/miramocha/griddungeon-game/issues/113) |
| Multi-level map layer toggle in HUD | Post-MVP1 |
| MapProxy + minimap camera (debug 3D preview) | Deferred / optional |
| Setting name / tone brief | [00 â€” Vision Â§ Tone](00-vision.md#tone--setting) (municipal underworks; UI palette in [map cell art](02-systems/map-cell-art.md#visual-tone-municipal-underworks)) |

---

## 6. Open for tuning only (locked structure)

Numbers can move in data without ADR change:

- Synchro Charge % per action, Protocol skill power, encounter rates, `stepsPerMove`, shop prices.

---

## 7. Pull order (GitHub backlog)

**Waves** are labeled **`pull-w01`** â€¦ **`pull-w08`** on game-repo issues â€” a suggested implementation sequence, not calendar weeks. Filter the [project board](https://github.com/users/miramocha/projects/3) by label, or **Status â†’ Ready** for the active wave.

| Wave | What it was for | Outcome |
|------|-----------------|--------|
| **1** (`pull-w01`) | **Persistence + campaign spine** â€” JSON save/load ([#32](https://github.com/miramocha/griddungeon-game/issues/32)) and S1 bootstrap / spawn routing ([#33](https://github.com/miramocha/griddungeon-game/issues/33)) | **Done** |
| **2** (`pull-w02`) | **Combat HUD skeleton** â€” AGI strip, command panel, HP ([#34](https://github.com/miramocha/griddungeon-game/issues/34)) so combat is playable before polish | **Done** |
| **3+** | Content, hub loop, map art, tutorials, vertical slice | See table below |

UI epic [#19](https://github.com/miramocha/griddungeon-game/issues/19): [#34](https://github.com/miramocha/griddungeon-game/issues/34) Â· [#35](https://github.com/miramocha/griddungeon-game/issues/35) Â· [#87](https://github.com/miramocha/griddungeon-game/issues/87) Â· [#36](https://github.com/miramocha/griddungeon-game/issues/36) done for **MVP1** â€” [#88](https://github.com/miramocha/griddungeon-game/issues/88) guided coach **post-MVP1** (epic may close on MVP1 scope without #88).

| Wave | Label | Pull next (top â†’ bottom) | Status |
|------|-------|--------------------------|--------|
| **1** | `pull-w01` | [#32](https://github.com/miramocha/griddungeon-game/issues/32) Save â†’ [#33](https://github.com/miramocha/griddungeon-game/issues/33) Campaign | **Done** |
| **2** | `pull-w02` | [#34](https://github.com/miramocha/griddungeon-game/issues/34) Combat HUD skeleton | **Done** |
| **3** | `pull-w03` | [#13](https://github.com/miramocha/griddungeon-game/issues/13) Hub Â· [#12](https://github.com/miramocha/griddungeon-game/issues/12) ContentDB Â· [#52](https://github.com/miramocha/griddungeon-game/issues/52) class skill rules Â· epics [#130](https://github.com/miramocha/griddungeon-game/issues/130) / [#131](https://github.com/miramocha/griddungeon-game/issues/131) | **In progress** â€” hub done; [#12](https://github.com/miramocha/griddungeon-game/issues/12) Â· [#52](https://github.com/miramocha/griddungeon-game/issues/52) Â· skill epics open |
| **4** | `pull-w04` | [#109](https://github.com/miramocha/griddungeon-game/issues/109)â€“[#113](https://github.com/miramocha/griddungeon-game/issues/113) story `!` cells Â· [#38](https://github.com/miramocha/griddungeon-game/issues/38) map cell art Â· [#56](https://github.com/miramocha/griddungeon-game/issues/56) enemy targeting | **In progress** â€” [#75](https://github.com/miramocha/griddungeon-game/issues/75) floor painter done ([#76](https://github.com/miramocha/griddungeon-game/issues/76)â€“[#79](https://github.com/miramocha/griddungeon-game/issues/79), [#107](https://github.com/miramocha/griddungeon-game/issues/107)); [#26](https://github.com/miramocha/griddungeon-game/issues/26) Â· [#20](https://github.com/miramocha/griddungeon-game/issues/20) done |
| **5** | `pull-w05` | [#35](https://github.com/miramocha/griddungeon-game/issues/35) Combat reactive + Synchro tutorial UI | **Done** |
| **5b** | `pull-w05b` | [#87](https://github.com/miramocha/griddungeon-game/issues/87) Story events Â· [#88](https://github.com/miramocha/griddungeon-game/issues/88) Guided tutorials | **Done for MVP1** â€” VN done; [#88](https://github.com/miramocha/griddungeon-game/issues/88) **post-MVP1** |
| **6** | `pull-w06` | [#11](https://github.com/miramocha/griddungeon-game/issues/11) summon | **In progress** â€” [#30](https://github.com/miramocha/griddungeon-game/issues/30) Â· [#36](https://github.com/miramocha/griddungeon-game/issues/36) done |
| **7** | `pull-w07` | [#31](https://github.com/miramocha/griddungeon-game/issues/31) XP + loot | Backlog |
| **8** | `pull-w08` | [#15](https://github.com/miramocha/griddungeon-game/issues/15) Vertical slice (integration) | Backlog |
| â€” | `pull-epic` | [#19](https://github.com/miramocha/griddungeon-game/issues/19) UI epic â€” MVP1 HUD scope done (#34â€“#36, #87); [#88](https://github.com/miramocha/griddungeon-game/issues/88) post-MVP1 Â· [#179](https://github.com/miramocha/griddungeon-game/issues/179) combat HUD frame layout **Done** ([#180](https://github.com/miramocha/griddungeon-game/issues/180)â€“[#181](https://github.com/miramocha/griddungeon-game/issues/181) Â· [PR #182](https://github.com/miramocha/griddungeon-game/pull/182)) Â· [#109](https://github.com/miramocha/griddungeon-game/issues/109) story `!` cells ([#110](https://github.com/miramocha/griddungeon-game/issues/110)â€“[#113](https://github.com/miramocha/griddungeon-game/issues/113); [#75](https://github.com/miramocha/griddungeon-game/issues/75) done) Â· [#130](https://github.com/miramocha/griddungeon-game/issues/130) skill trees Â· [#131](https://github.com/miramocha/griddungeon-game/issues/131) field picker [#140](https://github.com/miramocha/griddungeon-game/issues/140) (#138 combat picker done) | Backlog |

### Skill system epics (ADR 034 + 035)

Two epics â€” **different jobs**, **no strict A-then-B order**. Shared foundation: [#12](https://github.com/miramocha/griddungeon-game/issues/12) ContentDB + [#52](https://github.com/miramocha/griddungeon-game/issues/52) targeting/rules where combat applies.

| Epic | Game | What | Start |
|------|------|------|--------|
| **A â€” Skill trees** | [#130](https://github.com/miramocha/griddungeon-game/issues/130) | Spend **skill points** on class nodes (Guild + exploration) Â· [ADR 034](../decisions/034-skill-point-allocation-outside-combat.md) | [#132](https://github.com/miramocha/griddungeon-game/issues/132) â†’ [#133](https://github.com/miramocha/griddungeon-game/issues/133) â†’ [#134](https://github.com/miramocha/griddungeon-game/issues/134) |
| **B â€” Skill use picker** | [#131](https://github.com/miramocha/griddungeon-game/issues/131) | Pick **learned skill** to cast (tabs: **All** + `SkillType`) Â· [ADR 035](../decisions/035-skill-use-picker.md) | **Combat shipped** ([#138](https://github.com/miramocha/griddungeon-game/issues/138)); open [#139](https://github.com/miramocha/griddungeon-game/issues/139) content Â· [#140](https://github.com/miramocha/griddungeon-game/issues/140) field UI |

**Suggested priority for combat feel:** **B** (picker) + [#52](https://github.com/miramocha/griddungeon-game/issues/52) before or alongside **A**; dev fights can use pre-allocated `AllocatedSkillIds` without exploration tree UI. **A** before [#140](https://github.com/miramocha/griddungeon-game/issues/140) field heal. Coordinate menu copy: pause **Skill trees** (A) vs **Use skill** (B / [#140](https://github.com/miramocha/griddungeon-game/issues/140)).

**Closed since wave plan was written:** [#13](https://github.com/miramocha/griddungeon-game/issues/13) hub services Â· [#26](https://github.com/miramocha/griddungeon-game/issues/26) map grid painter Â· [#30](https://github.com/miramocha/griddungeon-game/issues/30) B3F Â· [#36](https://github.com/miramocha/griddungeon-game/issues/36) hub + explore HUD Â· [#87](https://github.com/miramocha/griddungeon-game/issues/87) story VN Â· [#75](https://github.com/miramocha/griddungeon-game/issues/75) floor painter epic ([#76](https://github.com/miramocha/griddungeon-game/issues/76)â€“[#79](https://github.com/miramocha/griddungeon-game/issues/79), [#107](https://github.com/miramocha/griddungeon-game/issues/107)) Â· [#35](https://github.com/miramocha/griddungeon-game/issues/35) combat reactive + Synchro HUD Â· [#29](https://github.com/miramocha/griddungeon-game/issues/29) B2F Â· [#27](https://github.com/miramocha/griddungeon-game/issues/27) pause Â· [#60](https://github.com/miramocha/griddungeon-game/issues/60) target selection Â· [#65](https://github.com/miramocha/griddungeon-game/issues/65) stale targets Â· design [#1](https://github.com/miramocha/griddungeon-design-docs/issues/1)â€“[#5](https://github.com/miramocha/griddungeon-design-docs/issues/5) content/review docs.

Board: [Codename: GridDungeon (project 3)](https://github.com/users/miramocha/projects/3) â€” open items ordered to match waves 1â†’8 where the API allows.

---

## Related

- [00 â€” Release scope](00-release-scope.md)
- [00 â€” Vision](00-vision.md) â€” success criteria
- [05 â€” Class design MVP1](../05-class-design.md) â€” concrete classes, assembly layout, folder structure
- [Game phase](02-systems/game-phase.md) â€” design goals, diagrams, macro phase flow ([ADR 017](../decisions/017-game-phase-controller.md))
- [README](../README.md)
