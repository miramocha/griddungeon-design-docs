# ADR 018 — Exploration Animation Speed

**Status:** Accepted  
**Date:** 2026-05-21  
**Aligns with:** [ADR 001 — Grid movement](001-grid-movement.md) (movement rules unchanged)

## Context

Exploration uses discrete grid steps with DOTween lerps ([ADR 001](001-grid-movement.md)). The original ~0.2s step default feels slightly fast for EO-style pacing. Players should be able to choose a comfortable animation speed without changing FOE patrol, encounters, or grid logic (still committed at step/turn start).

## Decision

1. **Presets (player-facing):** `Slow`, `Normal`, `Fast`, `VeryFast` — display as Slow / Normal / Fast / Very Fast.
2. **Default:** `Normal` — project baseline for new games and docs.
3. **What scales:** Visual lerp durations only — **step move**, **turn rotate**, and **bump nudge** (both segments). Does **not** change when grid logic commits, FOE step patrol, or random encounter rolls.
4. **Hold-to-repeat:** Unchanged ([ADR 001](001-grid-movement.md)); a faster preset shortens time between repeated steps while holding a key, not game-time step rules.
5. **Persistence:** `PlayerPrefs` (or future settings save) when the settings UI ships; until then, runtime uses **Normal**.
6. **UI (future):** Pause → Settings → Gameplay or Accessibility dropdown; not required for MVP1 code. Exploration pause: **Resume** / **Quit to title** only — no hub return ([ADR 014](014-mvp1-exploration-map.md) §7).

### Locked durations

| Preset | Step lerp | Turn lerp | Bump segment (each) | Notes |
|--------|-----------|-----------|---------------------|--------|
| **Slow** | 0.40 s | 0.36 s | 0.14 s | Deliberate exploration |
| **Normal** | 0.28 s | 0.26 s | 0.10 s | **Default** |
| **Fast** | 0.20 s | 0.18 s | 0.08 s | Snappier; prior Normal step target |
| **VeryFast** | 0.12 s | 0.11 s | 0.05 s | Near-instant; still discrete steps |

Bump animation total = 2 × bump segment. Turn lerp ≈ 93% of step lerp across presets (matched rotation pace to step feel).

## Rejected

| Option | Why |
|--------|-----|
| Continuous speed slider | Four presets bound tuning and QA |
| Speed affects FOE patrol or encounter timing | Breaks step-based design ([ADR 003](003-foe-step-patrol.md)) |
| Separate gamepad presets | One setting; PC first ([ADR 008](008-campaign-defaults.md)) |

## Consequences

- **Core:** `ExplorationAnimationSpeed` enum + `ExplorationAnimationDurations.Get(speed)` (pure C#, unit-testable).
- **Runtime:** `DungeonExplorer` reads preset durations on enable and when the setting changes; mid-lerp: finish current tween, apply new durations on the next action.
- **UI:** Settings dropdown writes prefs (post-MVP1).

## Related

- [ADR 001 — Grid movement](001-grid-movement.md)
- [02 — Dungeon navigation](../docs/02-dungeon-navigation.md)
- [Input bindings](../docs/02-systems/input-bindings.md)
- [05 — Class design MVP1](../docs/05-class-design-mvp1.md#exploration)
