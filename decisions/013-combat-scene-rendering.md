---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/combat
---
# ADR 013 — Combat Scene Rendering (Battle Arena vs World Space)

**Status:** Accepted  
**Date:** 2026-05-20  
**Amended:** 2026-05-23 — arena rig supports up to **6** enemy slot anchors (EO IV+ **3+3** formation; [ADR 015](015-mvp1-combat.md)).

## Context

On encounter, the game must show **enemies** (and party feedback) somehow. Two families of approach:

1. **World space** — fight in the live dungeon cell; camera re-frames in-place.
2. **Battle arena** — leave FPV; dedicated combat view with **fixed backdrop** and slot-based enemy placement.

Exploration is **FPV grid** ([02 — Dungeon navigation](../docs/02-dungeon-navigation.md)). Combat already assumes a **fixed battle camera** per skill ([combat presentation](../docs/02-systems/combat-presentation.md)), not per-room dungeon angles.

## Decision

**Use a battle arena (fixed background + slot rig), not in-world combat geometry, at launch and default long-term.**

| Layer | Behavior |
|-------|----------|
| **Exploration** | FPV dungeon scene stays loaded; **frozen** (input off, optional dim/blur) |
| **Transition** | Short blend (~0.3–0.6s): flash or wipe → **Combat scene** overlay or sub-scene |
| **Combat view** | **Stratum/floor-themed backdrop** (2D art or 3D set piece) + **enemy slot anchors** (up to 6) + party UI (portraits / row strip) |
| **Enemies** | Rendered at slot transforms — **sprites or 3D models** on the arena, **not** at grid world coordinates |
| **Return** | On win/flee/wipe → reverse transition → resume FPV at fight anchor cell |

`CombatEntryContext` carries `floorId`, `biome`, `encounterType` (random / FOE / boss), optional `foeId` → selects `BattleBackground` asset.

## Rejected (for launch)

| Option | Why |
|--------|-----|
| **Full in-world combat** | FPV corridors fight clipping, lighting, and camera; fights fixed camera anyway; art cost per room |
| **Pure UI-only** (no enemy meshes) | Loses EO/Wizardry identity; cinematics and QTE need a stage |
| **Seamless in-place camera only** | Still need slot layout; backdrop quality inconsistent per cell |

**Optional later experiment:** “arena backdrop” that **samples** the current cell’s wall/floor textures into a blurred plate — cosmetic only, still slot-based enemies.

## Consequences

- **`CombatPhaseController.OnEnter`** calls **`CombatScenePresenter`** to load `BattleScene` (additive) or enable `CombatLayer` on the same Unity scene ([ADR 017](017-game-phase-controller.md)).
- `DungeonExplorer` pauses; grid position unchanged until fight ends.
- FOE mid-battle join ([ADR 010](010-chain-foe-battle.md)) = new enemy **slides into empty slot** on arena, not walking into FPV cell.
- FOE flee retreat ([ADR 011](011-foe-flee-retreat.md)) applies to **grid** after transition out — no need for enemy mesh on exploration grid during fight.
- Content authors **`BattleBackground`** per stratum (and boss variants), not per dungeon cell.

## Related

- [Combat scene & enemies](../docs/02-systems/combat-scene.md)
- [Combat presentation](../docs/02-systems/combat-presentation.md)
- [Combat](../docs/02-systems/combat.md)
- [04 — Tech notes](../docs/04-tech-notes.md)
- [ADR 017 — Game phase controller](017-game-phase-controller.md)
- [Game phase](../docs/02-systems/game-phase.md)
