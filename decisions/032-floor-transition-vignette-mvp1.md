# ADR 032 — Floor transition vignette

**Status:** Accepted  
**Date:** 2026-05-28  
**Aligns with:** [ADR 017](017-game-phase-controller.md) (macro phases stay C#), [ADR 012](012-unity-6-stack.md) (Timeline + Cinemachine in stack), [floor transition](../docs/02-systems/floor-transition.md), [floor art FPV](../docs/02-systems/floor-art-fpv.md)

## Context

Floor changes (stairs, hub re-entry, campaign warp) previously loaded map data and floor art **synchronously** in `ExplorationPhaseController` without a presentation beat ([floor art FPV — transitions](../docs/02-systems/floor-art-fpv.md#floor-transitions)). That worked but had no **presentation beat** — unlike EO / *Labyrinth of Galleria* loading-room moments (black void + threshold prop + short camera move).

`com.unity.cinemachine` is already in the game manifest; exploration FPV still uses `ExplorationCameraRig` (parent camera to party pivot). A dedicated **transition vignette** needs its own camera stack, not a new `GamePhase`.

**Distinction:** This ADR is **not** combat skill cinematics ([ADR 027](027-combat-cinematic-timeline-events.md), [ADR 015](015-mvp1-combat.md) — `Fixed` only). It is a **macro floor-change mask** (~1.5–3.5 s), same class of problem as hub leave fade ([hub and services](../docs/02-systems/hub-and-services.md)).

## Decision

### 1. (launch) ships a floor transition vignette

| Topic | Launch |
|-------|------|
| **Triggers** | S1 **stairs up/down** (B1F↔B2F↔B3F); **exploration → hub** (gate `stairsUp`); **hub → stratum** enter; campaign **floor change** via `TryChangeFloor` |
| **Presentation** | Black-backed **3D vignette** (door / hatch / threshold prop) + **Cinemachine 3** virtual cameras; optional Timeline |
| **Gameplay** | Stay in **`GamePhase.Exploration`** for floor-to-floor; **→ Hub** switches phase under black; input gated via `ExplorationPresentationGate` during exploration beats |
| **Floor commit** | C# **only** — map, foes, spawn, save slices, `FloorArtPresenter` unload/load **during** the beat |
| **Fallback** | Missing beat asset → **fade + sequential load** (no hard block) |
| **Content** | **One default** beat (`stairs_default`) + catalog override per `leaveKey`→`enterKey` when authored |

**Not required at launch close:** unique beat per stair pair; hub root-menu camera pans; combat arena camera migration to Cinemachine.

### 2. Authority vs presentation

| Layer | Owner |
|-------|--------|
| When floor changes, spawn cell, campaign gates | `ExplorationPhaseController` + `S1CampaignResolver` ([ADR 025](025-campaign-exploration-target.md)) |
| Transition orchestration (gate, beat, commit timing) | **`FloorTransitionPresenter`** (Runtime) — single owner per floor change |
| 3D prop, camera, audio | Beat prefab / Timeline under `Assets/Scenes/Transitions/` |
| Macro phase | Unchanged — **no** `GamePhase.FloorTransition` |

**Commit timing (locked):** floor **map/foe commit** runs **after** the door vignette ends (`NotifyBeatEnd` or catalog `durationMax`), on the **second fade to black** — **not** on `NotifyThreshold`. `NotifyThreshold` is optional (SFX / door open) only. Hub → stratum also **spawns the party** in the commit delegate (`CommitHubEnterFloorSession`) before the final fade-in.

### 3. Load sequence (replaces same-frame load)

During `TryChangeFloor` / hub enter exploration (vignette path — see [authoring guide](../docs/04-dev/authoring-floor-transition-beats.md#what-the-player-sees-stairs_default)):

1. `ExplorationPresentationGate` acquire + HUD suppress; exploration rig off; screen **snap/fade to black**
2. Spawn beat prefab (if catalog resolves); Cinemachine brain **on** for transition vcams
3. `UnloadFloorArt()` — await complete (dungeon view may stay hidden for hub enter)
4. Fade **from** black — door beat visible
5. Wait for `BeatEndFired` → fade **to** black → destroy beat
6. **Commit** delegate (map, foes; stairs: spawn via `ApplyFloorSessionSideEffects`; hub: spawn in commit)
7. `LoadFloorArt(enterKey)` under black — await complete
8. Attach `ExplorationCameraRig` at spawn FPV — fade **in** to level; release gate

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
- **Docs:** [release scope](../docs/00-release-scope.md) checklist row; [release scope](../docs/00-release-scope.md) in-scope line.

## Related

- [Floor transition system](../docs/02-systems/floor-transition.md)
- [Floor art FPV](../docs/02-systems/floor-art-fpv.md)
- [Game phase](../docs/02-systems/game-phase.md)
