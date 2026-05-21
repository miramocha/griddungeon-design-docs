# MVP1 — Implementation Spec

Single checklist for the **first playable**. Locked exploration/combat rules: [ADR 014](../decisions/014-mvp1-exploration-map.md), [ADR 015](../decisions/015-mvp1-combat.md). Scope table: [release scope](00-release-scope.md).

---

## 1. Player-facing loop (MVP1)

```
Hub (inn save, guild 6, hospital, shop)
  → Enter Stratum 1 (Union bar 100%)
  → Explore B1F–B3F (FPV + auto-map + FOE on grid)
  → Random fights + FOE contact → battle arena
  → Win / flee → loot / XP → skill points at hub
  → Defeat stratum 1 boss on B3F (MVP1 vertical slice goal)
  → Hub heal / save / equip
```

**Not in MVP1:** synthesis, gather **minigame**, fishing, **FOE combat patrol / mid-battle join**, cinematics, gamepad, 3D hub walk, multiplayer.

---

## 2. Systems checklist

### Exploration & map ([ADR 014](../decisions/014-mvp1-exploration-map.md))

| # | Requirement | Doc |
|---|-------------|-----|
| ✅ | WASD + QE strafe/turn, ~0.2s step lerp | [ADR 001](../decisions/001-grid-movement.md) |
| ✅ | Auto-map, no drawing | [ADR 002](../decisions/002-mapping-model.md) |
| ✅ | Wall: bump + cell perimeter reveal | [ADR 014](../decisions/014-mvp1-exploration-map.md) |
| ✅ | Map fullscreen — movement pass-through | [ADR 014](../decisions/014-mvp1-exploration-map.md) |
| ✅ | FOE step patrol + grid sprite | [ADR 003](../decisions/003-foe-step-patrol.md) |
| ✅ | FOE contact → fight; flee + retreat cell | [ADR 011](../decisions/011-foe-flee-retreat.md) |
| ✅ | FOE respawn on hub return | [ADR 008](../decisions/008-campaign-defaults.md) |
| ✅ | Gather node: one-click instant loot (no minigame) | [ADR 014](../decisions/014-mvp1-exploration-map.md) |
| ⬜ | One test floor 20×20 + stairs | [dungeons & encounters](03-content/dungeons-and-encounters.md) |

### Combat ([ADR 015](../decisions/015-mvp1-combat.md))

| # | Requirement | Doc |
|---|-------------|-----|
| ✅ | Battle arena + enemy slots (not FPV fight) | [ADR 013](../decisions/013-combat-scene-rendering.md) |
| ✅ | 6 core + 0–2 aux; Navigator off-formation | [ADR 004](../decisions/004-auxiliary-slots.md), [007](../decisions/007-navigator-role.md) |
| ✅ | AGI queue UI; Union phase at 100% | [ADR 006](../decisions/006-union-team-bar.md) |
| ✅ | Enemy front + back rows (5 slots max) | [ADR 015](../decisions/015-mvp1-combat.md) |
| ✅ | Fixed camera + Fixed skills only | [combat presentation](02-systems/combat-presentation.md) |
| ✅ | Damage + status MVP1 subset | [combat](02-systems/combat.md), [status](02-systems/combat-status-and-buffs.md) |
| ✅ | FOE combat patrol **off** (MVP2) | [ADR 005](../decisions/005-foe-combat-patrol.md) deferred |
| ⬜ | 8 enemy types + 1 boss encounter group | content |
| ⬜ | One summon — **Summoner-only** `deploy_test_drone` (scripted) | [party classes](02-systems/party-and-classes.md#summon-skills--summoner-only), [ADR 016](../decisions/016-summon-control-mvp1.md) |

### Hub & progression

| # | Requirement | Doc |
|---|-------------|-----|
| ✅ | Inn save, hospital, shop, Guild + **Navigator Office** | [hub](02-systems/hub-and-services.md) |
| ✅ | 6 classes day one; skill points at hub | [party](02-systems/party-and-classes.md) |
| ✅ | Stats: HP, MP, STR, TEC, AGI, VIT, LUC | [progression](02-systems/character-progression.md) |
| ✅ | 1 Navigator + 2 Union skills (MVP1 kit) | [navigator](02-systems/navigator.md), [union](02-systems/union.md) |
| ⬜ | 3 skills per class minimum | content |
| ⬜ | Weapon + 3 armor + 1 accessory | [progression](02-systems/character-progression.md) |

### Tech ([ADR 012](../decisions/012-unity-6-stack.md))

| # | Requirement |
|---|-------------|
| ✅ | Unity 6 + URP + Input System + Shader Graph–first |
| ✅ | `GamePhaseController` + hub / explore / combat phase controllers ([ADR 017](../decisions/017-game-phase-controller.md)) |
| ⬜ | `CombatSimulator` unit tests for damage + AGI order |
| ⬜ | PC default bindings shipped |

---

## 3. Content slice (Stratum 1 MVP1)

| Floor | Goal |
|-------|------|
| **B1F** | Tutorial layout, 0–1 FOE, stairs down |
| **B2F** | First bind/poison enemies, 1 FOE |
| **B3F** | Stratum boss FOE + stairs (MVP1 “win”) |

Defer B4F–B5F polish until loop proven.

---

## 4. MVP1 Navigator & Union (placeholder content)

| Asset | MVP1 |
|-------|------|
| **Navigator** | `guild_handler` — unlocked day one; aura: Union gain +5% |
| **Union skills** | `union_strike` (damage), `union_mend` (heal all living core) |

Full Navigator roster unlocks post-MVP1.

---

## 5. Explicitly deferred (not blocking MVP1)

| Item | When |
|------|------|
| FOE combat patrol + mid-battle join ([005](../decisions/005-foe-combat-patrol.md), [010](../decisions/010-chain-foe-battle.md)) | MVP2 |
| Gather/fish **minigame**, synthesis | MVP2 |
| Cinematic / QTE skills | MVP2 optional |
| Gamepad, rebind UI | Post-MVP1 |
| Leg bind, paralysis, burn, speed buffs | Post-MVP1 |
| Traps, encounter suppress | Post-MVP1 |
| Guest (`MVP1+`) | Stretch |
| Setting name / tone brief | Parallel art |

---

## 6. Open for tuning only (locked structure)

Numbers can move in data without ADR change:

- Union % per action, skill power, encounter rates, `stepsPerMove`, shop prices.

---

## Related

- [00 — Release scope](00-release-scope.md)
- [00 — Vision](00-vision.md) — success criteria
- [05 — Class design MVP1](05-class-design-mvp1.md) — concrete classes, assembly layout, folder structure
- [Game phase](02-systems/game-phase.md) — design goals, diagrams, macro phase flow ([ADR 017](../decisions/017-game-phase-controller.md))
- [README](../README.md)
