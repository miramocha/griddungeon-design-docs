# ADR 038 — Centralized UI presentation lifecycle

**Status:** Accepted  
**Date:** 2026-06-11  
**Epic:** [game #206 — unified modal show/hide lifecycle](https://github.com/miramocha/griddungeon-game/issues/206)  
**Contract:** [game #207](https://github.com/miramocha/griddungeon-game/issues/207) (`ICentralizedUiSurface`, `CentralizedUiPresentation`)  
**Docs:** [centralized-ui-services § Presentation lifecycle](../docs/04-dev/centralized-ui-services.md#presentation-lifecycle), [centralized-ui-gotchas](../docs/04-dev/centralized-ui-gotchas.md)

## Context

Grid Dungeon hosts cross-phase UITK overlays as **one `UIDocument` per concern** under `GameState` ([ADR 012](012-unity-6-stack.md) UI Toolkit default). Before #207, each presenter invented its own visibility flags (`IsActive`, `IsClosing`, deferred `schedule.Execute`), which raced on rapid cancel/reopen and context swaps — especially `ItemListInventory` and `CharacterDetail` at party-menu sort **251**.

## Decision

### 1. Public vocabulary is transition-agnostic

Every centralized service presenter (except documented exceptions) implements **`ICentralizedUiSurface`**:

| Member | Meaning |
|--------|---------|
| `RequestedVisible` | Authority wants the panel open |
| `IsShown` | Panel presented for current authority (true through exit settle until animation completes) |
| `IsSettling` | Animated dismiss in flight after `Hide()` |
| `Show()` | Request on-screen presentation |
| `Hide()` | Same-authority dismiss (may settle) |
| `HideImmediate()` | Authority change — cancel deferred callbacks |

Facades mirror the three flags when a static facade exists. **Do not** expose `PopIn`, `IsClosing`, slide USS classes, or animation durations on public surfaces.

### 2. Visual drivers stay internal

Presenters compose **`CentralizedUiPresentation`** + **`IPresentationDriver`** (`PopIn`, slide, collapse, rail enter). Driver choice is an implementation detail per service — not a second public API. Motion is implemented with **DOTween** via `UiToolkitTweens` + `UiTransitionSession` ([ADR 039](039-uitk-dotween-show-hide.md)) — not USS `transition-property` or `schedule.Execute` on those overlays.

### 3. Hide semantics

| Situation | Call |
|-----------|------|
| Player dismiss, same context | `Hide()` |
| Phase exit, context enum swap, competing overlay | `HideImmediate()` |
| Data refresh while settling | `Show()` path — not refresh-only while `IsSettling` |

### 4. Exceptions

| Service | Why |
|---------|-----|
| `ScreenFadePresenter` | Beat-driven imperative fade on `GameState.ScreenFade` |
| Phase HUDs | Not centralized services |

`PartyMenuOverlayView` orchestrates service facades; it does not replace per-service lifecycle.

## Consequences

- New centralized services: reject PRs missing `ICentralizedUiSurface` ([centralized-ui-services.mdc](../.cursor/rules/centralized-ui-services.mdc)).
- **Reference consumer:** `ItemListInventory` / `ItemListPickerView`. **Second consumer:** `CharacterDetail` ([#209](https://github.com/miramocha/griddungeon-game/issues/209)).
- Gotchas and regression tests use **`IsSettling`**, not `IsClosing`.

## Related

- [game #206](https://github.com/miramocha/griddungeon-game/issues/206) — migration tracker  
- [ADR 039](039-uitk-dotween-show-hide.md) — internal animation stack (DOTween)  
- [game PR #240](https://github.com/miramocha/griddungeon-game/pull/240) — shipped DOTween migration  
- [design-docs #29](https://github.com/miramocha/griddungeon-design-docs/issues/29) — vocabulary + gotchas sync
