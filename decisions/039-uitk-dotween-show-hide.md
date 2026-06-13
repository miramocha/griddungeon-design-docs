# ADR 039 — UITK show/hide motion via DOTween

**Status:** Accepted  
**Date:** 2026-06-12  
**Implementation:** [game PR #240](https://github.com/miramocha/griddungeon-game/pull/240)  
**Builds on:** [ADR 038](038-centralized-ui-presentation-lifecycle.md) (`ICentralizedUiSurface`, `IPresentationDriver`)  
**Docs:** [centralized-ui-services § Animation stack](../docs/04-dev/centralized-ui-services.md#animation-stack-dotween), [unity-ui-toolkit.mdc](../.cursor/rules/unity-ui-toolkit.mdc)

## Context

Centralized UITK overlays (PopIn pickers, party floater collapse, wallet/input-hint slide, command-rail enter, map panel layout settle) originally used **USS `transition-property`** and **`schedule.Execute`** delays. That was brittle in Edit Mode tests, fought inline layout tweens (map markers, geometry-driven coordinates), and duplicated duration sources across USS and C#.

[game #206](https://github.com/miramocha/griddungeon-game/issues/206) locked **public** lifecycle vocabulary on `ICentralizedUiSurface`; animation mechanics remain **internal** to `GridDungeon.Runtime.UI`.

## Decision

### 1. Orchestrated show/hide uses DOTween — not USS transitions

| Layer | Owns |
|-------|------|
| **USS + BEM modifiers** | Steady-state pixels (`--hidden`, `--collapsed`, `--entering`, `--retracted`, `--expanded`) and hover/focus micro-states |
| **`UiToolkitTweens`** | DOTween on `VisualElement.style` (opacity, translate, scale, width/height) during motion |
| **`UiTransitionSession`** | Per-element **generation**; bump before kill so superseded exit callbacks bail via `IsCurrent` |
| **Transition helpers** | `PopInTransition`, `SlideTransition`, `CollapseTransition`, `FadeTransition`, `CommandRailEnterTransition`, `RailInfoCopyTransition`, `MapViewPanelTransition` |

**Do not** add `transition-duration` on blocks that C# animates. **Do not** use `schedule.Execute` for dismiss timing on centralized overlays.

Durations live in **C# constants only** (e.g. `PopInTransition.DurationMs` = 420).

### 2. Session rules

- **`Begin(target)`** — increment generation, then kill in-flight tweens on that session.
- **`Cancel(target)`** — same generation bump + kill (used by `HideImmediate` / `Reset` paths).
- **Detach cleanup** — `KillWithoutCompleting` only (no `onComplete` while UITK processes `DetachFromPanelEvent`).
- **Map marker fades** — `Begin(marker, separateTweenTarget: true)` so `MapGridMarkerAnimator.Kill` on the element does not cancel opacity tweens registered on a dedicated DOTween target.

### 3. BEM authority during motion

| Transition | Class authority |
|------------|-----------------|
| Pop-in exit | `--hidden` applied in `CentralizedUiPresentation.FinishDismissVisual` after driver `onComplete` |
| Collapse reveal | `--collapsed` **true** at dip start; **false** after bounce-in completes |
| Collapse dismiss | `--collapsed` **true** at slide-off start (before tween ends) |
| Command rail enter | `--entering` on body at open start; removed when enter tween completes (or immediately when `startingInMs == 0`) |
| Map marker hide | `map-view__marker--fade-hidden` applied **immediately**; opacity tweens for polish |
| Map panel fade dismiss | `map-view--faded` applied **after** opacity tween completes; **then** clear inline opacity — never clear inline before steady hidden class |
| Map panel fade present | Remove `map-view--faded`, tween inline opacity up, clear inline on complete |
| Party floater collapse present | Keep `--collapsed` during tween; single translate **dipY → 0**; remove collapsed **then** clear inline on complete |
| Party floater collapse dismiss | Set `--collapsed` **then** clear inline translate on complete |
| Slide retract dismiss | Retracted BEM **then** clear inline translate/opacity on complete |
| Slide retract present | Clear retracted BEM **then** clear inline on complete |
| Command rail panel close | `hiddenClass` **then** clear inline motion on complete |
| Rail info copy swap dismiss | `rail-info__*--faded` **true** after opacity tween completes |
| Rail info copy swap present | Remove `rail-info__*--faded`, tween inline opacity/translate, clear inline on complete |

Inline `style` drives motion; **`StyleKeyword.Null`** clears inline motion on complete.

### 4. Detached overlays (no `panel`)

`CentralizedUiPresentation.Hide` calls **`HideDetached`** when `ResolveTarget()?.panel == null` — instant dismiss + hidden class (Edit Mode picker tests without `UIDocument`). **Play Mode** hosts under `PanelSettings` still run animated `Hide()`.

Direct `PopInTransition` tests use **`SimulateDueExitCompletionForTests`** + generation guards; do not assume `panel == null` implies synchronous `PlayExit`.

### 5. Edit Mode test helpers

- `UiTransitionSession.CompleteImmediatelyForTests(target)`
- `PopInTransition.SimulateDueEnterCompletionForTests` / `SimulateDueExitCompletionForTests`
- `CollapseTransition.SimulateDueScheduleCompletionForTests`
- `SlideTransition.SimulateDueScheduleCompletionForTests`
- `FadeTransition.SimulateDueScheduleCompletionForTests`

### 6. Shared completion + presenter sync (mandatory for new BEM motion)

**Implementation guide:** [uitk-bem-transition-guide.md](../docs/04-dev/uitk-bem-transition-guide.md) — API reference, truth tables, transition/presenter recipes, steady-class registry, testing checklist.

| Helper | Path | Use |
|--------|------|-----|
| **`BemMotionCompletion`** | `Assets/Scripts/Runtime/UI/BemMotionCompletion.cs` | **All** transition `onComplete` / `Reset` paths that apply a steady BEM modifier — `ApplySteadyClassThenClearMotion(target, class, active)` |
| **`VisualPresentationSync`** | `Assets/Scripts/Runtime/UI/VisualPresentationSync.cs` | Presenter `SyncPresentation` / chrome visibility — `ShouldCallShow` / `ShouldCallHide` / `IsSteadyVisible` on **steady hidden class + `IsSettling`**, not `IsShown` alone |

**New transition helper checklist:**

- [ ] Steady modifier documented in §3 table above
- [ ] Present / dismiss / reset complete via `BemMotionCompletion` (or collapse `ApplyCollapsedSteady` when `pickingMode` must flip)
- [ ] Presenter sync via `VisualPresentationSync` or derive `IsShown` from steady class (`MapView`, `CommandRailInfoPresenter`)
- [ ] Edit Mode: `{Transition}_Present_*` + `{Transition}_Dismiss_*` class tests in `UiToolkitTweensTests`
- [ ] Presenter: rapid reopen during `IsSettling` test
- [ ] Phase owner: single visibility path; no duplicate apply same frame (see gotchas)

**Exceptions:** PopIn (host `--hidden` + scale; reopen = `Show` not `Refresh`). `MapViewPanelTransition` (layout tween). `ScreenFadePresenter` (imperative).

Rule: `.cursor/rules/uitk-bem-transition.mdc`

## Consequences

- New animated overlay: reuse `CentralizedUiPresentation` + `IPresentationDriver` + `UiTransitionSession`; do not fork USS transition timing.
- `UiToolkitTweens` lives under `Assets/Scripts/Runtime/UI/` (not `GridDungeon.UI`).
- Hover/focus USS transitions remain OK; orchestrated show/hide does not.
- Regression tests for exit races need a **panel-attached** presenter path or explicit `IsSettling` coverage — see [centralized-ui-gotchas § Edit Mode tests](../docs/04-dev/centralized-ui-gotchas.md#edit-mode-tests-without-a-panel).
- Map panel fade must be timed with `ScreenFadePresenter` on floor transitions — see [centralized-ui-gotchas § Map panel fade vs floor transition](../docs/04-dev/centralized-ui-gotchas.md#map-panel-fade-vs-floor-transition-screen-fade-mapview--fadetransition).

## Related

- [game #206](https://github.com/miramocha/griddungeon-game/issues/206) — lifecycle epic  
- [ADR 038](038-centralized-ui-presentation-lifecycle.md) — public API  
- [ADR 018](018-exploration-animation-speed.md) — exploration step timing (separate from UITK overlay durations)
