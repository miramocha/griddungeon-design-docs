# ADR 009 — PC Input Bindings

**Status:** Accepted  
**Date:** 2026-05-20

## Context

[ADR 008](008-campaign-defaults.md) locks **PC** as primary platform. [ADR 012](012-unity-6-stack.md) locks **Unity 6 + Input System**. Exploration uses 6 movement actions + interact; combat uses commands + mouse targeting; map uses pan/zoom.

## Decision

1. **Keyboard** for grid movement (Etrian Odyssey HD PC): `W/S` forward/back, `Q/E` strafe, `A/D` turn, `Space` interact.
2. **Mouse** for combat targeting and map pan/zoom; not for FPV movement.
3. **Protocol** on core turn when Synchro = 100%: `U` + confirm `Enter` ([ADR 020](020-team-burst-naming.md)); `1`–`9` for Protocol skill picks (no overlap with combat commands).
4. **Combat commands** `Z`/`X`/`C`/`V`/`B` (attack, guard, skill, item, flee); `Space` confirm targeting, `R`/`Esc` cancel/back; combat pause unbound until ADR 015 UI ships.
5. **Map** `M` toggle; LMB drag pan; wheel zoom.
6. **Rebindable** via settings when implemented; defaults in [input-bindings.md](../docs/02-systems/input-bindings.md).
7. **Gamepad** deferred.

## Related

- [Input bindings](../docs/02-systems/input-bindings.md)
