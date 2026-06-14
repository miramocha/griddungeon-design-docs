# ADR 033 — Hub environment camera (Cinemachine)

> **Scope: Optional feature** — not required for initial release.

**Status:** Accepted  
**Date:** 2026-05-29  
**Aligns with:** [ADR 012](012-unity-6-stack.md) (Cinemachine in stack), [ADR 017](017-game-phase-controller.md) (phase-owned presentation), [ADR 032](032-floor-transition-vignette-mvp1.md) (session brain + vcam priority pattern), [hub and services](../docs/02-systems/hub-and-services.md#hub-environment-presentation)

## Context

Later hub presentation reframes a **full-screen 3D guild-town** when the player focuses rows on the **root** hub menu ([hub environment](../docs/02-systems/hub-and-services.md#hub-environment-presentation)). (launch) ships menus and services only; this ADR locks **how** pans run when the hub environment epic wires focus → camera.

`com.unity.cinemachine` **3.x** is already in the game manifest and used for **floor transition** vignettes ([ADR 032](032-floor-transition-vignette-mvp1.md)). Exploration FPV still uses `ExplorationCameraRig` with the brain **off** during normal play. Hub pans are **ambient, debounced, non-blocking** — not skill cinematics ([ADR 027](027-combat-cinematic-timeline-events.md)) and not floor commits.

## Decision

### 1. Hub backdrop camera uses Cinemachine 3 — not DOTween on a rig

| Topic | Decision |
|-------|----------|
| **Package** | `com.unity.cinemachine` **3.x** (`CinemachineCamera`, `CinemachineBrain`) |
| **Rejected** | DOTween (or manual `Camera` lerp) as the primary pan mechanism for hub service anchors |
| **Blend** | **Virtual camera priority** (and optional shared blend asset on the brain) — same class of handoff as transition beats |
| **Anchors** | One authored **`CinemachineCamera`** (or equivalent pose) per root-menu slot + optional **establishing** wide shot |
| **Trigger** | After [debounced root focus settle](../docs/02-systems/hub-and-services.md#debounced-pan-rapid-scroll), presenter raises target vcam priority; previous active hub vcam priority lowered |

Combat may keep DOTween for **subtle hit zoom** on a fixed battle camera ([combat presentation](../docs/02-systems/combat-presentation.md)); that does not apply to hub environment pans.

### 2. Session brain — one brain, phase-aware ownership

| Phase / beat | Brain | Active stack |
|--------------|-------|----------------|
| **Exploration FPV** | Off (unless transition lock) | `ExplorationCameraRig` parents main camera |
| **Floor transition vignette** | On (transition lock) | Beat prefab vcams ([ADR 032](032-floor-transition-vignette-mvp1.md)) |
| **Hub** | **On** while `GamePhase.Hub` | Hub town vcams under `HubEnvironmentPresenter` |
| **Combat** | Off | Fixed battle camera ([ADR 013](013-combat-scene-rendering.md), [ADR 015](015-mvp1-combat.md)) |

- **One** `CinemachineBrain` on the session main camera (Dev Bootstrap / `DevSceneComposition`).
- **`HubEnvironmentPresenter`** (or equivalent) on hub enter: disable exploration FPV parenting, enable brain, activate hub scene vcams; reverse on hub exit.
- **Do not** add a second brain on the hub town prefab.
- Coordinate with `ExplorationCameraSession` / transition lock so hub enter/leave does not leave brain enabled during exploration FPV or disabled mid–floor-transition beat.

### 3. Authority vs presentation

| Layer | Owner |
|-------|--------|
| Macro phase, services, save | `HubPhaseController`, `HubController`, `HubHudView` |
| Root-menu focus index → slot | `MenuFocusNavigator` + `HubRootMenuSlot` ([ADR 026](026-combat-menu-focus-navigation.md)) |
| Debounce + vcam priority | **`HubEnvironmentPresenter`** |
| Anchor poses / blends | Hub town scene art (Transforms + `CinemachineCamera` children) |

Hub camera pan must **not** acquire `HubPresentationGate` (inn save, shop confirm) — menus stay live ([hub — presentation vs gameplay lock](../docs/02-systems/hub-and-services.md#presentation-vs-gameplay-lock)).

### 4. Content layout (authoring)

```
HubTown (scene or additive root)
├── Environment geo
├── CM_Establishing_Wide          ← optional default; priority when no root focus
├── CM_Guild
├── CM_Navigator
├── CM_Shop
├── CM_Hospital
├── CM_Inn
└── CM_Gate_Plaza                 ← all Enter Stratum rows
```

- Map `HubRootMenuSlot` → vcam in presenter data (serialized pairs or catalog asset).
- **Disabled** root rows: presenter **does not** raise vcam priority ([hub locked rows](../docs/02-systems/hub-and-services.md#locked-decisions)).
- **Service sub-menus:** no extra vcams; hold last root anchor.

### 5. Release scope

| Phase | Camera |
|-------|--------|
| **Launch** | No focus → pan (unchanged) |
| **Hub environment POC / later** | Cinemachine-backed pans per this ADR |
| **Defer** | Timeline-driven hub intros; per-sub-menu vcams; combat arena Cinemachine migration |

## Consequences

- **Game:** `HubEnvironmentPresenter` + hub town scene with vcams; extend `ExplorationCameraSession` (or hub-specific session helper) for brain on/off on phase enter/exit; Edit Mode tests for debounce + “no pan when disabled.”
- **Art:** tune blends in Inspector; avoid code-driven camera position each frame.
- **Docs:** [hub-and-services](../docs/02-systems/hub-and-services.md) implementation sketch updated; optional dev authoring note under `docs/04-dev/` when POC lands.

## Related

- [Hub and services — environment presentation](../docs/02-systems/hub-and-services.md#hub-environment-presentation)
- [Floor transition — Cinemachine](../docs/02-systems/floor-transition.md#cinemachine-mvp1)
- [Authoring floor transition beats](../docs/04-dev/authoring-floor-transition-beats.md#cinemachine)
