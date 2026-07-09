---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/ui
  - domain/hub
---
# ADR 047 — Party menu 3D stage (hex backdrop + Cinemachine)

**Status:** Accepted  
**Date:** 2026-07-06  
**Related:** [ADR 033](033-hub-environment-cinemachine.md) (hub 3D + CM brain pattern), [ADR 046](046-combat-arena-plates-camera.md) (combat arena — separate layout), [ADR 037](037-layered-uitk-panels.md) (UITK overlay stack), [ADR 017](017-game-phase-controller.md) (phase ownership), [game #400](https://github.com/miramocha/griddungeon-game/issues/400)

## Context

Tab **party menu** (`PartyMenuOverlayView`, sort **250**) is a full-screen UITK shell on hub and exploration. `CharacterDetail` (sort **251**) and `PartyFormationFloater` (sort **260**) provide inspect and member focus. EO-style character status screens use a **large character illustration**; our scratchpad defers portrait on `CharacterDetail` and places **3D character preview on a separate surface** ([party / character UI ref](../docs/refs/party-character-ui.md)).

Hub already locks **full-screen 3D backdrop + UITK overlay** for guild town ([hub environment presentation](../docs/02-systems/hub-and-services.md#hub-environment-presentation), [ADR 033](033-hub-environment-cinemachine.md)). Party menu should mirror that pattern: **3D hex formation stage** behind existing party UITK whenever the menu is open.

**Combat is separate.** The battle arena uses linear slot rig + enemy `battlePrefab` only ([ADR 013](013-combat-scene-rendering.md), [ADR 046](046-combat-arena-plates-camera.md)). Menu hex layout must **not** couple to `CombatArenaFormationLayout` or `CombatScenePresenter`. Future party battle animation uses the **arena** rig, not the menu stage.

## Decision

### When the 3D stage is active

| Rule | Choice |
|------|--------|
| **Trigger** | Party menu **open** (all sections: Inventory, Formation, Equipment, Skills, Quit) |
| **Phases** | **Hub** and **Exploration** only — gated by existing `PartyMenuGate` (not combat) |
| **UITK** | Unchanged ownership — `PartyMenuOverlayView`, floater, `CharacterDetail` |
| **Hub town** | Hide hub environment geo while party menu open when hub backdrop is active (`HubEnvironmentPresenter.SetTownVisible(false)`) |
| **Exploration dungeon** | Hide `DungeonSceneHost` while menu open; `FloorArtPresenter.SuppressUnloadOnDisable` keeps floor art loaded; restore view + FPV (`ExplorationCameraRig.ReattachPartyFpv`) on close |

### Visual instances — stash lifecycle

| Rule | Choice |
|------|--------|
| **Prefab (v1)** | `PlayerCharacter_Default` — one instance per **occupied** party grid slot; same prefab all members until per-class prefabs land |
| **When to spawn** | Once at roster bind (load / recruit) — not per menu open |
| **Stash** | Child of `GameState`: `PartyCharacterVisualStash` at fixed offset (e.g. `Y = -500`); `SetActive(false)` while stashed |
| **Menu open** | Reparent to stage `Slot_{gridIndex}`; `SetActive(true)` |
| **Menu close** | Reparent to stash; `SetActive(false)` |
| **Phase changes** | Stash persists Hub ↔ Exploration ↔ Combat; **never** show party stage in combat |

**Rejected:** spawn/destroy per menu toggle; sharing combat arena anchors; menu hex layout in combat.

### Formation layout — menu hex only

UITK floater keeps **2×4 grid** (`PartyFormationLayout`). **3D stage** uses a **hex ring**:

| Grid index | Role | Facing |
|------------|------|--------|
| 0–2 | Front cores | **−Z** (toward camera default) |
| 3, 7 | Aux flanks | Match row (front aux −Z, back aux +Z) |
| 4–6 | Back cores | **+Z** (opposite front row) |

`PartyMenuStageFormationLayout` (Core) maps grid index → slot transform + yaw. **Not** referenced from combat types.

### Per-slot idle poses (no VRMA)

| Piece | Choice |
|-------|--------|
| **Clips** | Humanoid `AnimationClip` assets — `PartyMenuIdle_Pose01`–`06` under `Assets/Art/Characters/PartyMenu/Idles/` |
| **Catalog** | `PartyMenuStagePoseCatalog` SO — `AnimationClip[8]` by grid index |
| **Animator** | Required on VRM humanoid; **one** state `PartyMenuIdleBase.controller` shell |
| **Runtime** | `AnimatorOverrideController` per visual swaps `Idle` clip per slot (`PartyCharacterVisualPose`) |
| **VRMA** | **Out of scope** — `Runtime.VrmAnimation` always null for menu |

Six authored poses cover core slots; aux grids **3** and **7** borrow a front/back row clip until dedicated aux poses exist.

### VRM LookAt — focused member only

| State | LookAt |
|-------|--------|
| Overview (floater undocked) | **Off** all — body faces slot yaw only |
| Floater docked + member focused | **On** for **that** visual — VRM 1.0 `CalcYawPitchToGaze` toward main camera (`LateUpdate`) |
| Focus change | Previous reset; new member on |
| Menu close | Reset all |

Only **one** character tracks camera at a time (matches floater single-focus UX).

### Material silhouette — focused member reveal

| State | 3D character colors |
|-------|---------------------|
| Menu open (any section) | **All silhouette** (black base + shade via `CharacterMaterialSilhouette`) |
| Floater undocked | **All silhouette** |
| Floater docked, no member focus | **All silhouette** |
| Floater docked + member focus | **Focused = revealed**; others silhouette |
| Menu close / stash | Restore cached colors |

Shares the **same debounced focus signal** as LookAt (`PartyMenuStagePresenter` → `PartyCharacterVisualRegistry.SetMemberRevealGridIndex`). Animator `Silhouette` layer on `PartyMenuIdleBase.controller` (`MemberRevealed` bool) syncs with C# material lerp (path B until `_CharacterSilhouetteReveal` ships on toon shaders). Implementation traps (inactive animator, MToon10 material instances, pristine cache): [centralized UI gotchas § silhouette reveal](../docs/04-dev/centralized-ui-gotchas.md#party-menu-3d--silhouette-reveal-stuck-black-charactermaterialsilhouette).

### Cinemachine — overview vs orbit

Session uses **one** `CinemachineBrain` ([ADR 033](033-hub-environment-cinemachine.md)). Extend `ExplorationCameraSession` with `partyMenuBrainLock` (same pattern as hub/combat locks).

| Mode | Active vcam | Behavior |
|------|-------------|----------|
| Menu open, floater **undocked** | `CM_Overview` | Wide shot; Look At = `FormationCenter` |
| Floater **docked**, member focus (core grid only) | `CM_FormationOrbit` | `PartyMenuStageOrbitRig` rotates pivot to slot yaw and sets orbit vcam local height from focused head; **separate Look At** = head transform |
| Focus change (debounced ~200ms) | Same orbit vcam | DOTween yaw/height blend **and** swap Look At target |

**Position vs rotation (CM 3):** Orbit pivot + local camera offset own **where** the camera stands; `Hard Look At` with **Use Separate Look At Target** aims at the focused member’s head — decoupled from pivot rotation on one `CinemachineCamera`.

**Head aim:** `Animator.GetBoneTransform(HumanBodyBones.Head)` on each instance; optional child `HeadLookAt` with small Y offset for framing (same intent as `BattleCameraRig.LookAtHeightAboveStageFocus`). VRM LookAt tracks the orbit vcam transform while docked.

**Rejected:** Cinemachine **Spline Dolly** on a circular path for v1 (greybox uses yaw pivot + height tween instead); look-at formation center while focused on one member; aux grid slots driving orbit (core slots only).

### Authority

| Layer | Owner |
|-------|--------|
| Menu open/close, section chrome | `PartyMenuOverlayView` |
| Floater dock + member focus | `PartyFormationFloaterPresenter` → `PartyMenuStage` facade |
| 3D session, brain lock, vcam | `PartyMenuStagePresenter` |
| Visual pool, pose, LookAt, silhouette | `PartyCharacterVisualRegistry`, `PartyCharacterVisualPose`, `VrmCharacterLookAt`, `CharacterMaterialSilhouette` |
| Stage anchors, orbit rig, vcams | `PartyMenuStageAnchorSet`, `PartyMenuStageOrbitRig` on `party_menu_stage_greybox` prefab |
| Debounced focus → camera | `PartyMenuMemberFocusDebouncer` (Core) |

### Content paths (game repo)

| Asset | Path |
|-------|------|
| Character prefab | `Assets/Art/Characters/PlayerCharacter_Default/PlayerCharacter_Default.prefab` |
| Idle clips | `Assets/Art/Characters/PartyMenu/Idles/PartyMenuIdle_Pose01`–`06` |
| Pose catalog | `Assets/Content/PartyMenu/PartyMenuStagePoseCatalog.asset` |
| Idle controller | `Assets/Art/Characters/PartyMenu/PartyMenuIdleBase.controller` |
| Stage prefab | `Assets/Scenes/PartyMenu/party_menu_stage_greybox.prefab` |

Editor menu: `GridDungeon → Party Menu → Create Greybox Stage Prefab` (mirror hub environment creator).

## Consequences

- **Game:** New Runtime presenters + Core layout/debouncer; VRM10 asmdef reference; Dev Bootstrap wires `PartyMenuStage` under `GameState`.
- **Art:** Six idle poses + additive breathing layer on idle controller; stage greybox + orbit pivot rig + two vcams; tune yaw stops and orbit height in playtest.
- **Docs:** [custom party UI § 3D stage](../docs/04-dev/custom-party-ui.md#party-menu-3d-stage), [exploration UI](../docs/02-systems/exploration-ui.md), [party / character UI ref](../docs/refs/party-character-ui.md).

## Out of scope (v1)

- Party models in combat arena / battle animation loops
- VRMA / `Runtime.VrmAnimation` for menu
- Per-class character prefabs from `ClassDefinition`
- Party menu in combat phase
- Player-driven orbit camera input

## Related

- [Custom party UI — 3D stage](../docs/04-dev/custom-party-ui.md#party-menu-3d-stage)
- [Hub environment presentation](../docs/02-systems/hub-and-services.md#hub-environment-presentation)
- [Exploration UI — party menu](../docs/02-systems/exploration-ui.md#party--pause-menu-partymenuoverlayview)
- [Party / character UI ref](../docs/refs/party-character-ui.md)
- [ADR 046 — Combat arena](046-combat-arena-plates-camera.md) (do not share formation layout)
