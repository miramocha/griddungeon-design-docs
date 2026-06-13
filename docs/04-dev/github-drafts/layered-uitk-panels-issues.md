# GitHub drafts — Layered UITK panels epic

**Not filed on GitHub yet.** Copy bodies into `gh issue create` when ready.  
**Repo:** `miramocha/griddungeon-game` (epic + implementation).  
**ADR:** [ADR 037](../../../decisions/037-layered-uitk-panels.md) in design-docs.

---

## Epic

**Title:** Epic: Layered UITK panels (HUD depth)

**Labels:** `epic`, `P2`, `UI`, `pull-w08` (or post-MVP1 wave — adjust)

**Body:**

```markdown
## Summary

Split monolithic phase HUDs (`ExplorationHud`, `CombatHud`) into **smaller `UIDocument` panel components** so chrome can stack, slide, and tilt independently — HUD feels more 3D without changing Core rules or combat arena model.

**Authority:** [ADR 037 — Layered UITK panels](https://github.com/miramocha/griddungeon-design-docs/blob/main/decisions/037-layered-uitk-panels.md)  
**Dev note:** [layered-uitk-panels.md](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/04-dev/layered-uitk-panels.md)

## Goals

- Tier 1: screen-space multi-panel (shared `GamePanelSettings`, `sortingOrder` stack, USS depth)
- Optional Tier 2: world-space panels for Navigator / command rail (separate child issues)
- Keep [ui-event-contract](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/04-dev/ui-event-contract.md) — Runtime unchanged

## Child issues

- [x] #244 — POC: exploration map split (`ExplorationMapCoordinator`, `MinimapPanelView`, `ExpandedMapOverlayView`) — **merged**
- [ ] #TBD — Exploration panel split (strip + pause)
- [ ] #TBD — Combat panel split (rail / center / AGI)
- [ ] #TBD — Cross-panel focus orchestration
- [ ] #TBD — (optional) World-space panel spike

## Out of scope

- In-world combat on exploration grid (ADR 013)
- uGUI migration
- Core / combat math changes

## Acceptance (epic)

- [ ] Exploration map, party strip, pause = separate `UIDocument` roots with documented sort order
- [ ] Combat command rail, center column, AGI strip = separate roots (pickers modals stack above)
- [ ] `InputRouter` + focus navigation work across panels (ADR 026)
- [ ] `InputHintPresenter` unchanged (global strip)
- [ ] Dev bootstrap + Edit Mode smoke tests green
```

---

## Child 1 — POC: MapPanel — **SHIPPED** ([#244](https://github.com/miramocha/griddungeon-game/pull/244))

**Title:** UI: Split exploration map into minimap and expanded overlay

**Status:** Merged 2026-06-13. `ExplorationMap` GO + `ExplorationMapCoordinator` + `MinimapPanelView` / `ExpandedMapOverlayView`; legacy `MapView` obsolete shim.

**Shipped tasks:**

- [x] `ExplorationMap` GO with coordinator + two child `UIDocument` presenters
- [x] Drop `BindToHud` — trees built via `MapGridHostBuilder` on each surface root
- [x] `ExplorationHudView` orchestrates party strip only; map on sibling GO
- [x] `DevSceneComposition.WireExplorationMap`
- [x] Expanded overlay sort **100**; M-toggle = scale in + minimap slide retract

**Tests:** `ExplorationMapCoordinatorTests`, `MinimapPanelPresenterTests`, `ExpandedMapOverlayPresenterTests`

---

## Child 2 — Exploration full split

**Title:** UI: Split exploration HUD into panel components

**Labels:** `UI`, `P2`, `M`

**Body:**

```markdown
## Summary

Complete exploration Tier 1 split: **party strip** and **pause overlay** each own `UIDocument`. `ExplorationHudView` = orchestrator only.

Depends on: #TBD (MapPanel POC)  
Epic: #TBD

## Tasks

- [ ] `PartyStripPanel` — extract from `ExplorationHud.uxml`
- [ ] `PauseOverlay` — already `PartyMenuOverlayView` (sort 250); optional further split of formation pane only
- [ ] Document sort stack in dev note
- [ ] USS depth pass on strip (optional tilt/shadow)

## Test plan

- Pause `Esc` stacks above map; quit confirm works
- Party strip show/hide unchanged vs #36 behavior
- `InputHints` still global strip
```

---

## Child 3 — Combat panel split

**Title:** UI: Split combat HUD into panel components

**Labels:** `UI`, `P2`, `L`

**Body:**

```markdown
## Summary

Split `CombatHud.uxml` monolith into **command rail**, **center column** (rosters + synchro + log preview), **turn-order strip**. Skill/item pickers may use dedicated high-sort doc.

Epic: #TBD  
Related: combat HUD frame [#179](https://github.com/miramocha/griddungeon-game/issues/179)

## Tasks

- [ ] Extract UXML/USS per panel; preserve BEM class names
- [ ] `CombatHudView` coordinates visibility + event bind
- [ ] `BattleRewardScreenView` — own doc or stay sibling with explicit sort
- [ ] Extend `CommandPanel.uss` depth pattern to other rails if useful

## Test plan

- F3 combat — planning focus `W/S`, targeting, log `L`, skill picker modal
- Reactive presenter + `CombatPresentationGate` unchanged
```

---

## Child 4 — Focus orchestration

**Title:** UI: Cross-panel focus owner for layered UIDocuments

**Labels:** `UI`, `P2`, `M`

**Body:**

```markdown
## Summary

UITK focus does not cross `UIDocument` boundaries. Add thin **focus owner** so `InputRouter` / combat + exploration handlers route `MenuNavigate` / `Submit` / `Cancel` to exactly one active panel.

Epic: #TBD  
Authority: [ADR 026](https://github.com/miramocha/griddungeon-design-docs/blob/main/decisions/026-combat-menu-focus-navigation.md), ADR 037 §4

## Tasks

- [ ] Define `IUitkFocusPanel` or orchestrator API (active panel register/release)
- [ ] Modal open/close pushes/pops owner
- [ ] Edit Mode tests — synthetic navigate reaches correct panel only

## Non-goals

- Gamepad rebinding (PC MVP1)
```

---

## Child 5 — Optional world-space spike

**Title:** UI: World-space UITK panel spike (Tier 2)

**Labels:** `UI`, `P2`, `S`, `spike`

**Body:**

```markdown
## Summary

Spike **one** world-space `PanelSettings` + `UIDocument` (e.g. Navigator corner placeholder or tilted command rail quad). Validates scale, input hit-test, camera parenting before broader Tier 2.

Epic: #TBD  
Defer until Tier 1 exploration/combat splits land.

## Done when

- [ ] Document pixels-per-unit + parent transform convention
- [ ] Play Mode: panel readable at 1080p + ultrawide smoke
- [ ] Decision: promote to Navigator epic or stay screen-space
```

---

## `gh` commands (when filing)

Replace `#TBD` with epic number after epic is created.

```powershell
# Epic (game repo)
gh issue create --repo miramocha/griddungeon-game `
  --title "Epic: Layered UITK panels (HUD depth)" `
  --label "epic,P2,UI" `
  --body-file path\to\epic-body.md

# Link ADR in design-docs README when Accepted (separate PR)
```
