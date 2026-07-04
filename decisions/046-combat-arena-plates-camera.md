---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/combat
  - domain/ui
---
# ADR 046 — Combat arena plates (Option A) + camera focus

**Status:** Accepted  
**Date:** 2026-07-04  
**Related:** [ADR 013](013-combat-scene-rendering.md) (battle arena), [ADR 039](039-uitk-dotween-show-hide.md) (PopIn dismiss), [ADR 017](017-game-phase-controller.md) (phase ownership), game epic [#384](https://github.com/miramocha/griddungeon-game/issues/384)

## Context

Combat uses a **battle arena** with up to six enemy slot anchors ([ADR 013](013-combat-scene-rendering.md)). Launch shipped:

- Optional **3D `battlePrefab`** per enemy on slot transforms via `CombatScenePresenter`
- A **fixed battle camera** with impulse shake on resolve ([combat presentation](../docs/02-systems/combat-presentation.md))
- Enemy HP chrome in a **top-center `enemy-roster`** embedded in `CombatHud` (`CombatRosterView`)

That embedded roster **occludes the 3D arena center** and duplicates a second enemy plate stack. EO-style play needs **transient** HP plates above the models during targeting and hit beats, not a permanent HUD strip.

## Decision

### World layer — 3D models on slot rig

| Rule | Choice |
|------|--------|
| **Asset** | `EnemyDefinition.battlePrefab` — optional `GameObject` per enemy |
| **Spawn** | `CombatScenePresenter.SpawnEnemyVisuals` parents prefab under `EnemySlot_0..5` |
| **Clear** | `CombatScenePresenter.ClearAndDestroyEnemyVisuals` on combat exit |
| **Orchestration** | `CombatPhaseController` calls presenter; no spawn logic in phase controller |
| **Layout** | `CombatArenaFormationLayout` maps tactical slot index → local position on anchor |

Exploration **grid sprites** and combat **battle prefabs** stay separate assets linked by enemy id.

### UI layer — Option A (locked)

**Reject** world-space UITK per slot (Option B).

| Piece | Choice |
|-------|--------|
| **Service** | `CombatArenaPlatePresenter` — centralized `UIDocument` @ `sortingOrder` **15** (between party floater **10** and `CombatHud` **20**) |
| **Facade** | `CombatArenaPlate` — `EnemyRoster`, `SyncTargetableEnemyPlates`, `RevealSlotForHpBeat`, `HideImmediate` |
| **View** | `CombatArenaPlateView` implements `IEnemyFormationRoster` |
| **Anchor math** | `CombatArenaOverlayAnchor` — `Camera.WorldToScreenPoint` + `RuntimePanelUtils.CameraTransformWorldToPanel`; plates track slot transforms each frame while revealed |
| **Motion** | Per-slot **PopIn** via `CentralizedUiPresentation.CreatePopIn` ([ADR 039](039-uitk-dotween-show-hide.md)) |
| **CombatHud** | Remove top-center `enemy-roster` from `CombatHud.uxml`; delete `CombatRosterView` |

`CombatTargetSelectionCoordinator`, `CombatHudReactivePresenter`, and `EnemyFormationGridTargetPicker` bind **`CombatArenaPlate.EnemyRoster`** (`IEnemyFormationRoster`) instead of an embedded roster view.

### Plate reveal policy

Plates are **hidden idle**. Reveal only for:

| Reason | When | Plates shown |
|--------|------|--------------|
| **Targeting** | `CombatController.IsSelectingTarget` vs living enemies | All valid enemy targets (`CombatArenaPlate.SyncTargetableEnemyPlates`) |
| **HP beat** | Enemy damage / heal / death on reactive beat | Affected slot only (`RevealSlotForHpBeat`, default hold **~0.28s**) |

**Not revealed:** acting highlight, MP-only updates, status-only ticks, planning chrome.

During **enemy targeting**, `PartyFormationFloater` **slides down** (collapse dismiss) so party floater plates do not block ally picks; `CombatArenaPlate` **snap-hides** when switching to ally targeting so its full-bleed layer does not block party grid LMB.

### Camera — Fixed presentation focus

| Trigger | Behavior |
|---------|----------|
| **Action start** | `CombatController.OnActionCommitted` → `BattleCameraRig.NudgeZoomToTarget(slot)` **before** resolve |
| **Party attack/skill vs enemy** | Focus **target** enemy slot (`BattleCameraFocusPolicy.GetFocusEnemySlotIndex`) |
| **Enemy attack/skill** | Focus **attacking** enemy slot (wind-up on actor slot) |
| **Target pick (enemy)** | `OnTargetPickFocusChanged` nudges toward hovered/focused enemy slot while selecting |
| **Turn start / targeting end** | `RestoreDefaultFramingAnimated` |
| **Skip focus** | Guard, Switch, Flee, Protocol, Item, heal/buff ally skills, Deploy — `ShouldFocusForAction` returns false |
| **Resolve shake** | Unchanged — `CinemachineImpulse` on `OnActionResolved` / Protocol hits |

Focus policy lives in **`BattleCameraFocusPolicy`** (Core); `BattleCameraRig` owns DOTween framing only.

## Rejected

| Option | Why |
|--------|-----|
| **World-space UITK plates parented to slot transforms** | UITK panel scale / DPI / sort-order fights; harder to share `GamePanelSettings` with HUD |
| **Keep embedded `enemy-roster` + overlay plates** | Double chrome; center column blocks arena view |
| **Camera nudge on resolve only** | Wind-up lacks target framing; EO-style read needs pre-hit zoom |
| **Reveal plates for entire combat** | Clutters arena; idle center column should stay clear |

## Consequences

- **Content:** authors assign `battlePrefab` on `EnemyDefinition`; dev slime prefab for F3 bootstrap ([#385](https://github.com/miramocha/griddungeon-game/issues/385)).
- **Bootstrap:** `DevSceneComposition.WireCombatArenaPlate` — child of `GameState`; refs on `GameState` + `CombatScenePresenter`.
- **Tests:** `CombatArenaOverlayAnchorTests`, `CombatScenePresenterSpawnTests`, `CombatArenaPlateViewTests`, `BattleCameraRigTests` / `ShouldFocusForAction` ([#390](https://github.com/miramocha/griddungeon-game/issues/390)).
- **Docs:** [combat scene](../docs/02-systems/combat-scene.md), [combat presentation](../docs/02-systems/combat-presentation.md), [centralized UI services](../docs/04-dev/centralized-ui-services.md), [custom party UI](../docs/04-dev/custom-party-ui.md).
- **Presentation bus** ([#312](https://github.com/miramocha/griddungeon-game/issues/312)) — optional follow-up; plates use presenter + facade today.

## Related

- [Combat scene & enemies](../docs/02-systems/combat-scene.md)
- [Combat presentation](../docs/02-systems/combat-presentation.md)
- [Centralized UI services § Combat arena plate](../docs/04-dev/centralized-ui-services.md#combat-arena-plate--combatarenaplatepresenter--combatarenaplate)
- [Custom party UI § Enemy arena plates](../docs/04-dev/custom-party-ui.md#enemy-arena-plates-combatarenaplate)
- Game epic [#384](https://github.com/miramocha/griddungeon-game/issues/384)
