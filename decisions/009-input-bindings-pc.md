# ADR 009 — PC Input Bindings

**Status:** Accepted (combat UI input amended by [ADR 026](026-combat-menu-focus-navigation.md))  
**Date:** 2026-05-20

## Context

[ADR 008](008-campaign-defaults.md) locks **PC** as primary platform. [ADR 012](012-unity-6-stack.md) locks **Unity 6 + Input System**. Exploration uses 6 movement actions + interact; combat uses commands + mouse targeting; map uses pan/zoom.

## Decision

1. **Keyboard** for grid movement: `W/S` forward/back, `Space` interact. **Trial layout launch playtest):** `A/D` strafe, `Q/E` turn (EO HD PC default was `Q/E` strafe, `A/D` turn — see [input-bindings.md](../docs/02-systems/input-bindings.md)).
2. **Mouse** for combat targeting and map pan/zoom; not for FPV movement.
3. **Protocol** when Synchro = 100%: **`U` or `Enter`** — one-shot at launch (dev `protocol_strike`; no skill sub-menu confirm). `1`–`9` skill picks deferred until Protocol picker UI ([#35](https://github.com/miramocha/griddungeon-game/issues/35)+).
4. **Combat commands** `Z`/`X`/`C`/`V`/`B` (attack, guard, skill, item, flee); `Space` confirm targeting, `R`/`Esc` cancel/back; combat pause unbound until ADR 015 UI ships.
5. **Map** `M` toggle; LMB drag pan; wheel zoom.
6. **Rebindable** via settings when implemented; defaults in [input-bindings.md](../docs/02-systems/input-bindings.md).
7. **Gamepad** deferred.

## Amendments (2026-05-23)

Combat **player command UI** (planning, targeting, summon/per-slot control): superseded by [ADR 026 — Combat menu focus navigation](026-combat-menu-focus-navigation.md) (`Z` confirm, `X` cancel/Back, arrows + `W`/`A`/`S`/`D` on `MenuNavigate` per [2026-05-23 amendment](026-combat-menu-focus-navigation.md#amendment-2026-05-23-wasd-menu-navigate), no direct `Z`/`X`/`C`/`V`/`B` commands, no `R` Back). Exploration, map, and hub deferrals unchanged.

**Skill use picker** ([ADR 035](035-skill-use-picker.md)): while modal open, **`Q`/`E`** = previous/next tab (not exploration turn). Gamepad **`L1`/`R1`** tab cycle **deferred** with general gamepad support.

## Amendment (2026-06) — Universal UI vocabulary

**Motivation:** Menu, picker, and hub input rules were spread across ADR 026, party-menu docs, and per-screen hints. One **layered** vocabulary reduces drift.

**Decision:**

1. **Menu surfaces** (hub, combat command UI, party menu, tabbed pickers) share one PC vocabulary — see [input-bindings.md § Universal PC UI vocabulary](../docs/02-systems/input-bindings.md#universal-pc-ui-vocabulary):

   | Role | Keyboard | Mouse |
   |------|----------|-------|
   | Navigate / focus | `WASD` + arrows | Hover + LMB on control |
   | Confirm | `Z` | LMB |
   | Cancel / back | `X` | RMB (`MenuCancel`) |
   | Tab cycle | `Q` / `E` | LMB on tab |
   | Menu / pause | `Tab` / `Esc` | — |

2. **Exploration FPV exception (unchanged):** with no overlay owning input, `WASD` = displacement, `Q`/`E` = turn — not tab cycle. Overlays gate exploration turn/movement maps.

3. **Hub `Esc`:** binds to `PartyMenu` toggle (parity with `Tab`) when party menu is safe to open.

4. **Combat `Esc`:** pause only when pause UI ships ([ADR 015](015-mvp1-combat.md)); never LIFO Back.

5. **Agent rule:** `.cursor/rules/unity-input-vocabulary.mdc` — hint axis tokens and handler checklist.

Exploration movement trial layout, map pan/zoom, and gamepad deferral unchanged.

## Amendment (2026-06) — Gamepad-ready keyboard layout

**Motivation:** Future gamepad support should not require redesigning every action. Keyboard defaults should cluster on keys that map 1:1 to stick / face / shoulder groups.

**Decision:**

1. **Layout policy** (implementation still deferred): [input-bindings.md § Gamepad-ready keyboard layout](../docs/02-systems/input-bindings.md#gamepad-ready-keyboard-layout-deferred-implementation)
   - **`WASD`** (+ arrows) → left stick / D-pad
   - **`Z` / `X` / `C` / `V`** → face buttons (Xbox **A / B / X / Y**); **`V`** = combat log; **`C`** = map autopilot
   - **`Q` / `E`** → **L1 / R1** shoulder bumpers (tab cycle or exploration turn — phase-gated)
2. **`Tab` / `Esc`** → **Menu** / **Options** (`startButton`); **`M`** (map) → Xbox **View** (`selectButton`); DualSense **touchpad click** (`touchpadButton`, not Create) — not **`C`**, not **L3**.
3. **PC confirm:** **`Z` only** in `GridDungeon.inputactions` — no **`Space`** / **`Enter`** gameplay binds.
4. **Known layout:** Combat log on **`V`** (was **`L`**). Map toggle stays **`M`** (gamepad **View** / PS touchpad), not **`C`**.
5. **Reference table:** [input-bindings.md § PC vs console reference](../docs/02-systems/input-bindings.md#pc-vs-console-reference-locked-intent).
6. **Agent rule:** `.cursor/rules/unity-input-vocabulary.mdc` § Gamepad-ready layout.

## Related

- [Input bindings](../docs/02-systems/input-bindings.md)
- [ADR 026 — Combat menu focus navigation](026-combat-menu-focus-navigation.md)
