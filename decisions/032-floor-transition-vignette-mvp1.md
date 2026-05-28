# ADR 032 — Floor transition vignette (MVP1)

**Status:** Accepted  
**Date:** 2026-05-28  
**Aligns with:** [ADR 017](017-game-phase-controller.md) (macro phases stay C#), [ADR 012](012-unity-6-stack.md) (Timeline + Cinemachine in stack), [floor transition](../docs/02-systems/floor-transition.md), [floor art FPV](../docs/02-systems/floor-art-fpv.md)

## Context

Floor changes (stairs, hub re-entry, campaign warp) today load map data and floor art **synchronously** in `ExplorationPhaseController.TryLoadTargetFloor` ([floor art FPV — MVP1 path](../docs/02-systems/floor-art-fpv.md#floor-transitions--mvp1-vs-planned-transition-scene)). That works but has no **presentation beat** — unlike EO / *Labyrinth of Galleria* loading-room moments (black void + threshold prop + short camera move).

`com.unity.cinemachine` is already in the game manifest; exploration FPV still uses `ExplorationCameraRig` (parent camera to party pivot). A dedicated **transition vignette** needs its own camera stack, not a new `GamePhase`.

**Distinction:** This ADR is **not** combat skill cinematics ([ADR 027](027-combat-cinematic-timeline-events.md), [ADR 015](015-mvp1-combat.md) — `Fixed` only). It is a **macro floor-change mask** (~1.5–3.5 s), same class of problem as hub leave fade ([hub and services](../docs/02-systems/hub-and-services.md)).

## Decision

### 1. MVP1 ships a floor transition vignette

| Topic | MVP1 |
|-------|------|
| **Triggers** | S1 **stairs up/down** (B1F↔B2F↔B3F); **exploration → hub** (gate `stairsUp`); **hub → stratum** enter; campaign **floor change** via `TryChangeFloor` |
| **Presentation** | Black-backed **3D vignette** (door / hatch / threshold prop) + **Cinemachine 3** virtual cameras; optional Timeline |
| **Gameplay** | Stay in **`GamePhase.Exploration`** for floor-to-floor; **→ Hub** switches phase under black; input gated via `ExplorationPresentationGate` during exploration beats |
| **Floor commit** | C# **only** — map, foes, spawn, save slices, `FloorArtPresenter` unload/load **during** the beat |
| **Fallback** | Missing beat asset → **fade + sequential load** (no hard block) |
| **Content** | **One default** beat (`stairs_default`) + catalog override per `leaveKey`→`enterKey` when authored |

**Not required for MVP1 close:** unique beat per stair pair; hub root-menu camera pans; combat arena camera migration to Cinemachine.

### 2. Authority vs presentation

| Layer | Owner |
|-------|--------|
| When floor changes, spawn cell, campaign gates | `ExplorationPhaseController` + `S1CampaignResolver` ([ADR 025](025-campaign-exploration-target.md)) |
| Transition orchestration (gate, beat, commit timing) | **`FloorTransitionPresenter`** (Runtime) — single owner per floor change |
| 3D prop, camera, audio | Beat prefab / Timeline under `Assets/Scenes/Transitions/` |
| Macro phase | Unchanged — **no** `GamePhase.FloorTransition` |

**Commit timing (locked):** floor data + art load at **`OnThreshold`** animation/Timeline notification (door open / step into closet). If beat has no marker, commit at **beat end** before fade-up.

### 3. Load sequence (replaces same-frame load)

During `TryChangeFloor` / hub enter exploration:

1. `ExplorationPresentationGate.Acquire("floor_transition")`
2. Hide or freeze FPV + map HUD under black
3. Play vignette (Cinemachine priority → transition vcams)
4. `FloorArtPresenter.UnloadFloorArt()` — await complete
5. Commit logic floor (`MapSystem`, foes, spawn) — **not** before threshold unless beat specifies end-only
6. `FloorArtPresenter.LoadFloorArt(enterKey)` — await complete
7. End vignette; release gate; restore exploration camera

**Rule:** `LoadFloorArt` must **not** be called from both `ExplorationPhaseController` and `FloorTransitionPresenter` on the same change ([floor art FPV](../docs/02-systems/floor-art-fpv.md)).

### 4. Cinemachine

- **One** `CinemachineBrain` on main camera for the session.
- Transition beats use **virtual cameras** on the vignette prefab; exploration keeps `ExplorationCameraRig` until a later migration.
- Hub leave may call the same presenter with `beatId = hub_enter_stratum` or fade-only fallback.

### 5. UVS / Visual Scripting

Presentation only ([uvs phase presentation](../docs/02-systems/uvs-phase-presentation.md)) — graphs may fire audio/VFX on `PhaseChanged` or transition signals; **must not** own floor commit or `RequestTransition` rules.

## Consequences

- **Game:** refactor `TryChangeFloor` to async/coroutine path through `FloorTransitionPresenter`; [#102](https://github.com/miramocha/griddungeon-game/issues/102) Play Mode tests target transition enter → load → exit.
- **Art:** author `Transitions/stairs_default` prefab (black skybox, door mesh, 2 vcams, Timeline).
- **Docs:** [mvp1-spec](../docs/mvp1-spec.md) checklist row; [release scope](../docs/00-release-scope.md) in-scope line.

## Related

- [Floor transition system](../docs/02-systems/floor-transition.md)
- [Floor art FPV](../docs/02-systems/floor-art-fpv.md)
- [Game phase](../docs/02-systems/game-phase.md)
