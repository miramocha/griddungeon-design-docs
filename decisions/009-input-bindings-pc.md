# ADR 009 — PC Input Bindings

**Status:** Accepted  
**Date:** 2026-05-20

## Context

[ADR 008](008-campaign-defaults.md) locks **PC** as primary platform. [ADR 012](012-unity-6-stack.md) locks **Unity 6 + Input System**. Exploration uses 6 movement actions + interact; combat uses commands + mouse targeting; map uses pan/zoom.

## Decision

1. **Keyboard** for grid movement: `W/S` forward/back, `Space` interact. **Trial layout (MVP1 playtest):** `A/D` strafe, `Q/E` turn (EO HD PC default was `Q/E` strafe, `A/D` turn — see [input-bindings.md](../docs/02-systems/input-bindings.md)).
2. **Mouse** for combat targeting and map pan/zoom; not for FPV movement.
3. **Protocol** when Synchro = 100%: **`U` or `Enter`** — one-shot in MVP1 (dev `protocol_strike`; no skill sub-menu confirm). `1`–`9` skill picks deferred until Protocol picker UI ([#35](https://github.com/miramocha/griddungeon-game/issues/35)+).
4. **Combat commands** `Z`/`X`/`C`/`V`/`B` (attack, guard, skill, item, flee); `Space` confirm targeting, `R`/`Esc` cancel/back; combat pause unbound until ADR 015 UI ships.
5. **Map** `M` toggle; LMB drag pan; wheel zoom.
6. **Rebindable** via settings when implemented; defaults in [input-bindings.md](../docs/02-systems/input-bindings.md).
7. **Gamepad** deferred.

## Related

- [Input bindings](../docs/02-systems/input-bindings.md)
