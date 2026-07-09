---
tags:
  - path/docs/04-dev
  - type/dev
  - scope/required
  - status/active
  - domain/ui
---
# Centralized UI — implementation gotchas

Living list of **non-obvious bugs and review traps** when wiring cross-phase UITK services (`ItemListInventory`, `InputHints`, `CommandRail`, `PartyFormationFloater`, …). For the happy-path pattern, see [centralized UI services](centralized-ui-services.md). For picker APIs and rail focus, see [shared menu & picker UI](shared-menu-picker-ui.md).

**Implementation repo:** [griddungeon-game](https://github.com/miramocha/griddungeon-game) — `Assets/Scripts/UI/Views/`, `Assets/Scripts/Runtime/UI/`.

**Reference consumers:** [`ItemListInventory`](centralized-ui-services.md#item-list-inventory--itemlistinventorypresenter--itemlistinventory) / `ItemListPickerView` ([#207](https://github.com/miramocha/griddungeon-game/issues/207)) — stable PopIn reference. [`CharacterDetail`](centralized-ui-services.md#character-detail--characterdetailpresenter--characterdetail) ([#209](https://github.com/miramocha/griddungeon-game/issues/209)) — second PopIn consumer; same `ICentralizedUiSurface` traps.

---

## How to use this doc

| When | Action |
|------|--------|
| Hit a weird modal / picker bug | Search here before adding guards in phase HUDs |
| Adding a new centralized overlay with show/hide animation | Read **Pop-in exit vs reopen**, **Context switches**, and [centralized UI services § Presentation lifecycle](centralized-ui-services.md#presentation-lifecycle) |
| Wiring presentation bus shells / projectors | Read [presentation-shell-gotchas](presentation-shell-gotchas.md) — apply [presentation-shell.mdc](../../.cursor/rules/presentation-shell.mdc) |
| Public lifecycle vocabulary (`Show` / `Hide` / `IsSettling`) | [ICentralizedUiSurface](centralized-ui-services.md#public-contract-transition-agnostic) ([#207](https://github.com/miramocha/griddungeon-game/issues/207)); epic [#206](https://github.com/miramocha/griddungeon-game/issues/206) |
| Reviewing a migration off embedded pickers | Cross-check **Standalone document** + **Modal rail chrome leak** |
| Hover / click dead on a lower `UIDocument` (keyboard still works) | Read **Pointer dead — `sortingOrder` + `PickingMode`** — verify stack table + pass-through on full-screen chrome |
| Closed a related bug | Add a short entry (symptom → cause → fix → test) in the same PR or follow-up |
| Party menu 3D silhouette / VRM material reveal | Read [§ Party menu 3D — silhouette reveal](#party-menu-3d--silhouette-reveal-stuck-black-charactermaterialsilhouette) |

---

## Pop-in exit vs rapid reopen (`ItemListInventory` / `ItemListPickerView`)

**Symptom:** Hub → Shop → Buy → **X** → spam **Buy** again — buy list never appears (or flashes then vanishes).

**Cause:** `ItemListPickerView.Hide()` runs a **~420ms** `PopInTransition` exit (`PopInTransition.DurationMs`). During that window:

- `IsShown` stays **true** until the exit callback runs.
- `IsSettling` is **true** (public name for the old `IsClosing` / `m_isClosing` trap).
- `RequestedVisible` is **false** after dismiss starts — intent and on-screen state disagree.
- A naive reopen that calls **`Refresh`** (because `IsShown` is still true) only updates row data — it does **not** cancel the exit or re-show the shell.
- When the stale exit callback eventually runs, it applies the hidden USS class and fires the hide callback (`SetContext(Hidden)`, `m_hubMode = Hub`).

`Show()` during exit **is** safe: `CentralizedUiPresentation` / `PopInTransition` bump generation and clear settle state, which suppresses the stale exit callback. The bug is taking the **Refresh** path while `IsSettling`.

**Fix (shipped on [#207](https://github.com/miramocha/griddungeon-game/issues/207)):**

- `ItemListPickerView.Refresh` — if `IsSettling`, delegate to `Show`.
- `ItemListInventoryPresenter.PresentHubShop` / `SetHubShopContext` — use `Refresh` only when `IsShown && !IsSettling`; otherwise `Show`.

**Test:** `ItemListInventoryPresenterTests.SetHubShopMode_RapidReopenAfterCancel_StaysActiveAfterExitAnimation`.

**Rule for new hosts:** Any code that reopens a pop-in picker while an exit may still be running must call **`Show`**, not **`Refresh`**, unless you have explicitly confirmed `!IsSettling`. Treat `IsShown` alone as insufficient.

```csharp
// ❌ BAD — reopen during exit animation
if (m_picker.IsShown)
    m_picker.Refresh(model);
else
    m_picker.Show(model);

// ✅ GOOD — ICentralizedUiSurface vocabulary (#207)
if (m_picker.IsShown && !m_picker.IsSettling)
    m_picker.Refresh(model);
else
    m_picker.Show(model);
```

**Same class of bug elsewhere:** Any overlay using deferred dismiss (`PopInTransition`, slide retract, floater collapse) can race if the host reopens before exit completes. Prefer **`Show`** on reopen entry points, or **`HideImmediate()`** when switching authority (phase/context), not `Refresh`-style data-only updates.

---

## `RequestedVisible` / `IsShown` / `IsSettling` ≠ domain flags

Public surface is **`ICentralizedUiSurface`** only — do not expose legacy `IsActive`, `IsClosing`, or `IsVisible` on facades.

| Member / flag | Meaning | Trap |
|---------------|---------|------|
| `RequestedVisible` | Authority wants the panel open | Can be **true** while exit animation runs if context not cleared yet |
| `IsShown` | Panel presented for current authority | Stays **true** through exit settle until dismiss animation completes ([#207](https://github.com/miramocha/griddungeon-game/issues/207)) |
| `IsSettling` | Enter/exit animation in flight after `Hide()` (or chained dismiss) | **true** during the ~420ms PopIn exit window — use this instead of `IsClosing` |
| `ItemListInventory.IsHubShopActive` | `context == HubShop` **and** `picker.IsShown` | Domain composite — **not** `RequestedVisible`; false after exit completes even if hub mode enum lags |
| `ItemListInventory.IsModalActive` | Hub shop or combat item modal composite | Uses `IsShown` / combat host `IsOpen` — not `IsSettling` alone |
| Visible to player | Hidden USS class off **and** pop-in expanded | Requires `Show` path, not mid-settle `Refresh` |

Hub shop modal rail disable (`CommandPanelModalSupport`) and input hints key off `IsHubShopActive` / `HubMode` — rapid cancel+reopen can leave rail/hint state wrong if hide callbacks run after a reopen. The pop-in reopen fix above is the primary guard; phase owners should still **`RefreshInputHint` / `RebuildServiceFocus`** after shop mode changes.

---

## Character detail — context intent vs on-screen (`CharacterDetail`)

**Symptom:** Formation/Equipment pane thinks detail is open; panel invisible or stale after rapid section swap; party menu sort **251** fights bag modal.

**Cause (pre-#209):** Facade used domain flags (`ActiveContext`, ad-hoc `IsVisible`) that did not track PopIn settle. `Refresh()` during `Hide()` exit updated slot copy without re-presenting the shell — same class as inventory **Refresh while `IsSettling`**.

**Fix (shipped on [#209](https://github.com/miramocha/griddungeon-game/issues/209)):**

- `CharacterDetailPresenter` implements `ICentralizedUiSurface`; facade exposes `RequestedVisible`, `IsShown`, `IsSettling`.
- `Show()` while `IsSettling` bumps `UiTransitionSession` generation (kills in-flight tweens) and re-enters via `PresentCurrentContext` — not `Refresh()` alone.
- Party-menu section swaps call facade `Hide()` on competing sort-251 overlays before opening the next pane ([#411](https://github.com/miramocha/griddungeon-game/issues/411)).
- `SetPartyMenuContext` still uses `TeardownPresentationForContextSwap` on the internal presentation for same-overlay context swaps (formation ↔ equipment).
- `PartyMenuOverlayView` orchestrates context + `Show`/`Hide`; it does **not** own a second PopIn stack ([#208](https://github.com/miramocha/griddungeon-game/issues/208)).

**Tests:** `CharacterDetailPresenterTests` (settle + `HideImmediate`), `PartyMenuSort251LifecycleTests` (bag + detail at sort 251).

**Rule:** Callers distinguish **`ActiveContext`** (which party-menu layout is armed) from **`IsShown`** (whether the PopIn panel is on-screen). Use `IsSettling` before choosing `Refresh` vs `Show`.

---

## Hide vs HideImmediate policy ([#411](https://github.com/miramocha/griddungeon-game/issues/411))

| Call | When |
|------|------|
| `Hide()` | Player dismiss, tab/section switch, competing overlay handoff the player sees |
| `HideImmediate()` | `OnDisable`, phase exit, bootstrap init, story preemption, documented input-stack snap |

**Player-visible paths (animated):** party-menu Q/E section swap (`HideCompetingSort251Overlays`), hub hospital detail exit (`ResetHospitalPickState`), inventory context switch (`ForceHideForContextSwitch`), party-menu close (`FinishPartyMenuClose` unless `snapPresentation: true`), field-skill picker cancel.

**Intentional snap (documented Tier 2):** combat target-mode picker dismiss, party floater dock teardown, story preemption on notice overlay, phase-exit paths on command rail / minimap / skill picker.

`UiTransitionSession` generation cancels stale exit callbacks when `Show()` runs during dismiss — prefer `Hide()` + reopen over `HideImmediate()` on happy paths. Reserve `HideImmediate()` for lifecycle/teardown.

**Tests:** `PartyMenuSort251LifecycleTests`, `CharacterDetailPresenterTests`, `ItemListInventoryPresenterTests` (mid-dismiss reopen).

---

## Context switches and animated dismiss

**Symptom (legacy):** Left combat with item picker mid-close; hub shop opens invisible, or bag + shop contexts fight.

**Cause:** `ItemListInventoryPresenter` owns **one** `ItemListPickerView` across contexts. Stale exit `onComplete` fired after the next context called `Show` when hosts used `Refresh` during settle or skipped `UiTransitionSession` generation.

**Fix (shipped [#411](https://github.com/miramocha/griddungeon-game/issues/411)):** `ForceHideForContextSwitch` calls animated `Hide()` / `Close()` on the leaving context. `Show()` while `IsSettling` bumps generation and re-presents. Phase exit and `OnDisable` still use `HideImmediate()`.

**Rule:** Animated `Hide()` for player-visible dismiss and in-phase overlay handoff. `HideImmediate()` for lifecycle teardown and documented input-stack snaps — not mid-beat Runtime hard cuts ([no hard cuts](uitk-bem-transition-guide.md#no-hard-cuts-player-visible-showhide)).

---

## `UiTransitionSession` generation cancels stale exit callbacks

**Shipped:** [game PR #240](https://github.com/miramocha/griddungeon-game/pull/240) · [ADR 039](../../decisions/039-uitk-dotween-show-hide.md)

`PopInTransition`, `SlideTransition`, `CollapseTransition`, and `CommandRailEnterTransition` call **`UiTransitionSession.Begin`** before starting DOTween motion. `Begin` **increments generation then kills** in-flight tweens on that target (or on a separate DOTween target for map marker fades). Exit `onComplete` handlers capture generation and return early when `!IsCurrent`.

A new `Show()` during exit therefore **should not** run the old exit `onComplete` — unless the host never called `Show` and only called `Refresh`.

Do not bypass with hand-rolled delays or USS `transition-duration`. New animated overlays: `CentralizedUiPresentation` + `IPresentationDriver` + `UiTransitionSession` — not ad-hoc `schedule.Execute`.

**Detach:** `UiTransitionSession` cleanup on `DetachFromPanelEvent` uses `KillWithoutCompleting` so DOTween does not fire callbacks while UITK is modifying hierarchy.

---

## Shared `CommandRail.PanelHost` — chrome leaks

**Symptom:** Hub service buttons look dim/disabled after combat; party rail chips stuck muted.

**Cause:** `command-panel--disabled` / `command-panel--modal-open` left on the **shared** rail host when combat or a modal ends without reset.

**Fix:** `CommandPanelModalSupport.ResetPanelChrome` on combat teardown, hub root repopulate, party section rail build. See [centralized UI services § Panel chrome reset](centralized-ui-services.md#global-command-rail--commandrailpresenter--commandpanelmodalsupport).

---

## Global input hints — publish / clear stack

**Symptom:** Wrong bind line after closing shop, party menu, or story modal; duplicate footers if someone adds a `Label` on the panel.

**Cause:** Overlays publish to `InputHints` while open; underlying phase hint not restored on dismiss, or two publishers active.

**Rules:**

- One strip (`InputHintPresenter`, sort **300**). Constants in `TabbedPickerRailHints`.
- Overlay **publish** on open, **clear** or **restore** phase hint on close (`HubHudView.RestoreInputHint`, `ExplorationMapCoordinator.RefreshGlobalInputHint`, …).
- Non-bind copy (tutorial, save warning) stays on modal body — not the global strip. See [global input hints rule](../../.cursor/rules/unity-global-input-hints.mdc).

---

## Standalone `UIDocument` — no geometry dock

**Symptom:** Bag panel drifts when resolution changes; picker clipped under wrong parent; double input hit targets.

**Cause:** `CloneTree` of service UXML into phase HUD, or `worldBound` / `GeometryChangedEvent` sync across two `UIDocument` roots.

**Rule:** Phase views call facades (`ItemListInventory.OpenBag`, `SetHubShopMode`, …). Modal position comes from **USS** (`tabbed-picker--rail-offset`, full-bleed overlay), not reparenting. Review smell table: [centralized-ui-services.mdc](../../.cursor/rules/centralized-ui-services.mdc).

---

## Pointer dead — `sortingOrder` stack + `PickingMode` pass-through

**Symptom:** Mouse **hover** and **LMB** do nothing on a `UIDocument` below another panel — **keyboard** navigation / confirm on the same control still works. Often one surface in the stack works (e.g. enemy roster in combat HUD) while a sibling document does not (e.g. ally slots on `PartyFormationFloater`).

**Cause (layered — check both):**

| Trap | What goes wrong |
|------|-----------------|
| **Higher `sortingOrder` wins picks first** | UITK routes pointer events to the **topmost** panel at that screen position. A full-screen phase HUD (`CombatHud` **20**) above the party floater (**10**) intercepts hits before the lower document is tested. |
| **Transparent chrome still picks** | Default `PickingMode.Position` on `position: absolute; left/right/top/bottom: 0` roots and flex **spacers** (`combat-hud__arena-spacer`) blocks clicks even when visually empty. Enemy slots inside the HUD still work; content on a **lower** document does not. |
| **Handler / coordinator red herring** | Keyboard uses `MenuFocusNavigator` / `TryConfirm()` — no hit-test. A broken `m_onPointerConfirm` looks like “click dead” but **hover also dead** usually means **picking**, not confirm wiring. |
| **Wrong document owns the grid** | Party combat roster is on **`PartyFormationFloater`**, not `CombatHud` UXML. Debugging only `CombatHudView` misses the floater document. |

**Reference stack (launch):** [centralized UI services § `sortingOrder` stack](centralized-ui-services.md#sortingorder-stack-at-launch) — e.g. floater **10**, `CombatHud` **20**, command rail **25**, skill/item pickers **200**.

**Fix (shipped — combat ally targeting, ADR 026 pointer parity):**

1. **Confirm stack** — list every `UIDocument` that overlaps the interactive region; note each presenter’s `sortingOrder` constant. If the interactive surface is **below** opaque or full-bleed chrome, either **raise** its sort while active (formation edit uses **260**) or pass picks through the blocker.
2. **Pass-through ambient chrome** — on full-screen / spacer nodes that should not steal input: `pickingMode = PickingMode.Ignore`. Re-enable `PickingMode.Position` only on **interactive** descendants (roster slots, log preview row, synchro bar when actionable).
3. **Lower document hygiene** — `PartyFormationFloaterPresenter` sets document root + floater shell + grid mount to `Ignore`; `PartyFormationGridView` sets `Position` per slot when targetable (`IsSlotClickable`).
4. **Do not “fix” with handler-only patches** when hover is also dead — fix hit-test first, then verify `PartyFormationGridPointerCoordinator` claim / confirm handlers.

```csharp
// ❌ BAD — full-screen combat HUD root blocks party floater (sort 10) underneath
// Default PickingMode.Position on combat-hud + arena-spacer

// ✅ GOOD — ambient chrome ignores picks; interactive children opt in
documentRoot.pickingMode = PickingMode.Ignore;
combatHud.pickingMode = PickingMode.Ignore;
arenaSpacer.pickingMode = PickingMode.Ignore;
logPreviewRow.pickingMode = PickingMode.Position;
// Enemy slots: CombatArenaPlateView.ApplySlotPickingMode when targetable
```

**Shipped in:** `CombatHudView.ConfigurePassThroughPicking`, `PartyFormationFloaterPresenter.ConfigurePassThroughPicking`.

**Tests:** `CombatTargetSelectionCoordinatorTests` (ally pointer confirm after planning handoff); manual F3 — medic heal → hover + LMB on ally; enemy mouse targeting regression.

**Rule for new cross-document pointer (ADR 026):** When adding hover = focus / LMB = confirm on a centralized surface, **double-check `sortingOrder`** against overlapping phase HUDs and set **pass-through picking** on non-interactive full-bleed nodes. If mouse is dead but keyboard works, suspect stack + `PickingMode` before coordinator handlers.

---

## `ItemListInventory` — one picker, three contexts

Only one context active at a time. Opening bag while shop modal logic still thinks it owns the picker causes focus/picking-mode bugs.

| Context | Sort | Typical owner |
|---------|------|----------------|
| `HubShop` | 200 | `HubHudView` |
| `CombatItem` | 200 | `CombatHudView` / `CommandPanelView` |
| `PartyBag` | 251 | `PartyMenuOverlayView` |
| `Hidden` | — | Phase exit, explicit hide |

`SyncPickingMode` enables host hits when combat item is open **or** picker is **`IsSettling`** (keeps hits coherent through exit). New contexts should follow the same immediate-hide-on-switch rule.

---

## Edit Mode tests without a panel

**Symptom:** Picker tests pass in isolation but Play Mode still breaks on rapid cancel.

**Cause (post-#240):** `ItemListPickerView` tests that clone UXML **without** a live `panel` take **`CentralizedUiPresentation.HideDetached`** — instant dismiss, no `IsSettling`, no exit tween. Exit-animation races **do not reproduce** unless the host is under a `UIDocument` with `PanelSettings` (see `ItemListInventoryPresenterTests.CreatePresenter`, `ItemListPickerViewTests.Hide_WithPanel_ThenSimulatedExit_CompletesHide`).

Direct `PopInTransition` / `UiTransitionSession` tests still use **`SimulateDueExitCompletionForTests`** on detached `VisualElement`s; generation guards apply even without a panel.

**Rule:** Any bug involving animated hide/show needs at least one test with a **real panel** or an explicit `IsSettling` regression test on the presenter path.

---

## Map marker fade vs step motion

**Symptom:** FOE marker invisible after patrol step, or fade interrupted when `MapGridMarkerAnimator.Kill` runs.

**Cause:** Opacity fade and step translate shared one DOTween target on the marker element.

**Fix (shipped #240):** `MapMarkerVisibility` registers opacity tweens on a **separate session target** (`Begin(marker, separateTweenTarget: true)`). Hide applies `map-view__marker--fade-hidden` **immediately**; opacity tween is visual polish only.

**Test:** `MapGridMarkerAnimatorTests.Kill_DoesNotCancelMarkerFadeInTween`, `MapFoeMarkersPresenterTests.PatrolIntoFog_HidesMarkerAndStopsTween`.

---

## Map chrome vs floor transition screen fade (`ExplorationMapCoordinator`)

**Symptom:** Exploration minimap **hard cuts** on stairs (or hub boot shows empty frame); slide retract never visible; map pops in only after screen is already clear.

**Cause (layered — fix all that apply):**

| Trap | What goes wrong |
|------|-----------------|
| **Dismiss `onComplete` order** | `ClearMotionStyles` / inline translate **before** steady retract class → USS steady state flashes one frame (snap). |
| **`SnapFadeOpaque` same frame as HUD suppress** | `AcquireHudSuppress` starts minimap dismiss then `SnapFadeOpaque` → full-screen black at sort **10000** hides the slide tween entirely. Looks like instant cut. |
| **Map reveal after screen clear** | `PresentationReleased` / minimap `Show` only after `FadeFromColor` finished → map appears in one frame when tween is broken or too late. |
| **`CentralizedUiPresentation.Hide` early return** | `!IsShown && !IsSettling` → animated dismiss skipped while panel still visible. Host must drive **visual** state (`map-minimap--retracted`), not presentation flags alone. |
| **Opacity fade on side panel** | Right-docked panel opacity fade does not read well; minimap uses **slide retract** (`SlideTransition`, `map-minimap--retracted`) — not `map-view--faded`. |
| **Expanded open during suppress** | Coordinator must `CloseExpandedImmediate()` when chrome should hide — expanded overlay at sort **100** can cover fade beats. |

**Fix (shipped — `ExplorationMapCoordinator`, `MinimapPanelPresenter`, `FloorTransitionPresenter`):**

1. **`ExplorationMapCoordinator.SyncMapChromeVisibility`** — `VisualPresentationSync` gates on `map-minimap--retracted` + `IsSettling`; hub / non-exploration: `HideImmediate()`. Also retract when **party/pause menu** is open (matches party floater collapse).
2. **M-toggle** — expanded `UniformScaleTransition` / `ScaleInPresentationDriver`; minimap `SlideTransition.Hide()` while expanded open (MSK-style).
3. **Stairs leave floor** — `AcquireHudSuppress()` then **`yield return FadeToColor()`** (not `SnapFadeOpaque`) so minimap retract and screen darken overlap. Skip duplicate intro `FadeToColor` in `RunFadeOnlyTransition` when routine already faded.
4. **Land reveal** — `ReleaseExplorationChromeForReveal()` (`m_transitionInProgress = false`, `ResetHudSuppress`, `PresentationReleased`) **before** `FadeFromColor()` in `RevealFloorArtStep` so minimap slide-in runs with screen fade-in.
5. **Steady hidden** — `map-minimap--retracted` on slide shell (translate off-screen).

**Authority:**

| Layer | Owns |
|-------|------|
| `map-minimap--retracted` | Steady hidden minimap pixels |
| `SlideTransition` + `UiToolkitTweens` | Minimap motion (`style.translate` during tween) |
| `map-expanded--hidden` / `map-expanded-scale--expanded` | Expanded overlay steady + scale end state |
| `UniformScaleTransition` | Expanded present/dismiss motion |
| `ExplorationPresentationGate.AcquireHudSuppress` | When map chrome **should** hide (stairs); coordinator subscribes + `FloorTransition.IsTransitioning` |
| `ScreenFadePresenter` | Full-screen black — must not **snap** opaque on the same frame as minimap dismiss if players should see slide |

**Tests:** `ExplorationMapCoordinatorTests`, `MinimapPanelPresenterTests`, `ExpandedMapOverlayPresenterTests`, `UiToolkitTweensTests` (`SlideTransition_*`, `UniformScaleTransition_*`).

**Prevent recurrence:** [UITK BEM transition guide](uitk-bem-transition-guide.md) — [`BemMotionCompletion`](uitk-bem-transition-guide.md#bemmotioncompletion), [`VisualPresentationSync`](uitk-bem-transition-guide.md#visualpresentationsync), [presenter sync recipe](uitk-bem-transition-guide.md#recipe-presenter-syncpresentation).

**Rule for new phase chrome:** If UITK chrome must animate **with** `ScreenFadePresenter`, coordinate timing in `FloorTransitionPresenter` (or phase owner) — do not rely on HUD suppress alone while screen snaps opaque.

---

## Party floater collapse — double slide-up (`CollapseTransition` / `PartyFormationFloater`)

**Symptom:** Bottom party strip **slides up twice** (or dips down then up) on exploration reveal, floor land, or HUD suppress release.

**Cause (layered):**

| Trap | What goes wrong |
|------|-----------------|
| **Two-leg `Present` tween** | Old sequence: inline translate **0 → dipY** (down) then **dipY → 0** (up) — reads as double vertical motion. |
| **Present `onComplete` order** | `ClearMotionStyles` before removing `--collapsed` → one-frame snap when USS steady state catches up (same class as map `FadeTransition`). |
| **`IsShown` without visual class** | `CentralizedUiPresentation.Show()` sets `IsShown = true` immediately; `SyncPresentation` skip logic missed re-entrant calls while the floater was still visually collapsed. |
| **Duplicate suppress release** | `OnHudSuppressedChanged(false)` called `ApplyPartyStripVisibility` then `RefreshExplorationChrome` (which called it again) in the same frame. |

**Fix (shipped — `CollapseTransition`, `PartyFormationFloaterPresenter`, `ExplorationHudView`):**

1. **`CollapseTransition.Present`** — single slide **dipY → 0**; `onComplete`: `SetCollapsed(false)` **then** `ClearMotionStyles`. Dismiss `onComplete`: collapsed class **then** clear inline.
2. **`SyncPresentation`** — gate on **`party-formation-floater--collapsed`** (visual), like minimap + `map-minimap--retracted`; skip hide when already collapsed and not settling.
3. **HUD suppress release** — `RefreshExplorationChrome` only (includes party strip visibility); no duplicate `ApplyPartyStripVisibility` before it.

**Tests:** `PartyFormationFloaterPresenterTests`, `UiToolkitTweensTests.CollapseTransition_Present_ClearsCollapsedClassAfterComplete`.

**Prevent recurrence:** [UITK BEM transition guide](uitk-bem-transition-guide.md) — [collapse steady class](uitk-bem-transition-guide.md#steady-class-registry), [presenter sync recipe](uitk-bem-transition-guide.md#recipe-presenter-syncpresentation).

---

## Hub hospital pick — floater dock vs party menu (`PartyFormationFloater` / `HubHudView`)

**Symptom:** Hospital **Heal member** opens rail pick mode but party strip never slides up (or shows party-menu bind state); leaving hub with pick active leaves `command-panel--modal-open` on the shared rail.

**Cause (layered):**

| Trap | What goes wrong |
|------|-----------------|
| **Context priority** | `PartyMenuDock` resolved before `HubHospitalDock` — Tab party menu floater owns the strip while hospital pick is active. |
| **System dismiss uses animated hide** | `CloseServicePanelImmediate` / phase exit called `ApplyHubHospitalFloaterDock(false)` — collapse exit can finish after reopen or after hub teardown (same class as **Context switches must not use animated hide**). |
| **Rail chrome leak** | `CommandPanelModalSupport.SetModalOpen(true)` during hospital pick; immediate service teardown did not clear modal class before root menu rebuild. |
| **Rapid X → Heal** | Stale collapse exit if reopen does not `CancelPendingDismiss` before `Show` (mirrors party-menu dock redock). |

**Fix (shipped — `PartyFormationFloaterPresenter`, `HubHudView`):**

1. **`HubHospitalDock` before `PartyMenuDock`** in `ResolveActiveContext` when `m_hubHospitalDocked` (formation-edit still wins).
2. **`DismissHubHospitalDockImmediate()`** — system/phase/service teardown; restores `m_requestedVisible` when party-menu dock survives.
3. **Player X / Back** — keep animated `ApplyHubHospitalFloaterDock(false)` within hospital service.
4. **`ResetHospitalPickState`** → `DismissHubHospitalDockImmediate()`; `CloseServicePanelImmediate` also `SetModalOpen(host, false)`.
5. **Enter pick** — `CancelPendingDismiss` at start of `ApplyHubHospitalFloaterDock(true)` (rapid redock).

**Tests:** `PartyFormationFloaterPresenterTests.ApplyHubHospitalFloaterDock_RapidExitAndRedock_CancelsPendingDismiss`, `DismissHubHospitalDockImmediate_ClearsSettlingState`, `HubHospitalServiceFocusTests`.

**Rule:** Hub hospital pick uses the **standalone** `PartyFormationFloater` facade (`ApplyHubHospitalFloaterDock` / slot handler) — not `CloneTree` on `HubHud`. Publish `TabbedPickerRailHints.HubHospitalPick` while pick active; **WASD** (Hub `MenuNavigate`) moves focus on the floater grid — not Q/E. Restore `HubService` on exit. Service rail chrome uses **`CommandPanelModalSupport.SyncModalChipRail`** (Heal chip selected + Revive disabled) — same recipe as hub shop Buy/Sell; see [shared menu § Modal rail sibling disable](shared-menu-picker-ui.md#modal-rail-sibling-disable-commandpanelmodalsupport).

---

## Hub service modal chip rail (`CommandPanelModalSupport.SyncModalChipRail`)

**Symptom:** Hub **Heal member** / **Buy** opens a child modal but both service chips stay enabled and neither shows `rail-menu__item--selected` — player cannot tell which action owns the floater/picker.

**Cause:** Re-implementing per-service `SetEnabledForModal` + `BindSelectionTargets` + `SetSelectedIndex` in the phase HUD instead of the shared helper. Shop and hospital had duplicate private methods that drifted.

**Fix (shipped — `CommandPanelModalSupport`, `HubHudView`):**

1. **`SyncModalChipRail`** — one call: bind selection targets, disable non-owner siblings while modal open, apply `rail-menu__item--selected` on owner (`CommandPanel.uss` keeps owner bright even when `:disabled`).
2. **`ApplyModalChipEnables`** — index-stable nullable chip list for party section rail (same enable rule, selection handled separately).
3. **Domain index helpers** — `HubShopServiceFocus`, `HubHospitalServiceFocus.ResolveSelectedRailIndex`; do not hardcode chip order in the HUD beyond action button indices.
4. **`RebuildServiceFocus`** — `SetModalOpen` → `Sync*ServiceModalChips` → **then** build `MenuFocusItem` rows from `button.enabledSelf` → `ClearFocusItems` when modal open.

**Trap:** Building `MenuFocusItem(button.enabledSelf, …)` **before** `SyncModalChipRail` leaves siblings permanently non-focusable in `MenuFocusNavigator` after modal dismiss (Revive skipped after Heal pick **X**). Chip sync must precede focus-item snapshot.

**Tests:** `CommandPanelModalSupportTests`, `HubHospitalServiceFocusTests`, `HubShopServiceFocusTests`.

**Rule:** Any new hub service action that opens a rail-offset modal or floater pick with **two+ sibling chips** must use `SyncModalChipRail` (or `ApplyModalChipEnables` when selection is owned elsewhere). Document the consumer row in [shared menu § Modal rail sibling disable](shared-menu-picker-ui.md#modal-rail-sibling-disable-commandpanelmodalsupport).

---

## Party section rail policy (`PartyMenuSectionPolicies`)

**Symptom:** New party-menu section (e.g. Use Skill) keeps sibling section chips enabled after **Z** reveal — player can Tab/Q/E to another section while a child modal is open.

**Cause:** Sibling disable is policy-driven (`PartyMenuSectionPolicies` → `PartyMenuSectionRailFocusRules.TryEvaluate`), not automatic per section. A missing policy row defaults to siblings staying enabled (same class of bug as Use Skill before `OnPaneRevealed` was registered).

**Fix:**

1. Add `PartyMenuSection` enum value + `PartyMenuSections.ForPhase` entry.
2. Register **`PartyMenuSectionModalPolicy`** in `PartyMenuSectionPolicies` (`PartyMenuSectionRailFocusRules.cs`) — match Equipment / Formation / Inventory patterns in [shared menu § Party section modal](shared-menu-picker-ui.md#modal-rail-sibling-disable-commandpanelmodalsupport).
3. Extend `PartyMenuSectionRailFocusRulesTests.EveryPartyMenuSection_HasRegisteredModalPolicy` — fails if policy missing.
4. Overlay builds one `PartyMenuSectionRailSnapshot` in `SyncSectionRailFocus`; `PartyMenuSectionRailCoordinator.Sync` applies both rails.

**Rule:** Do not add per-section bool parameters to the overlay — extend the policy map and snapshot fields only when a new signal is required.

---

## Slide retract dismiss order (`SlideTransition` / input hint / wallet)

**Symptom:** Input hint or wallet strip **double-slides** or **one-frame snap** on hide/show; re-publishing hint text retriggers slide while strip already expanded.

**Cause:**

| Trap | What goes wrong |
|------|-----------------|
| **Dismiss `onComplete` order** | `ClearMotionStyles` before `--retracted` → USS steady state flashes visible one frame. |
| **Present `onComplete` order** | Clear inline before confirming retracted class off → same snap on slide-in complete. |
| **`IsShown` without visual class** | `Show()` sets `IsShown` immediately; `SyncPresentation` skipped re-show while label still had `--retracted`, or called `Show` again while already expanded. |

**Fix (shipped — `SlideTransition`, `InputHintPresenter`, `WalletHudPresenter`):**

1. **`SlideTransition`** — dismiss: `SetRetracted(true)` then `ClearMotionStyles`; present complete: `SetRetracted(false)` then clear inline.
2. **`SyncPresentation`** — gate on **`--retracted`** / `wallet-hud__panel--retracted` (visual), like minimap + `PartyFormationFloater`; hide: `ShouldCallHide` → `Hide()` only — **no** instant teardown in an `else` branch (see **Wallet dual hide layer** below).
3. **`CommandRailEnterTransition.PlayClose`** — apply `hiddenClass` **before** `ClearMotionStyles` when panel close uses hidden BEM.

**Tests:** `UiToolkitTweensTests` slide present/dismiss class tests, `InputHintPresenterTests`, `WalletHudPresenterTests`.

**Prevent recurrence:** [UITK BEM transition guide](uitk-bem-transition-guide.md) — API + [transition recipe](uitk-bem-transition-guide.md#recipe-new-transition-helper) + [presenter sync recipe](uitk-bem-transition-guide.md#recipe-presenter-syncpresentation) + [no hard cuts](uitk-bem-transition-guide.md#no-hard-cuts-player-visible-showhide). ADR checklist: [039 §6](../../decisions/039-uitk-dotween-show-hide.md#6-shared-completion--presenter-sync-mandatory-for-new-bem-motion); agent rule: `uitk-bem-transition.mdc`.

---

## Input hint hard cut — hub → stratum (`InputHintPresenter` + `FloorTransitionPresenter`)

**Symptom:** Global bind strip **snaps off** when leaving hub for stairs / **Depart** — no slide retract; strip may linger through first half of hub leave fade then vanish instantly.

**Cause:**

| Trap | What goes wrong |
|------|-----------------|
| **Hint outlives hub chrome** | Hub leave hides `hub-hud__chrome` via USS; `InputHintPresenter` is a separate `UIDocument` (sort 300) — still visible until phase flip. |
| **`HideImmediate` mid-beat** | `FloorTransitionPresenter` called `InputHint.HideImmediate()` at transition start → kills slide tween if hub already called `Clear`, or snaps without motion if strip still extended. |
| **Late clear** | Waiting until `SetHubVisible(false)` / phase change to clear hint — desync from leave fade start. |

**Fix (shipped):**

1. **`HubHudView.OnDepartClicked`** — `InputHints.Clear` when leave transition **starts** (slide retract with fade).
2. **`FloorTransitionPresenter`** — `InputHint.Hide()` not `HideImmediate()` (animated dismiss; no-op if already clearing).
3. **`ExplorationMapCoordinator.OnFloorTransitionPresentationReleased`** — republish exploration copy (`MinimapPanelPresenter.Show()` slide in).

**Rule:** Floor-transition and other Runtime beat code must not `HideImmediate()` player-visible centralized chrome. Coordinate with phase owners per [no hard cuts](uitk-bem-transition-guide.md#no-hard-cuts-player-visible-showhide).

**Tests:** `InputHintPresenterTests` (settle, rapid swap during hide); manual F1 → **Depart**.

---

## Wallet / slide strip — dual hide layer hard cut (`WalletHudPresenter`)

**Symptom:** Credits wallet **snaps off** (hard cut) on shop close, party bag → Formation tab, or transient pulse end — while party floater / other chrome still animates out smoothly.

**Cause (layered — same class of bug as map `display:none` + fade, but on slide retract):**

| Trap | What goes wrong |
|------|-----------------|
| **Two visibility authorities** | Parent `wallet-hud--hidden` (`display: none`) **and** child `wallet-hud__panel--retracted` (translate + opacity). Slide tweens the panel; `PrepareHiddenVisual` / `SetRootVisible(false)` nukes the root **instantly** — player sees cut, not retract. |
| **`SyncPresentation` else on hide** | When `!RequestedVisible` and `!ShouldCallHide` (steady retracted, not settling), an `else { PrepareHiddenVisual() }` applies `display: none` without running `SlideTransition.Dismiss`. |
| **`CancelPendingDismiss` on deactivate** | `SetReason(..., false)` while dismiss is settling called `HideImmediate` → **snap**. Party floater only cancels on **activate** / redock (`ApplyHubHospitalFloaterDock(true)`), not every reason clear. |
| **`CentralizedUiPresentation.Hide` early return** | `!IsShown && !IsSettling` skips driver dismiss while panel still extended — or pairs with forced teardown for a snap. `TryDismissVisuallyExtended` on slide driver runs dismiss from steady class. |
| **Zero-length slide sample** | `translate: 0 -100%` with `layout.height == 0` → sampled end offset **0** → tween noop → retract class on complete = instant. Use `CreateSlide(..., fallbackRetractOffsetSign)` (-1 wallet up, +1 input hint down), same idea as `CollapseTransition.SampleCollapsedOffsetY`. |
| **Show path un-hides root before slide** | `SetRootVisible(true)` before `ShouldCallShow` / `Show()` — root visible while presentation `IsShown` can lag; clearing reasons then hits early-return hide + callback hard cut. |

**Reference (good):** `PartyFormationFloaterPresenter` — **one** steady class on the animation target (`party-formation-floater--collapsed`), `SyncPresentation` hide calls `Hide()` only when gated, **no** second `display: none` parent, `CancelPendingDismiss` only when **activating** / redocking.

**Fix (shipped — `WalletHudPresenter`, `WalletHudView`, `WalletHud.uxml` / `.uss`, `SlideTransition`, `CentralizedUiPresentation`):**

1. **Remove** `wallet-hud--hidden` — panel `wallet-hud__panel--retracted` + `SlideTransition` is the only show/hide authority.
2. **`SyncPresentation`** — mirror floater: hide → `ShouldCallHide` → `m_presentation.Hide()` (no callback, no `else` teardown); show → `IsSteadyVisible` early-out, then `ShouldCallShow` → `Show()`.
3. **`CancelPendingDismiss`** — call on `SetReason(..., true)` and `StartTransient` only; **not** on `SetReason(..., false)` while dismiss is settling.
4. **`CreateSlide(..., fallbackRetractOffsetSign: -1)`** for wallet — non-zero retract distance when `%` layout sample fails.
5. **Override `IsShown`** from `!IsPanelRetracted` (like `MinimapPanelPresenter` + retracted class).
6. **`CentralizedUiPresentation.TryDismissVisuallyExtended`** — slide dismiss when target is extended but lifecycle missed `Show()`.
7. **Cold start / phase teardown** — `m_presentation.HideImmediate()` only; reserve `HideImmediate` for `OnDisable` and system dismiss, not player context close within the same phase.
8. **Balance lerp** (`SyncBalance` / transient pulse) stays separate from chrome slide — do not conflate number snap on shop open with visibility hard cut.

**Tests:** `WalletHudPresenterTests` — `Hide_EntersSettleWindowBeforeShownClears`, `SetReason_RapidSwapDuringHideSettle_CancelsDismissAndShowsAgain`, `SetReason_DeactivateAgainDuringHideSettle_DoesNotSnapRetract`, `ClearAllReasons_WhenAlreadyRetracted_DoesNotRecallHide`.

**Rule for new slide strips:** Do **not** stack `display: none` (or `visibility: hidden`) on a parent **and** retract/fade on a child unless the parent toggle is **only** used after the child dismiss tween completes — and never in a `SyncPresentation` `else` branch. Prefer **`PartyFormationFloaterPresenter` / `InputHintPresenter`** sync shape: one animation target, `VisualPresentationSync`, optional `CancelPendingDismiss`. `InputHint` may still use a dismiss callback to clear label text — it does **not** add a root `display: none` layer.

**Cross-ref:** [Slide retract dismiss order](#slide-retract-dismiss-order-slidetransition--input-hint--wallet), [Party floater collapse](#party-floater-collapse--double-slide-up-collapsetransition--partyformationfloater), [Map chrome vs floor transition](#map-chrome-vs-floor-transition-screen-fade-explorationmapcoordinator) (`CentralizedUiPresentation.Hide` early return).

---

## Party menu 3D — silhouette reveal stuck black (`CharacterMaterialSilhouette`)

**Symptom:** Focused party member stays **black silhouette** after floater dock + grid focus; orbit camera and `SetMemberRevealGridIndex` fire, but no color reveal. Console may spam **`Game object with animator is inactive`** and **`Animator is not playing an AnimatorController`** during `OnMenuOpened` → `SyncRoster`.

**Authority:** [ADR 047](../../decisions/047-party-menu-3d-stage.md) · [custom party UI § Party menu 3D stage](custom-party-ui.md#party-menu-3d-stage).

**Cause (layered):**

| Trap | What goes wrong |
|------|-----------------|
| **Pose on inactive instance** | `ApplyPoseForGridIndex` ran while the VRM root was still `SetActive(false)` in stash spawn — `Animator.Play` / `GetLayerIndex` for `Silhouette` / `Breathing` layers fail silently or log errors; controller state never binds. |
| **Cached `Material` refs ≠ live renderer** | `CharacterMaterialSilhouette` stored `Material` instances in snapshots and lerped `_Color` on those objects; VRM / play-mode `renderer.materials` later pointed at **different** instances — tween reached `revealAmount: 1` on orphaned materials. |
| **Re-cache after silhouette pass** | Re-running `EnsureCache()` after `SetRevealed(false)` re-read **blackened** shared/instance materials as “original” colors — reveal lerps black → black forever. |
| **MToon10 property shape** | `VRM10/…/MToon10` often has `_Color` = white multiplier `(1,1,1)`; skin tint lives in **`_BaseColorFactor`** / **`_Base_Color_Opacity`**. Capturing or writing only `_Color` after a blacken pass loses the real reveal target. |

**Fix (shipped — `PartyCharacterVisualRegistry`, `PartyCharacterVisualPose`, `CharacterMaterialSilhouette`):**

1. **`PresentSlotOnStage`** — `PartyCharacterVisualStagePlacement.Present` (activate) **before** `ApplyPoseForGridIndex`; `PartyCharacterVisualPose.Apply` no-ops when `!animator.gameObject.activeInHierarchy`.
2. **Live material writes** — snapshots store **renderer + material index + pristine color values**; `ApplyRevealAmount` batches `renderer.materials` per renderer and writes the same property IDs that were cached (e.g. `_BaseColorFactor` when `_Color` is neutral white).
3. **Pristine lock** — first successful `EnsureCache` captures colors from **shared** materials (before silhouette blacken); values stay locked — do **not** rebuild cache after `SetRevealed(false)`; attach meshes before the first cache pass.
4. **MToon10** — when `_Color` is neutral white, cache and apply via **`_BaseColorFactor`** / **`_ShadeColorFactor`**.
5. **`RefreshSilhouetteAfterActivation`** — re-apply current `RevealAmount` to live materials only; no cache rebuild on stage present.

**Tests:** `CharacterMaterialSilhouetteTests` (late renderer attach + restore), `PartyCharacterVisualRegistryTests` (silhouette focus grid index).

**Rule for party-menu VRM work:**

```csharp
// ❌ BAD — pose / silhouette while stash instance is inactive
instance.SetActive(false);
ApplyPoseForGridIndex(instance, gridIndex);
silhouette.SetRevealed(false);

// ❌ BAD — rebuild material cache after blackening
silhouette.EnsureCache(); // re-captures black as "original" once pristine lock is set

// ✅ GOOD — activate, cache pristine once, apply to live materials
Present(slot); // SetActive(true)
ApplyPoseForGridIndex(slot.Root, gridIndex);
silhouette.SetRevealAmount(revealAmount, immediate: true);
```

**Cross-ref:** [ADR 047 § Material silhouette](../../decisions/047-party-menu-3d-stage.md#material-silhouette--focused-member-reveal), [custom party UI § Party menu 3D stage](custom-party-ui.md#party-menu-3d-stage).

---

## Documentation map

| Topic | Doc |
|-------|-----|
| Service pattern, sort stack, bootstrap | [centralized-ui-services.md](centralized-ui-services.md) |
| Presentation lifecycle (shipped API, migration index) | [centralized-ui-services.md § Presentation lifecycle](centralized-ui-services.md#presentation-lifecycle) |
| BEM transition helpers (API, recipes, registry) | [uitk-bem-transition-guide.md](uitk-bem-transition-guide.md) |
| Lifecycle epic (pull order) | [game#206](https://github.com/miramocha/griddungeon-game/issues/206) |
| ADR (team-locked API) | [ADR 038](../../decisions/038-centralized-ui-presentation-lifecycle.md), [ADR 039](../../decisions/039-uitk-dotween-show-hide.md) |
| Picker layout, rail focus, cancel layering | [shared-menu-picker-ui.md](shared-menu-picker-ui.md) |
| Presentation bus / UITK shell traps | [presentation-shell-gotchas.md](presentation-shell-gotchas.md) |
| Agent review smells (embed/dock) | [centralized-ui-services.mdc](../../.cursor/rules/centralized-ui-services.mdc) |
| Floor transition + map panel fade timing | [authoring-floor-transition-beats.md § Screen fade](authoring-floor-transition-beats.md#screen-fade-uitk) |
| **Gotchas (this page)** | **Here** |
| Pointer / `sortingOrder` / `PickingMode` pass-through | [§ Pointer dead](#pointer-dead--sortingorder-stack--pickingmode-pass-through) |
| Party menu 3D silhouette reveal (VRM / MToon10) | [§ Party menu 3D — silhouette reveal](#party-menu-3d--silhouette-reveal-stuck-black-charactermaterialsilhouette) |
