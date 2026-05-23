# MVP1 — Implementation Spec

Single checklist for the **first playable**. Locked exploration/combat rules: [ADR 014](../decisions/014-mvp1-exploration-map.md), [ADR 015](../decisions/015-mvp1-combat.md). Scope table: [release scope](00-release-scope.md).

---

## 1. Player-facing loop (MVP1)

```
New game: s1_B1F movement tutorial (no enemies, blocked path → mouth stairs → hub)
  → Hub Act 2: Guild party (6 core), Navigator, save
  → Enter Stratum 1 at B1F mouth (no warp gate; Synchro taught on **unbeatable** B2F FOE)
  → Explore B1F–B3F (FPV + auto-map + FOE on B2F+)
  → Random fights + FOE contact → battle arena
  → Win / flee → loot / XP → retreat via mouth stairs → hub
  → Defeat stratum 1 boss on B3F (MVP1 vertical slice goal)
  → Hub heal / save / equip
```

**Not in MVP1:** synthesis, gather **minigame**, fishing, **FOE combat patrol / mid-battle join**, **autopilot**, cinematics, gamepad, 3D hub walk, multiplayer.

---

## 2. Systems checklist

### Exploration & map ([ADR 014](../decisions/014-mvp1-exploration-map.md))

| # | Requirement | Doc |
|---|-------------|-----|
| ✅ | WASD + QE strafe/turn, ~0.28s step lerp (Normal), hold-to-repeat | [ADR 001](../decisions/001-grid-movement.md) |
| ⬜ | Exploration animation speed preset (Slow / Normal / Fast / Very Fast) — **UI deferred** post-MVP1; Normal timings shipped in code | [ADR 018](../decisions/018-exploration-animation-speed.md) |
| ✅ | Auto-map, no drawing | [ADR 002](../decisions/002-mapping-model.md) |
| ✅ | Wall: bump + cell perimeter reveal | [ADR 014](../decisions/014-mvp1-exploration-map.md) |
| ✅ | Map fullscreen — movement pass-through | [ADR 014](../decisions/014-mvp1-exploration-map.md) |
| ✅ | FOE step patrol + grid sprite | [ADR 003](../decisions/003-foe-step-patrol.md) |
| ✅ | FOE contact → fight; flee + retreat cell | [ADR 011](../decisions/011-foe-flee-retreat.md) |
| ✅ | FOE respawn on hub return | [ADR 008](../decisions/008-campaign-defaults.md) |
| ✅ | Gather node: one-click instant loot (no minigame) | [ADR 014](../decisions/014-mvp1-exploration-map.md) |
| ✅ | Exploration pause (`Esc`, resume / quit — no save) | [game #27](https://github.com/miramocha/griddungeon-game/issues/27), [input-bindings](02-systems/input-bindings.md) |
| ✅ | `StratumFloor` **B1F** (`s1_B1F`) — Act 1/3 modes, blockers | [game #14](https://github.com/miramocha/griddungeon-game/issues/14), [dungeons — MVP1 §](03-content/dungeons-and-encounters.md#mvp1--stratum-1-b1fb3f) |
| ✅ | `StratumFloor` **B2F** floor asset — patrol FOE spawn; bind/poison **data** via ContentDB | [game #29](https://github.com/miramocha/griddungeon-game/issues/29) · tables [#12](https://github.com/miramocha/griddungeon-game/issues/12) |
| ⬜ | `StratumFloor` **B3F** — boss FOE | [game #30](https://github.com/miramocha/griddungeon-game/issues/30) |
| ✅ | 2D `MapView` from floor data + reveal (no minimap RT) | [ADR 002](../decisions/002-mapping-model.md), [game #18](https://github.com/miramocha/griddungeon-game/issues/18) |
| ⬜ | Map cell art — composite walls, door overlay, sprites | [map-cell-art](02-systems/map-cell-art.md), [game #38](https://github.com/miramocha/griddungeon-game/issues/38) |
| ⬜ | Shared map grid painter (dedupe MapView + dev preview) | [game #26](https://github.com/miramocha/griddungeon-game/issues/26) — schedule early MVP1 |
| ⬜ | Floor verticality + jump pads — **deferred**; flat B1F–B3F OK | [ADR 019](../decisions/019-floor-verticality.md) |

### Combat ([ADR 015](../decisions/015-mvp1-combat.md))

| # | Requirement | Doc |
|---|-------------|-----|
| ✅ | Battle arena + enemy slots (not FPV fight) | [ADR 013](../decisions/013-combat-scene-rendering.md) |
| ✅ | 6 core + 0–2 aux; Navigator off-formation | [ADR 004](../decisions/004-auxiliary-slots.md), [007](../decisions/007-navigator-role.md) |
| ✅ | AGI queue UI; Protocol on core turn at Synchro Charge 100% | [ADR 006](../decisions/006-union-team-bar.md), [ADR 020](../decisions/020-team-burst-naming.md) |
| ✅ | Enemy front + back rows (6 slots max, **3+3**) | [ADR 015](../decisions/015-mvp1-combat.md) |
| ✅ | Fixed camera + Fixed skills only | [combat presentation](02-systems/combat-presentation.md) |
| ✅ | Damage + status MVP1 subset | [combat](02-systems/combat.md), [status](02-systems/combat-status-and-buffs.md) |
| ✅ | Command planning — queue all living cores before AGI playback | [game #58](https://github.com/miramocha/griddungeon-game/issues/58), [combat § UI](02-systems/combat.md#ui-requirements) |
| ✅ | **Back** during planning (`R`/`Esc`, LIFO) | [game #61](https://github.com/miramocha/griddungeon-game/issues/61) |
| ✅ | Protocol skills `protocol_strike` / `protocol_mend` (combat rules) | [game #10](https://github.com/miramocha/griddungeon-game/issues/10) |
| ✅ | Player **target selection** (mouse + valid highlights) | [game #60](https://github.com/miramocha/griddungeon-game/issues/60), [combat § targeting](02-systems/combat.md#command-planning--targeting) |
| ✅ | **Stale queued target** UI + AGI retarget | [game #65](https://github.com/miramocha/griddungeon-game/issues/65) |
| ⬜ | Enemy **row collapse** + full melee/pierce targeting rules | [game #56](https://github.com/miramocha/griddungeon-game/issues/56) · partial in `ValidTargetCalculator` |
| ✅ | FOE combat patrol **off** (MVP2) | [ADR 005](../decisions/005-foe-combat-patrol.md) deferred |
| ⬜ | 8 enemy types + 1 boss encounter group — **roster authored** ([design #2](https://github.com/miramocha/griddungeon-design-docs/issues/2) closed) | [mvp1-enemy-roster](03-content/mvp1-enemy-roster.md) · ship in [game #12](https://github.com/miramocha/griddungeon-game/issues/12) |
| ⬜ | MVP1 class skill **rules** + Summoner `deploy_test_drone` | [game #52](https://github.com/miramocha/griddungeon-game/issues/52), [#11](https://github.com/miramocha/griddungeon-game/issues/11), [ADR 016](../decisions/016-summon-control-mvp1.md) |
| ⬜ | Post-battle **XP + loot** (core party) | [game #31](https://github.com/miramocha/griddungeon-game/issues/31), [progression](02-systems/character-progression.md) |
| ✅ | Combat HUD skeleton (AGI strip, commands, HP) | [game #34](https://github.com/miramocha/griddungeon-game/issues/34) |
| ⬜ | Combat HUD reactive + Synchro tutorial presentation | [#35](https://github.com/miramocha/griddungeon-game/issues/35) · epic [#19](https://github.com/miramocha/griddungeon-game/issues/19) |
| ⬜ | Hub + exploration HUD (party strip, service motion) | [game #36](https://github.com/miramocha/griddungeon-game/issues/36) |
| ⬜ | S1 intro blockers + FOE patrol/encounters/gather wiring | [game #20](https://github.com/miramocha/griddungeon-game/issues/20), [hub](02-systems/hub-and-services.md#stratum-1-intro) |
| ⬜ | Synchro **tutorial** — mid-fight unlock, unbeatable FOE, forced `protocol_strike` | [#35](https://github.com/miramocha/griddungeon-game/issues/35), [synchro — S1 gating](02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe) |

### Hub & progression

| # | Requirement | Doc |
|---|-------------|-----|
| ⬜ | Inn save, hospital, shop, Guild + **Navigator Office** (services + UX) | [game #13](https://github.com/miramocha/griddungeon-game/issues/13), [hub](02-systems/hub-and-services.md) |
| ✅ | **SaveGame** JSON persist (inn, map, FOE, S1 campaign flags) | [game #32](https://github.com/miramocha/griddungeon-game/issues/32), [map save format](02-systems/map-reveal-save-format.md) |
| ✅ | **Campaign:** S1 flags, new-game bootstrap, spawn routing | [game #33](https://github.com/miramocha/griddungeon-game/issues/33), [campaign/s1-intro](03-content/campaign/s1-intro.md) · S2+ resolver split [ADR 025](../decisions/025-campaign-exploration-target.md) (stub) |
| ✅ | 6 classes day one; skill points at hub | [party](02-systems/party-and-classes.md) |
| ✅ | Stats: HP, MP, STR, TEC, AGI, VIT, LUC | [progression](02-systems/character-progression.md) |
| ✅ | 1 Navigator + 2 Protocol skills (MVP1 kit) | [navigator](02-systems/navigator.md), [synchro-protocol](02-systems/synchro-protocol.md) |
| ⬜ | 3 skills per class minimum — **kits authored** ([design #3](https://github.com/miramocha/griddungeon-design-docs/issues/3) closed) | [MVP1 class skills](03-content/mvp1-class-skills.md) · ship in [game #12](https://github.com/miramocha/griddungeon-game/issues/12) |
| ⬜ | Weapon + 3 armor + 1 accessory — **IDs locked** ([design #4](https://github.com/miramocha/griddungeon-design-docs/issues/4) closed) | [locked table](02-systems/character-progression.md#mvp1-equipment-locked) · [game #12](https://github.com/miramocha/griddungeon-game/issues/12) |

### Tech ([ADR 012](../decisions/012-unity-6-stack.md))

| # | Requirement |
|---|-------------|
| ✅ | Unity 6 + URP + Input System + Shader Graph–first |
| ✅ | `GamePhaseController` + hub / explore / combat phase controllers ([ADR 017](../decisions/017-game-phase-controller.md)) |
| ✅ | `CombatSimulator` unit tests for damage + AGI order |
| ✅ | PC default bindings (exploration `A/D` strafe + `Q/E` turn; combat focus + `Z`/`X` per [ADR 026](../decisions/026-combat-menu-focus-navigation.md)) | [game #3](https://github.com/miramocha/griddungeon-game/issues/3), [#63](https://github.com/miramocha/griddungeon-game/issues/63), [ADR 009](../decisions/009-input-bindings-pc.md) |
| ⬜ | Combat menu focus navigation (command bar + targeting Path B) | [ADR 026](../decisions/026-combat-menu-focus-navigation.md) — implementation issues in game repo |

---

## 3. Content slice (Stratum 1 MVP1)

| Floor | Goal |
|-------|------|
| **B1F** | Shared map: Act 1 movement (0 enemies, blockers); Act 3 mouth entry, **0 FOE**, stairs down |
| **B2F** | First bind/poison enemies, 1 FOE |
| **B3F** | Stratum boss FOE + stairs (MVP1 “win”) |

**Layouts (ASCII + YAML):** [dungeons & encounters — MVP1 §](03-content/dungeons-and-encounters.md#mvp1--stratum-1-b1fb3f) · [campaign S1 intro](03-content/campaign/s1-intro.md) · [design-docs #1](https://github.com/miramocha/griddungeon-design-docs/issues/1) (authoritative, closed).

**Enemies & groups:** [mvp1-enemy-roster](03-content/mvp1-enemy-roster.md) · [design-docs #2](https://github.com/miramocha/griddungeon-design-docs/issues/2) (closed — ship via game #12).

**Floor assets (game):** B1F [#14](https://github.com/miramocha/griddungeon-game/issues/14) · B2F [#29](https://github.com/miramocha/griddungeon-game/issues/29) · B3F [#30](https://github.com/miramocha/griddungeon-game/issues/30) (open).

**Vertical slice:** [game #15](https://github.com/miramocha/griddungeon-game/issues/15) — end-to-end hub → B3F boss → hub.

Defer B4F–B5F polish until loop proven.

---

## 4. MVP1 Navigator & Synchro Protocol

| Asset | MVP1 |
|-------|------|
| **Navigator** | `guild_handler` — unlocked day one; aura: Synchro gain +5% |
| **Protocol skills** | `protocol_strike` (damage), `protocol_mend` (heal all living core) |

Authority: [navigator](02-systems/navigator.md), [synchro-protocol](02-systems/synchro-protocol.md), [class design — MVP1 IDs](05-class-design-mvp1.md#mvp1-content-ids-locked). Protocol **rules** [#10](https://github.com/miramocha/griddungeon-game/issues/10) done; S1 **tutorial beat** [#35](https://github.com/miramocha/griddungeon-game/issues/35) · [synchro § S1](02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe).

Full Navigator roster unlocks post-MVP1.

---

## 5. Explicitly deferred (not blocking MVP1)

| Item | When |
|------|------|
| FOE combat patrol + mid-battle join ([005](../decisions/005-foe-combat-patrol.md), [010](../decisions/010-chain-foe-battle.md)) | MVP2 |
| **Autopilot** — pathfind on discovered tiles ([ADR 021](../decisions/021-autopilot-mvp2.md)) | MVP2 |
| Gather/fish **minigame**, synthesis | MVP2 |
| Cinematic / QTE skills | MVP2 optional |
| Gamepad, rebind UI | Post-MVP1 |
| Exploration animation speed UI (presets in [ADR 018](../decisions/018-exploration-animation-speed.md)) | Post-MVP1 |
| Reduce UI motion (accessibility) | Post-MVP1 |
| Leg bind, paralysis, burn, speed buffs | Post-MVP1 |
| Traps, encounter suppress | Post-MVP1 |
| **Protocol Deploy** / **Protocol Transform** ([023](../decisions/023-protocol-deploy-sortie-summon.md), [024](../decisions/024-protocol-transform.md)) | Post-MVP1 |
| Guest (`MVP1+`) | Stretch |
| Floor level painter (Editor → `StratumFloor`) | Post-MVP1; MVP1 may hand-author one test floor |
| Multi-level map layer toggle in HUD | Post-MVP1 |
| MapProxy + minimap camera (debug 3D preview) | Deferred / optional |
| Setting name / tone brief | [00 — Vision § Tone](00-vision.md#tone--setting) (municipal underworks; UI palette in [map cell art](02-systems/map-cell-art.md#visual-tone-municipal-underworks)) |

---

## 6. Open for tuning only (locked structure)

Numbers can move in data without ADR change:

- Synchro Charge % per action, Protocol skill power, encounter rates, `stepsPerMove`, shop prices.

---

## 7. Pull order (GitHub backlog)

**Waves** are labeled **`pull-w01`** … **`pull-w08`** on game-repo issues — a suggested implementation sequence, not calendar weeks. Filter the [project board](https://github.com/users/miramocha/projects/3) by label, or **Status → Ready** for the active wave.

| Wave | What it was for | Outcome |
|------|-----------------|--------|
| **1** (`pull-w01`) | **Persistence + campaign spine** — JSON save/load ([#32](https://github.com/miramocha/griddungeon-game/issues/32)) and S1 bootstrap / spawn routing ([#33](https://github.com/miramocha/griddungeon-game/issues/33)) | **Done** |
| **2** (`pull-w02`) | **Combat HUD skeleton** — AGI strip, command panel, HP ([#34](https://github.com/miramocha/griddungeon-game/issues/34)) so combat is playable before polish | **Done** |
| **3+** | Content, hub loop, map art, tutorials, vertical slice | See table below |

UI epic [#19](https://github.com/miramocha/griddungeon-game/issues/19): [#34](https://github.com/miramocha/griddungeon-game/issues/34) done → [#35](https://github.com/miramocha/griddungeon-game/issues/35) reactive + Synchro tutorial → [#36](https://github.com/miramocha/griddungeon-game/issues/36) hub + explore HUD.

| Wave | Label | Pull next (top → bottom) | Status |
|------|-------|--------------------------|--------|
| **1** | `pull-w01` | [#32](https://github.com/miramocha/griddungeon-game/issues/32) Save → [#33](https://github.com/miramocha/griddungeon-game/issues/33) Campaign | **Done** |
| **2** | `pull-w02` | [#34](https://github.com/miramocha/griddungeon-game/issues/34) Combat HUD skeleton | **Done** |
| **3** | `pull-w03` | [#13](https://github.com/miramocha/griddungeon-game/issues/13) Hub · [#12](https://github.com/miramocha/griddungeon-game/issues/12) ContentDB · [#52](https://github.com/miramocha/griddungeon-game/issues/52) class skill rules | **Ready** (current) |
| **4** | `pull-w04` | [#26](https://github.com/miramocha/griddungeon-game/issues/26) map painter · [#20](https://github.com/miramocha/griddungeon-game/issues/20) FoeSystem · [#56](https://github.com/miramocha/griddungeon-game/issues/56) enemy targeting rules | Backlog |
| **5** | `pull-w05` | [#35](https://github.com/miramocha/griddungeon-game/issues/35) Combat reactive + Synchro tutorial UI | Backlog |
| **6** | `pull-w06` | [#30](https://github.com/miramocha/griddungeon-game/issues/30) B3F · [#11](https://github.com/miramocha/griddungeon-game/issues/11) summon · [#36](https://github.com/miramocha/griddungeon-game/issues/36) Hub + explore HUD | Backlog |
| **7** | `pull-w07` | [#31](https://github.com/miramocha/griddungeon-game/issues/31) XP + loot | Backlog |
| **8** | `pull-w08` | [#15](https://github.com/miramocha/griddungeon-game/issues/15) Vertical slice (integration) | Backlog |
| — | `pull-epic` | [#19](https://github.com/miramocha/griddungeon-game/issues/19) UI epic — closes when #35–#36 done (#34 done) | Backlog |

**Closed since wave plan was written:** [#29](https://github.com/miramocha/griddungeon-game/issues/29) B2F · [#27](https://github.com/miramocha/griddungeon-game/issues/27) pause · [#60](https://github.com/miramocha/griddungeon-game/issues/60) target selection · [#65](https://github.com/miramocha/griddungeon-game/issues/65) stale targets · design [#1](https://github.com/miramocha/griddungeon-design-docs/issues/1)–[#5](https://github.com/miramocha/griddungeon-design-docs/issues/5) content/review docs.

Board: [Codename: GridDungeon (project 3)](https://github.com/users/miramocha/projects/3) — open items ordered to match waves 1→8 where the API allows.

---

## Related

- [00 — Release scope](00-release-scope.md)
- [00 — Vision](00-vision.md) — success criteria
- [05 — Class design MVP1](05-class-design-mvp1.md) — concrete classes, assembly layout, folder structure
- [Game phase](02-systems/game-phase.md) — design goals, diagrams, macro phase flow ([ADR 017](../decisions/017-game-phase-controller.md))
- [README](../README.md)
