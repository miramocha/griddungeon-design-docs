# ADR 026 — Combat menu focus navigation (PC)

**Status:** Accepted  
**Date:** 2026-05-23  
**Supersedes (combat UI input):** [ADR 009](009-input-bindings-pc.md) § combat direct `Z`/`X`/`C`/`V`/`B` commands and planning `R`/`Esc` Back.

## Context

MVP1 combat shipped **direct** keyboard binds (`Z` = Attack, `X` = Guard, …) and **mouse** targeting ([#60](https://github.com/miramocha/griddungeon-game/issues/60)). That works on PC but does not scale to gamepad/console-style **focus + confirm** flows.

Product direction: **cursor navigation** on the command bar (and target list during targeting), **`Z` confirm**, **`X` cancel/Back**, **`Esc` pause** (when pause UI exists). Mouse clicks stay **one-shot** (no extra confirm). Hub service UI is **out of scope** until [#36](https://github.com/miramocha/griddungeon-game/issues/36) ships; if hub lands in MVP1, use the same pattern in a follow-up doc amendment.

**Not in scope:** [#44](https://github.com/miramocha/griddungeon-game/issues/44) — optional **round-end** confirm after all cores are assigned (separate from per-command focus).

## Decision

### Global keys (combat — player command modes)

| Key | Role |
|-----|------|
| **Arrow keys** | Move focus within the **active scope** (command bar or target list) |
| **`Z`** | **Confirm** focused item (`Enter` is an alias) |
| **`X`** | **Cancel** or **Back** (same as **Back button** when that action applies) |
| **`Esc`** | **Pause** in any combat phase when pause UI ships ([ADR 015](015-mvp1-combat.md)); **no-op** until then |
| **`R`** | **Dropped** for Back (no alias) |

**Mouse:** LMB on a command or valid target **queues immediately** (today’s behavior). Keyboard focus is **independent** — clicks do not move the keyboard cursor.

### Command planning (round start)

1. **Formation order:** `PartyCommandBatch.FirstUnassigned` walks `coreSlots`; highlight auto-advances to the next living core without a command ([#58](https://github.com/miramocha/griddungeon-game/issues/58)).
2. **No roster keyboard:** player does not arrow-select cores on the party strip. Mistakes use **`X`** / **Back button** (LIFO undo) or mouse re-select when [#58](https://github.com/miramocha/griddungeon-game/issues/58) follow-up wires LMB.
3. **Command bar focus:** default **Attack** when planning opens for a core. Focus order skips disabled/hidden entries (Flee off, Protocol hidden, etc.). Items include **Attack, Guard, Skill, Item, Flee, Protocol** (when visible), **Back button**.
4. **`Z` on focused command** queues that command (or enters targeting when required).
5. **Back button** is focusable; **`Z`** on it runs the same logic as **`X`** when Back applies (see below).

**Back / `X` behavior** (single implementation — `StepBackCommandPlanning` / `CancelTargetSelection`):

| State | Effect |
|-------|--------|
| **Targeting** sub-step | Cancel targeting; **no** command queued |
| **Planning**, ≥1 command queued | LIFO — remove last queued command; highlight that core |
| **Planning**, nothing queued | No-op |
| **Back button** disabled | No-op |

### Targeting sub-step (Path B — locked)

After **Attack** or single-target **Skill** requires a target:

1. **Focus auto-moves** to the **target list** (valid enemy/ally slots). Command bar does not accept **`Z`** until targeting ends.
2. **Default highlight:** first valid target in calculator order.
3. **Arrow keys** move target highlight among valid slots only.
4. **`Z`** confirms the highlighted target, sets `TargetId`, queues the command, advances planning.
5. **`X`** or **Back button** (or **`Z`** on focused **Back button**) cancels targeting only.
6. **LMB** on a valid slot confirms immediately (no **`Z`**).

### Protocol

**Protocol** is on the command bar focus list; confirm with **`Z`** when Synchro = 100% and unlocked. No instant **`U`** / **Enter** one-shot in this model (those binds may be removed or remapped in implementation).

### Summon / per-slot player turns

Same **focus + `Z` / `X`** pattern for summon and any legacy per-slot player control ([ADR 016](016-summon-control-mvp1.md)). Skill/item **sub-menus** when shipped ([#35](https://github.com/miramocha/griddungeon-game/issues/35)+) use the same navigator.

### Implementation notes

- **`MenuFocusNavigator`** (or equivalent) in `GridDungeon.UI` — testable focus index, skip disabled, Confirm/Cancel callbacks; not in Core.
- **Input maps:** add or remap **MenuConfirm** / **MenuCancel** / **MenuNavigate** on Combat (or bridge `UI.Navigate` + `Submit`/`Cancel` with `Z`/`X` bindings). Remove **`R`** from planning Back.
- **Pause:** bind **`Esc`** when combat pause overlay ships; until then ignore **`Esc`** in combat (do not map to LIFO Back).
- **Dev HUD** (`GamePhaseDevHud`) is explicitly **out of scope**.

### Hub (deferred)

When hub service UI ([#13](https://github.com/miramocha/griddungeon-game/issues/13), [#36](https://github.com/miramocha/griddungeon-game/issues/36)) ships, apply the same **`Z` / `X` / arrows** pattern to root + service menus. Amend this ADR or add a short hub addendum at that time.

## Consequences

- **Breaking change** for players used to `Z`/`X`/`C`/`V`/`B` direct commands and `R`/`Esc` Back.
- **Combat HUD** labels: remove per-button `(Z)` hints; show global **Z Confirm · X Cancel · Esc Pause**.
- **Tests:** Edit Mode for navigator; update `CombatInputHandlerTests`; Play Mode checklist for planning, targeting Path B, LIFO, mouse instant queue.
- **Gamepad (later):** map face buttons to same Confirm/Cancel actions as `Z`/`X`.

## Related

- [Input bindings — Combat](../docs/02-systems/input-bindings.md#combat)
- [Combat — Command planning](../docs/02-systems/combat.md#command-planning--back)
- [ADR 009 — PC input](009-input-bindings-pc.md) (exploration unchanged)
- [ADR 015 — MVP1 combat](015-mvp1-combat.md)
- Implementation: [game repo issues](https://github.com/miramocha/griddungeon-game/issues) filed from ADR 026 (menu focus navigation epic)
