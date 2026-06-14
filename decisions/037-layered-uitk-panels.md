# ADR 037 — Layered UITK panels (HUD depth)

**Status:** Proposed (draft)  
**Date:** 2026-06-08  
**Epic (draft):** [game #TBD — layered UITK panels](https://github.com/miramocha/griddungeon-game/issues/TBD)  
**Aligns with:** [ADR 012](012-unity-6-stack.md) (UI Toolkit default), [ADR 013](013-combat-scene-rendering.md) (arena vs FPV — combat stays slot-based), [ADR 026](026-combat-menu-focus-navigation.md) (focus + confirm), [ADR 033](033-hub-environment-cinemachine.md) (3D hub backdrop pattern), [navigator § 3D presence](../docs/02-systems/navigator.md#consider--explore--navigator-3d-presence) (optional world-attached rig)

## Context

(launch) HUD is **screen-space UI Toolkit**: one shared `GamePanelSettings.asset`, multiple top-level `UIDocument` roots (`ExplorationMap`, `CombatHud`, `HubHud`, overlays), orchestrator-only `ExplorationHud`, and **`sortingOrder`** for stack depth.

Within exploration and combat, phase chrome splits across documents at different maturity:

| Phase | Orchestrator GO | Logical chunks today |
|-------|-----------------|----------------------|
| Exploration | `ExplorationHud` (**no** `UIDocument`) | **Shipped [#244](https://github.com/miramocha/griddungeon-game/pull/244):** `ExplorationMap` (minimap + expanded), `PartyFormationFloater`, `PartyMenuOverlay` |
| Combat | `CombatHud` (monolith `UIDocument`) | command rail, enemy/party rosters, synchro, AGI strip, log, cloned pickers |

Legacy `MapView` shim delegates to `ExplorationMapCoordinator` until scenes refresh. `InputHintPresenter`, `PartyMenuOverlay`, and `StoryHud` already prove the **multi-document** bootstrap pattern.

Product direction: HUD should feel **more dimensional** — layered plates, slide/tilt depth, independent draw order — **without** rewriting combat rules or moving fights onto the exploration grid ([ADR 013](013-combat-scene-rendering.md)).

This is **not** full diegetic UI (map as in-world prop, command rail in dungeon cell). It is **presentation layering** on top of the existing Runtime event contract ([ui-event-contract](../docs/04-dev/ui-event-contract.md)).

## Decision

### 1. Split monolith HUDs into **panel components** — each owns one `UIDocument`

| Principle | Rule |
|-----------|------|
| **One panel = one concern** | Map, party strip, pause, command rail, roster column, AGI strip, log preview — separate `GameObject` + `UIDocument` when they need independent sort order or USS depth |
| **Orchestrator, not mega-doc** | `ExplorationHudView` / `CombatHudView` become coordinators (phase visibility, event fan-out); they do **not** require a single root UXML shell |
| **Shared scale** | Tier 1 keeps **one** `GamePanelSettings` (1920×1080, Match Height) unless a panel needs a deliberate exception |
| **Depth** | `UIDocument.sortingOrder` is the authoritative draw stack between panels; USS `translate` / `rotate` / `scale` on each panel for parallax (extend `CommandPanel.uss` poke pattern) |
| **Runtime boundary** | `GridDungeon.Core` / phase controllers unchanged; only `GridDungeon.UI` + bootstrap wiring |

**Rejected for Tier 1:** replacing UITK with uGUI Canvas per widget; merging all HUD into one document “for simplicity.”

### 2. Two tiers — ship Tier 1 before optional world-space

| Tier | Render mode | Goal |
|------|-------------|------|
| **Tier 1 (default)** | Screen Space — Overlay (current) | Split documents + sort stack + USS depth illusion |
| **Tier 2 (optional follow-up)** | World Space `PanelSettings` on selected transforms | Parallax vs camera / arena; Navigator corner rig; **not** required for Tier 1 acceptance |

Tier 2 panels parent to camera rig or `CombatScenePresenter` slot anchors — still **not** in-grid combat geometry.

### 3. Target panel map (rough)

**Exploration** (under `ExplorationHud` orchestrator root or siblings):

```
MapPanel          sort 0   (today MapView + mount)
PartyStripPanel   sort 10
PauseOverlay      sort 50
InputHint         sort 300  (already separate)
```

**Combat**:

```
CombatCommandRail   sort 20
CombatCenterColumn  sort 21  (enemy roster, synchro, party roster, log preview)
CombatTurnOrder     sort 22
CombatPickers       sort 40  (skill / item modals — may stay cloned into picker doc)
BattleReward        sort 45  (today on CombatHud GO)
InputHint           sort 300
```

Exact sort values are implementation tuning; order matters more than absolute numbers.

### 4. Input and focus

| Topic | Decision |
|-------|----------|
| **Authority** | `InputRouter` + existing handlers remain entry points ([ADR 009](009-input-bindings-pc.md), [ADR 026](026-combat-menu-focus-navigation.md)) |
| **Cross-panel focus** | UITK focus does not span `UIDocument` trees — introduce a thin **focus owner** (or extend handlers) so exactly one panel receives `MenuNavigate` / `Submit` / `Cancel` at a time |
| **Modals** | Higher `sortingOrder` panel owns focus while open; dismiss restores previous owner |
| **Mouse** | Unchanged — one-shot clicks on visible panel hit targets |

### 5. Global input hints

`InputHintPresenter` stays a **separate screen-space strip** ([global input hints](../docs/04-dev/shared-menu-picker-ui.md#global-input-hints)) — not folded into diegetic panels.

### 6. Release scope

| Phase | Deliverable |
|-------|-------------|
| **POC** | Exploration map split — **shipped** [#244](https://github.com/miramocha/griddungeon-game/pull/244): `ExplorationMap` GO, `MinimapPanelView` + `ExpandedMapOverlayView`, drop `BindToHud` |
| **Wave A** | Exploration full split (map + strip + pause) + bootstrap/tests |
| **Wave B** | Combat split (rail / center / AGI / pickers) |
| **Wave C (optional)** | Tier 2 world-space for 1–2 panels (Navigator corner, command rail tilt) |
| **Out of scope** | Core rule changes; in-world combat; replacing `ui-event-contract` pull model |

## Consequences

- **Game:** refactor `ExplorationHudView`, `MapView`, `CombatHudView`, `DevBootstrapSceneCreator` / `DevSceneComposition`; add panel prefabs or scene children; Edit Mode tests for sort order + focus handoff smoke paths.
- **Docs:** [layered UITK panels dev note](../docs/04-dev/layered-uitk-panels.md); [exploration UI](../docs/02-systems/exploration-ui.md) scene diagram updated ([#244](https://github.com/miramocha/griddungeon-game/pull/244)).
- **Art/USS:** per-panel depth tokens (tilt, shadow, slide) — reuse BEM modifiers; avoid C# `style` writes per `unity-ui-toolkit` rules.

## Related

- [Layered UITK panels — dev / integrator](../docs/04-dev/layered-uitk-panels.md)
- [UI event contract](../docs/04-dev/ui-event-contract.md)
- [Exploration UI](../docs/02-systems/exploration-ui.md)
- [Combat HUD frame layout](../docs/02-systems/combat.md#combat-hud-frame-layout)
- [GitHub issue drafts (not filed)](../docs/04-dev/github-drafts/layered-uitk-panels-issues.md)
