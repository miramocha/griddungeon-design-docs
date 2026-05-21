# ADR 001 — Grid Movement Feel

**Status:** Proposed  
**Date:** 2026-05-20  
**Aligns with:** *Etrian Odyssey*

## Context

EO uses discrete grid steps with light animation. Movement must stay compatible with **per-step random encounters**, **FOE patrol ticks**, and **auto-floor mapping**.

## Decision (proposed)

1. **Displacement** — forward, backward, **strafe left**, **strafe right**: one cell, ~0.2s lerp; logic at step start; **facing unchanged**.
2. **Turn in place** — 90°; **no step events** (no encounter, no FOE tick).
3. **During lerp** — block duplicate input; queue one buffered step max.
4. Each completed **displacement** step triggers **FOE patrol** resolution ([ADR 003](003-foe-step-patrol.md)).

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
