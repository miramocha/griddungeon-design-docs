# ADR 001 — Grid Movement Feel

**Status:** Accepted  
**Date:** 2026-05-20  
**Aligns with:** *Etrian Odyssey*

## Context

EO uses discrete grid steps with light animation. Movement must stay compatible with **per-step random encounters**, **FOE patrol ticks**, and **auto-floor mapping**.

## Decision

1. **Displacement** — forward, backward, **strafe left**, **strafe right**: one cell, ~0.28s step lerp at **Normal** speed ([ADR 018](018-exploration-animation-speed.md)); logic at step start; **facing unchanged**.
2. **Turn in place** — 90° lerp (~0.26s at Normal); facing commits at turn start; **no step events** (no encounter, no FOE tick). **Hold-to-repeat:** same as displacement — when a turn lerp completes, if the same turn action is still held, rotate 90° again.
3. **During animation** — block new displacement commits, overlapping step lerps, and overlapping turn lerps. **Hold-to-repeat** for movement and turn: when the current lerp completes, if the same action is still held (`IsPressed`), start the next action of that type. **No tap buffer** during lerp (input during animation only counts if the key is still held at lerp end). If both movement and turn are held at lerp end, **displacement takes priority**. Bump tweens use the same rule as step lerps.
4. Each completed **displacement** step triggers **FOE patrol** resolution ([ADR 003](003-foe-step-patrol.md)).

## Amendments (2026-05-21)

- Supersedes the prior rule “queue one buffered step max” during lerp. EO-style exploration uses **hold-to-repeat** after each step and turn animation instead of edge-buffered taps mid-lerp.
- Default lerp timings moved from ~0.2s / ~0.15s step/turn to **Normal** preset in [ADR 018](018-exploration-animation-speed.md) (0.28s step / 0.26s turn). Player-selectable Slow / Fast / Very Fast presets added there.

## Alternatives considered

| Option | Rejected because |
|--------|------------------|
| Encounters on turn | Not EO-like; punishes map orientation |
| Free movement | Breaks FOE/grid design |

## Consequences

- `OnPartyEnteredCell` drives map auto-floor + encounter roll
- FOE system listens to step events for patrol advancement

## Related

- [02 — Dungeon navigation](../docs/02-dungeon-navigation.md)
- [ADR 003 — FOE step patrol](003-foe-step-patrol.md)
- [ADR 018 — Exploration animation speed](018-exploration-animation-speed.md)
- [ADR 021 — Autopilot MVP2](021-autopilot-mvp2.md) — deferred; path steps use same lerp/step rules
