---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/exploration
---
# ADR 018 — Exploration Animation Speed

**Status:** Accepted (amended 2026-05-26)  
**Date:** 2026-05-21  
**Aligns with:** [ADR 001 — Grid movement](001-grid-movement.md) (movement rules unchanged); [floor art FPV](../docs/02-systems/floor-art-fpv.md) (`WorldUnitsPerCell` = 10)

## Context

Exploration uses discrete grid steps with DOTween lerps ([ADR 001](001-grid-movement.md)). The original ~0.2s step default runs fast for EO-style pacing. Players should be able to choose a comfortable animation speed without changing FOE patrol, encounters, or grid logic (still committed at step/turn start).

## Decision

1. **Presets (player-facing):** `Slow`, `Normal`, `Fast`, `VeryFast` — display as Slow / Normal / Fast / Very Fast.
2. **Default:** `Normal` — project baseline for new games and docs.
3. **What scales:** Visual lerp durations only — **step move**, **turn rotate**, and **bump nudge** (both segments). Does **not** change when grid logic commits, FOE step patrol, or random encounter rolls.
4. **Hold-to-repeat:** Unchanged ([ADR 001](001-grid-movement.md)); a faster preset shortens time between repeated steps while holding a key, not game-time step rules.
5. **Persistence:** `PlayerPrefs` (or future settings save) when the settings UI ships; until then, runtime uses **Normal**.
6. **UI (future):** Pause → Settings → Gameplay or Accessibility dropdown; not required at launch code. Exploration pause: **Resume** / **Quit to title** only — no hub return ([ADR 014](014-mvp1-exploration-map.md) §7).

### Locked durations

| Preset | Step lerp | Turn lerp | Bump segment (each) | Notes |
|--------|-----------|-----------|---------------------|--------|
| **Slow** | 0.46 s | 0.36 s | 0.14 s | Deliberate exploration |
| **Normal** | **0.32 s** | 0.26 s | 0.10 s | **Default** (amended for 10 u/cell FPV — was 0.28 s at 1 u/cell) |
| **Fast** | 0.23 s | 0.18 s | 0.08 s | Snappier |
| **VeryFast** | 0.14 s | 0.11 s | 0.05 s | Near-instant; still discrete steps |

Bump animation total = 2 × bump segment. Turn lerp ≈ 81% of Normal step lerp (rotation pace unchanged from pre-FPV scale).

### Locked easing (DOTween)

| Motion | Ease | Notes |
|--------|------|--------|
| **Step** | `OutQuad` | Slight ease-out over **10** world units/cell |
| **Turn** | `OutQuad` | Unchanged |
| **Bump out / in** | `OutQuad` / `InQuad` | Unchanged |

**Amendment (2026-05-26):** at launch exploration world scale is **10 Unity units per logic cell** (`ExplorationGridMetrics.WorldUnitsPerCell`). Normal **step** duration increases **0.28 s → 0.32 s** so perceived walk pace stays similar; step tween uses **OutQuad** instead of linear. Other presets’ step durations scale by the same ratio (~8/7); turn/bump timings unchanged until `ExplorationAnimationDurations` ships in Core.

## Rejected

| Option | Why |
|--------|-----|
| Continuous speed slider | Four presets bound tuning and QA |
| Speed affects FOE patrol or encounter timing | Breaks step-based design ([ADR 003](003-foe-step-patrol.md)) |
| Separate gamepad presets | One setting; PC first ([ADR 008](008-campaign-defaults.md)) |

## Consequences

- **Core:** `ExplorationAnimationSpeed` enum + `ExplorationAnimationDurations.Get(speed)` (pure C#, unit-testable).
- **Runtime:** `DungeonExplorer` reads preset durations on enable and when the setting changes; mid-lerp: finish current tween, apply new durations on the next action.
- **UI:** Settings dropdown writes prefs (later).

## Related

- [ADR 001 — Grid movement](001-grid-movement.md)
- [02 — Dungeon navigation](../docs/02-dungeon-navigation.md)
- [Input bindings](../docs/02-systems/input-bindings.md)
- [05 — class design](../docs/05-class-design.md#exploration)
