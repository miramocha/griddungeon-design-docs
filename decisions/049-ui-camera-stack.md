---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/ui
---
# ADR 049 — UI camera stack (URP) + presentation actor layers

**Status:** Accepted  
**Date:** 2026-07-11  
**Amended:** 2026-07-12 — backdrop sandwich shipped ([#430](https://github.com/miramocha/griddungeon-game/issues/430) / [PR #431](https://github.com/miramocha/griddungeon-game/pull/431))  
**Aligns with:** [ADR 033](033-hub-environment-cinemachine.md) (hub Cinemachine), [ADR 047](047-party-menu-3d-stage.md) (party menu 3D stage), [ADR 038](038-centralized-ui-presentation-lifecycle.md) (overlay lifecycle), [ADR 027](027-combat-cinematic-timeline-events.md) (future skill cinematics), [centralized UI services](../docs/04-dev/centralized-ui-services.md)

## Context

Hub, party menu, floor-transition beats, and future story/skill cinematics show **3D environment** with **UITK chrome** and **character models**. Design needs:

- UITK **backdrop** visually **in front of** 3D environment but **behind** character actors.
- Screen HUD (`GamePanelSettings` Overlay — command rail, hints, modals) stays **above** the whole stack.
- Exploration FPV and combat arena should not pay multi-camera cost unless UI stack is active.
- Future cutscenes/skills must resolve actors without rebaking prefab layers.

URP **camera stacking** (Base + Overlay cameras) sandwiches **3D** draw order. UITK is separate: [`PanelRenderMode`](https://docs.unity3d.com/6000.3/Documentation/ScriptReference/UIElements.PanelRenderMode.html) exposes only **`ScreenSpaceOverlay`** and **`WorldSpace`** — there is **no** uGUI-style **Screen Space - Camera** mode.

| UITK mode | Sandwich behavior |
|-----------|-------------------|
| **Screen Space - Overlay** (`GamePanelSettings`) | Composites **after** all cameras — always above 3D; cannot sit between env and characters. |
| **World Space** | Renders as **3D panel geometry** (depth-sorted); layer culling applies, but it does **not** automatically slot into a URP overlay stack like a camera-attached canvas. |

**Implication:** layer routing + char overlay ([#428](https://github.com/miramocha/griddungeon-game/issues/428)) and **mid-stack hero backdrop** ([#430](https://github.com/miramocha/griddungeon-game/issues/430) / [PR #431](https://github.com/miramocha/griddungeon-game/pull/431)) ship as one system. **Shipped path:** world-space `UIDocument` on `UiBackdrop`, drawn on the stack **overlay** camera with focused roster on `UiCharacters`; non-focused roster on `UiEnvironment` (base pass). Per-frame cover sync: `UiBackdropWorldPanelSync` + `UiBackdropCoverLayout`. **Deferred alternative:** UITK → `RenderTexture` → env-layer quad (or URP **Render Objects** — [#429](https://github.com/miramocha/griddungeon-game/issues/429)).

## Decision

### 1. `UiCameraStackSession` owns render mode (presenters do not)

Three automatic modes:

| Mode | When | Cameras |
|------|------|---------|
| **Off** | Exploration FPV; combat (until combat backdrop ships) | Main camera only; overlays disabled; base mask `UiLayers.OffMask` (all layers except UI stack routing — includes `Exploration`) |
| **SingleCam** | UI 3D registered; **no backdrop UITK shown** | Main camera; base mask `UiEnvironment` \| `UiWorldBackdrop` \| `UiCharacters` |
| **Stack** | Backdrop UITK **shown** (`SetBackdrop`) | Base: `UiEnvironment` \| `UiWorldBackdrop`; overlay: `UiBackdrop` (world-space hero UITK) \| `UiCharacters` (focused roster) |

**Stack trigger:** only a **backdrop** `UIDocument` bound via `SetBackdrop` — not Overlay HUD (`InputHint`, command rail, etc.).

Hiding backdrop → session falls back to **SingleCam** (if env/chars still registered) or **Off**.

### 2. Tags at instantiate; layers on register

| Mechanism | When | Purpose |
|-----------|------|---------|
| **Unity tag** | Immediately after `Instantiate` | Identity for cutscenes/skills (`CompareTag`, find actors) |
| **Unity layer** | `RegisterEnvironment` / `RegisterCharacters` | Camera culling, stack routing, shadow masks |

Locked tags (see [ui-camera-stack.md](../docs/04-dev/ui-camera-stack.md)):

- `PresentationCharacter` — party menu pool, future cinematic actors
- `PresentationEnemy` — combat battle prefabs (prep for combat cinematics)
- `PresentationEnvironment` — hub town, party stage, transition beat shells

Prefabs stay on **Default** layer. **No** baked stack layers in assets.

### 3. UITK split

| PanelSettings | `PanelRenderMode` | Role |
|---------------|-------------------|------|
| `GamePanelSettings` | `ScreenSpaceOverlay` | Global HUD — always on top of camera stack |
| `UiBackdropPanelSettings` | `WorldSpace` (`PanelRenderMode` value **1**) | Hero / modal backdrop — cloned at runtime by `UiBackdropDocumentSetup`; **not** `ScreenSpaceOverlay` |

`SetBackdrop` is the **Stack mode trigger** when the bound `UIDocument` is active. Party menu: `PartyMenuClassBackdropPresenter` → `PartyMenuClassBackdrop` facade.

### 4. Camera stack layout (Stack mode)

| Pass | Culling / source | Content |
|------|------------------|---------|
| Base | `UiEnvironment` \| `UiWorldBackdrop` | Town, stage floor, beat shell, greybox sphere; **non-focused** roster roots (`SetCharacterDrawLayer` → `UiEnvironment`) |
| Stack overlay | `UiBackdrop` \| `UiCharacters` | World-space hero UITK (`UiBackdropWorldPanelSync`); **focused** roster roots |
| Above all | `GamePanelSettings` overlay | Command rail, hints, modals |

Legacy `UiStackOverlay1_Backdrop` child cameras are **removed** at runtime (`UiCameraStackRig`) — one stack overlay camera (`UiStackOverlay`) only. Cinemachine drives the base camera lens; backdrop panel syncs from base each frame.

Char overlay camera **disabled** when zero characters registered.

Post-processing: **one** camera in the stack (base or char overlay — profile in Frame Debugger).

### 5. Integration scope (initial)

| Surface | Env register | Char register | Backdrop |
|---------|--------------|---------------|----------|
| Hub | Town root | — | When hub shell uses backdrop |
| Party menu | Stage root | Roster on present | Menu backdrop on open |
| Floor transition beat | Beat root | Beat actors if any | If authored |
| Story / VN | Scene set | 3D actors | Modal backdrop |
| Exploration FPV | — | — | Off |
| Combat arena | — | — | Off (until combat backdrop) |

`ExplorationCameraSession` keeps **Cinemachine brain locks**; `UiCameraStackSession` is separate.

### 6. Presentation spawn tagging standard (locked)

**Not** “every `GameObject` must be tagged.” **Yes:**

> Every runtime **`Instantiate` under presentation/cinematic ownership** must set a locked **`PresentationActorTags`** value on the **spawn root** in the same frame. **Layer** assignment stays **`UiCameraStackSession.Register*`** only.

| In scope (tag required) | Tag | Notes |
|-------------------------|-----|-------|
| Party roster visuals | `PresentationCharacter` | `PartyCharacterVisualRegistry` — tag on pool spawn, even while stashed |
| Combat battle prefabs | `PresentationEnemy` | `CombatScenePresenter.SpawnEnemyVisuals` |
| Hub town, party stage, transition beat **roots** | `PresentationEnvironment` | Root only — not every child mesh |
| Future skill / cutscene spawns | `PresentationCharacter` or `PresentationEnemy` | Per actor role |

| Exempt (no presentation tag required) | Why |
|---------------------------------------|-----|
| `FloorArtPresenter` / floor props | Exploration gameplay geometry — not UI stack |
| Editor authoring / dev bootstrap primitives | e.g. `PartyVisual` capsule unless promoted to real actor |
| Plugin / vendor `Instantiate` | Out of project control |
| UITK / `VisualElement` trees | Not `GameObject` |

**Rules:**

- Use **`PresentationActorTags.Apply*`** — no scattered `go.tag = "..."` literals.
- **Root only** — do not recurse tags to children unless a future ADR says otherwise.
- **One tag per GO** (Unity limit) — role is exclusive; use components/refs for combatant id, class id.
- **`Register*`** may `Debug.Assert(CompareTag)` in dev — tag proves spawn path; layer proves render pass.
- **Do not** require tags on exploration floor art or generic props — avoids tag taxonomy sprawl.

**Rejected:** project-wide “tag every `Instantiate`” rule (high migration cost, blurs presentation vs gameplay).

### 7. Layer naming standard — no Default for camera routing (phased)

**Rejected:** project-wide ban on **Default layer (0)** — Unity’s fallback for new objects; most third-party assets ship on Default; full migration is high cost and **conflicts** with phase-1 unregister restore (see below).

**Accepted (phased):**

> **Do not rely on Default for camera routing.** Every **camera-visible** runtime root must sit on a **named layer** for its **current role**. Default is OK only for transient/editor objects, vendor defaults, or brief state before first assignment.

| Layer | Phase | When set | Purpose |
|-------|-------|----------|---------|
| `UiEnvironment` | **1** ([#428](https://github.com/miramocha/griddungeon-game/issues/428)) | `RegisterEnvironment` | UI stack env pass |
| `UiCharacters` | **1** | `RegisterCharacters` / `SetCharacterDrawLayer` foreground | UI stack char pass (focused roster in Stack) |
| `UiBackdrop` | **1** ([#430](https://github.com/miramocha/griddungeon-game/issues/430)) | `SetBackdrop` + active `UIDocument` | World-space hero UITK on stack overlay |
| `UiWorldBackdrop` | **1** | `WorldBackdropLayerRules` on env register | Greybox / transition sphere behind stage |
| `Exploration` | **2** | Floor art spawn / scope | Dungeon geometry — **not** UI stack (`FloorArtPresenter`) |
| `PresentationIdle` | **2** (optional) | Pool spawn / unregister | Stashed roster not on stage — replaces Default as idle target |

**Phase 1 (#428):**

- Prefabs stay **Default** in assets; **no** baked stack layers.
- `Register*` → `UiEnvironment` / `UiCharacters`; **unregister restores Default** (snapshot via `GameObjectLayerScope`).
- Camera masks are **explicit** (`UiEnvironment` only on base in Stack mode) — do not use “everything except UI” masks that accidentally include unrelated Default geometry.

**Phase 2 (follow-up):**

- Move `FloorArtPresenter` roots to **`Exploration`** so hub/UI cameras never bleed dungeon mesh via Default.
- Optionally restore pooled chars to **`PresentationIdle`** instead of Default when stashed.
- Code review / **fresh-reviewer**: camera-visible roots that **stay** on Default while a stack camera could see them → Should fix (must `Register*` or use a named non-UI layer).

**Default still OK for:** editor primitives, vendor spawns, UITK-unrelated scratch, objects never drawn by main or stack cameras.

**Why not ban Default entirely:** unregister needs a known idle layer; exploration and combat domains need named homes before Default can be eliminated; fighting Unity’s default for every new GO adds friction without removing the need for a “misc” bucket.

## Rejected

| Option | Why |
|--------|-----|
| **Tags for camera culling** | Cameras ignore tags |
| **Baked layers on prefabs** | Breaks SingleCam vs Stack; pool reuse |
| **Overlay HUD as stack trigger** | Would force Stack during all hub/combat UI |
| **Stack always on in hub** | Wastes passes when backdrop hidden — auto SingleCam |
| **Screen Overlay for mid UITK sandwich** | Cannot render behind 3D characters |
| **UITK as uGUI Screen Space - Camera** | `PanelRenderMode` has no equivalent — see Context |
| **World Space UITK without per-frame sync** | Lens/orbit drift — rejected for party menu; shipped path syncs cover from base camera each frame |
| **Single-camera merge (quad + focused MToon on base)** | Deferred — MToon queue not tunable; char overlay remains until quad SG proves otherwise |
| **Tag every `GameObject` on `Instantiate`** | Tag soup; floor art / props are not presentation actors — see §6 |
| **Ban Default layer entirely** | Huge prefab migration; conflicts with phase-1 restore; vendor/editor defaults — see §7 |

## Consequences

- Runtime: `UiCameraStackSession`, `UiCameraStackRig`, `GameObjectLayerScope`, `PresentationActorTags`, `UiBackdropWorldPanelSync`, `UiBackdropCoverLayout` ([#428](https://github.com/miramocha/griddungeon-game/issues/428) + [#430](https://github.com/miramocha/griddungeon-game/issues/430)).
- DevBootstrap: main camera + one stack overlay child (`UiStackOverlay`); `UiCameraStackRig` wires masks per mode.
- Project layers: `UiEnvironment`, `UiCharacters`, `UiBackdrop`, `UiWorldBackdrop` (phase 1); `Exploration` (+ optional `PresentationIdle`) in phase 2; tags in `TagManager`.
- Spawn sites tag roots; register/unregister with phase presenters.
- Party menu: `PartyMenuClassBackdropPresenter` + `PartyMenuClassBackdrop.uxml`; `SetCharacterDrawLayer` splits non-focused (`UiEnvironment`) vs focused (`UiCharacters`) during member focus; hero label on `UiBackdrop` overlay pass — shipped [#430](https://github.com/miramocha/griddungeon-game/issues/430) / [PR #431](https://github.com/miramocha/griddungeon-game/pull/431).
- Dev guide: [ui-camera-stack.md](../docs/04-dev/ui-camera-stack.md) · Cover math: [world-space-uitk-cover-fit.md](../docs/04-dev/world-space-uitk-cover-fit.md)

## Backdrop sandwich (shipped — [#430](https://github.com/miramocha/griddungeon-game/issues/430))

**Goal:** `env 3D → hero UITK → focused character → overlay HUD`.

**Shipped (world-space overlay pass):**

1. `PartyMenuClassBackdropPresenter` binds `UiBackdropPanelSettings` + `PartyMenuClassBackdrop.uxml` via `UiBackdropDocumentSetup` (runtime clone, `WorldSpace`, `targetTexture = null`).
2. `SetBackdrop` → Stack mode; backdrop root on `UiBackdrop`; `UiBackdropWorldPanelSync` applies CSS **object-fit: cover** via `UIDocument.worldSpaceSize` (`UiBackdropCoverLayout`, 1920×1080 reference height + live aspect width) and syncs pose from base camera each frame while Stack is active — see [world-space UITK cover-fit](../docs/04-dev/world-space-uitk-cover-fit.md) ([#439](https://github.com/miramocha/griddungeon-game/pull/439)).
3. `SetCharacterDrawLayer(root, foreground, backdropSplitActive)` — non-focused roster → `UiEnvironment` (base); focused → `UiCharacters` (overlay with backdrop).
4. Stack overlay camera lens copied from base (`UiCameraStackRig.SyncStackOverlayLensFromBase`) — required for **MToon** roster (character render queue not tunable for manual sandwich ordering).
5. Backdrop root `pickingMode = Ignore`; label reveal timed with silhouette (`PartyMenuClassBackdropContentTransition`).

**Player builds:** `Assets/Resources/UI/UiBackdropRuntimeContent.asset` when scene refs missing.

**Off mode culling:** `UiLayers.OffMask` = all layers except `UiStackRoutingMask` (`UiEnvironment`, `UiCharacters`, `UiBackdrop`, `UiWorldBackdrop`) so hub `SingleCam` can exclude `Exploration` and Off restores FPV floor art after hub exit.

## Deferred alternatives

**RT → env-layer quad:** UITK `PanelSettings.targetTexture` + screen-aligned quad on base pass — fallback if world-space backdrop depth proves fragile on a target platform. Spike assets: `Assets/Shaders/Graph/UI/UITKBackdrop.shadergraph` + `Assets/UI/Materials/UITKBackdrop.mat` — **not** the shipped path.

**URP Render Objects** and presentation VFX (e.g. character silhouette when occluded) — optional ([#429](https://github.com/miramocha/griddungeon-game/issues/429)).

**Single-camera merge** (quad or backdrop + focused MToon on base) — deferred; MToon queue not tunable; char overlay remains until proven otherwise.

Closed: [griddungeon-game#430](https://github.com/miramocha/griddungeon-game/issues/430) · Shipped: [PR #431](https://github.com/miramocha/griddungeon-game/pull/431).

## References

- [UI camera stack (dev)](../docs/04-dev/ui-camera-stack.md)
- [World-space UITK cover-fit (dev)](../docs/04-dev/world-space-uitk-cover-fit.md)
- [Centralized UI services](../docs/04-dev/centralized-ui-services.md)
- [Party menu 3D stage (ADR 047)](047-party-menu-3d-stage.md)
