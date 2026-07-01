---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/campaign/s1
---
# ADR 008 — Campaign Defaults (FOE Respawn, Exploration, Platform)

**Status:** Accepted  
**Date:** 2026-05-20

## Context

Launch defaults for FOE respawn on hub re-entry, exploration limits (no TP clock), target platform, and out-of-scope burst mechanics.

## Decision

1. **FOE respawn:** When party **returns to hub** and re-enters a floor, **FOEs respawn** to authored positions (map progress persists).
2. **Exploration limits:** **Unlimited steps** — no TP/food clock for labyrinth movement (EO2-style limits out of scope).
3. **Target platform:** **PC** first (keyboard + mouse; gamepad optional later).
4. **Boost/Break:** **Out of scope** — [Synchro Protocol](006-union-team-bar.md) + [Navigator](007-navigator-role.md) cover team burst.

## Related

- [03 — Dungeons & encounters](../docs/03-content/dungeons-and-encounters.md)
- [00 — Vision](../docs/00-vision.md)
