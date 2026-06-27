# ADR 026 — Combat menu focus navigation (PC)

**Status:** Accepted  
**Date:** 2026-05-23  
**Supersedes (combat UI input):** [ADR 009](009-input-bindings-pc.md) § combat direct `Z`/`X`/`C`/`V`/`B` commands and planning `R`/`Esc` Back.

## Context

launch combat shipped **direct** keyboard binds (`Z` = Attack, `X` = Guard, …) and **mouse** targeting ([#60](https://github.com/miramocha/griddungeon-game/issues/60)). That works on PC but does not scale to gamepad/console-style **focus + confirm** flows.

Product direction: **cursor navigation** on the command bar (and target list during targeting), **`Z` confirm**, **`X` cancel/Back**, **`Esc` pause** (when pause UI exists). Mouse clicks stay **one-shot** (no extra confirm). Combat is an **instance** of the project-wide [Universal PC UI vocabulary](../docs/02-systems/input-bindings.md#universal-pc-ui-vocabulary) ([ADR 009 amendment](009-input-bindings-pc.md#amendment-2026-06--universal-ui-vocabulary)). Hub service UI is **out of scope** until [#36](https://github.com/miramocha/griddungeon-game/issues/36) ships; if hub lands at launch, use the same pattern in a follow-up doc amendment.

**Not in scope:** [#44](https://github.com/miramocha/griddungeon-game/issues/44) — optional **round-end** confirm after all cores are assigned (separate from per-command focus).

## Decision

### Global keys (combat — player command modes)

| Key | Role |
|-----|------|
| **Arrow keys** or **`W` / `A` / `S` / `D`** | Move focus within the **active scope** (command bar or target list). **`W`/`S`/`A`/`D` mirror arrows** (`W`↑ `S`↓ `A`← `D`→). Exploration movement keys are **not** active in combat — only the Combat `MenuNavigate` composite applies ([amendment](#amendment-2026-05-23-wasd-menu-navigate)). |
| **`Z`** | **Confirm** focused item (`Enter` is an alias) |
| **`X`** | **Cancel** or **Back** (same as **Back button** when that action applies) |
| **`Esc`** | **Pause** in any combat phase when pause UI ships ([ADR 015](015-mvp1-combat.md)); **no-op** until then |
| **`R`** | **Dropped** for Back (no alias) |

**Mouse:** LMB on a command or valid target **queues immediately** (no second confirm step). On focus-nav surfaces, **pointer hover** shares the same highlight index as keyboard focus ([amendment (2026-06)](#amendment-2026-06--pointer-parity-menu-surfaces-within-combat), [ADR 009 amendment](009-input-bindings-pc.md#amendment-2026-06--universal-ui-vocabulary)).

### Command planning (round start)

1. **Formation order:** `PartyCommandBatch.FirstUnassigned` walks `coreSlots`; highlight auto-advances to the next living core without a command ([#58](https://github.com/miramocha/griddungeon-game/issues/58)).
2. **No roster arrow-nav during planning:** player does not **`W`/`A`/`S`/`D`**-select cores on the party strip; formation order still auto-advances ([#58](https://github.com/miramocha/griddungeon-game/issues/58)). Mistakes use **`X`** / **Back button** (LIFO undo). **Pointer** hover / LMB on a living core may **re-select** that core for planning or refresh the skill picker when Skill flow is active ([amendment (2026-06)](#amendment-2026-06--pointer-parity-menu-surfaces-within-combat)).
3. **Command bar focus:** default **Attack** when planning opens for a core. Focus order skips disabled/hidden entries (Flee off, etc.). Items include **Attack, Guard, Skill, Item, Flee, Back button**.
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
3. **Arrow keys** or **`W` / `A` / `S` / `D`** move target highlight among valid slots only (same mapping as command bar).
4. **`Z`** confirms the highlighted target, sets `TargetId`, queues the command, advances planning.
5. **`X`** or **Back button** (or **`Z`** on focused **Back button**) cancels targeting only.
6. **LMB** on a valid slot confirms immediately (no **`Z`**). **Pointer hover** on a valid slot moves target highlight to match keyboard focus ([amendment (2026-06)](#amendment-2026-06--pointer-parity-menu-surfaces-within-combat)).

### Protocol

**Protocol** is on the **synchro bar** when Synchro = 100% and unlocked — **`C`** or **LMB** on the bar ([input bindings](../docs/02-systems/input-bindings.md#protocol-synchro-100)). Not on the command rail focus list.

### Summon / per-slot player turns

Same **focus + `Z` / `X`** pattern for summon and any legacy per-slot player control ([ADR 016](016-summon-control-mvp1.md)). **Skill use picker** ([ADR 035](035-skill-use-picker.md)): row list uses this navigator; **tab cycle** uses **`Q`/`E`** at launch; gamepad **`L1`/`R1`** deferred. Item sub-menu deferred.

### Implementation notes

- **`MenuFocusNavigator`** (or equivalent) in `GridDungeon.UI` — testable focus index, skip disabled, Confirm/Cancel callbacks; not in Core.
- **Input maps:** add or remap **MenuConfirm** / **MenuCancel** / **MenuNavigate** on Combat (or bridge `UI.Navigate` + `Submit`/`Cancel` with `Z`/`X` bindings). **`MenuNavigate`:** arrow keys **and** `W`/`A`/`S`/`D` on the same 2D vector composite. Remove **`R`** from planning Back.
- **Pause:** bind **`Esc`** when combat pause overlay ships; until then ignore **`Esc`** in combat (do not map to LIFO Back).
- **Dev HUD** (`GamePhaseDevHud`) is explicitly **out of scope**.

### Hub (implemented)

Hub service UI ([#13](https://github.com/miramocha/griddungeon-game/issues/13), [#36](https://github.com/miramocha/griddungeon-game/issues/36)) uses the same **`Z` / `X` / arrows / WASD** pattern on root + service menus ([game #98](https://github.com/miramocha/griddungeon-game/issues/98)): `HubInputHandler`, `MenuFocusNavigator`, dedicated `Hub` input map (`MenuNavigate`, `MenuConfirm`, `MenuCancel`). `UI.Submit`/`Cancel` disabled in hub so UIToolkit does not steal `Z`/`X`. Camera pan on root-menu focus remains deferred ([hub-and-services](../docs/02-systems/hub-and-services.md#hub-environment-presentation)); when wired, pans use **Cinemachine 3** ([ADR 033](033-hub-environment-cinemachine.md)).

## Amendment (2026-05-23) — WASD menu navigate

**Motivation:** PC players expect **`W`/`A`/`S`/`D`** to behave like arrow keys in menu-style UI. Combat disables the Exploration action map, so `W`/`A`/`S`/`D` must be **re-bound on Combat `MenuNavigate`**, not inherited from exploration displacement.

**Mapping (locked):**

| Key | Same as | Focus direction |
|-----|---------|-----------------|
| `W` | ↑ | Previous item (same as Up arrow) |
| `S` | ↓ | Next item (same as Down arrow) |
| `A` | ← | Previous item (same as Left arrow) |
| `D` | → | Next item (same as Right arrow) |

**Scope:** Command bar, target list (Path B), summon / per-slot player control — any surface using `MenuNavigate` in combat.

**Implementation:** [game #80](https://github.com/miramocha/griddungeon-game/issues/80) — add four composite parts to `Combat.MenuNavigate` in `GridDungeon.inputactions`; `CombatInputHandler` unchanged if it already reads `Vector2` from `MenuNavigate`.

**Rebind note:** When settings rebind ships, `W`/`A`/`S`/`D` and arrows may be remapped independently unless product chooses a single “menu navigate” binding group.

## Amendment (2026-06) — Pointer parity (menu surfaces within combat)

**Motivation:** [ADR 009 amendment (2026-06)](009-input-bindings-pc.md#amendment-2026-06--universal-ui-vocabulary) locks **hover = navigate/focus** and **LMB = confirm** for menu surfaces. Combat shipped with LMB **instant queue** on commands and targets (no extra **`Z`**), but an older note in this ADR said keyboard focus was fully **independent** of mouse — that blocked parity on pickers, target grids, and command-rail hover. Align combat **focus-nav** surfaces with the universal vocabulary while keeping **one-shot** LMB outcomes on commands and targets.

**Decision:**

| Surface | Pointer hover | LMB | Keyboard equivalent |
|---------|---------------|-----|---------------------|
| **Command bar** (`Button`s) | Moves focus highlight | **Instant** activate (= **`Z`** on focused item) | Arrows / WASD + **`Z`** |
| **Target list** (enemy roster + party grid, Path B) | Moves focus highlight among **valid** slots only | **Instant** confirm (= **`Z`** on focused target) | Arrows / WASD + **`Z`** |
| **Skill / item picker rows** (modal) | Moves row focus | Confirm row (= **`Z`**) | Arrows / WASD + **`Z`**; **`Q`/`E`** tabs unchanged ([ADR 035](035-skill-use-picker.md)) |
| **Planning party grid** (optional) | Moves highlight on living cores | Re-select core; when Skill picker open or Skill command focused, open/refresh picker for that actor | No arrow-nav on roster strip — undo still **`X`** / Back (LIFO) |

**Clarifications (locked):**

1. **Shared focus index** — keyboard and pointer use one `MenuFocusNavigator` (or grid picker) index on focus-nav surfaces. “Independent” in the 2026-05-23 text meant **LMB does not require a second confirm after hover**, not that mouse and keyboard never share highlight state.
2. **Instant queue unchanged** — LMB on a command or valid target still queues in **one click**; hover does not add a confirm step.
3. **Disabled / invalid slots** — pointer hover and click are no-ops (same as keyboard skip rules); invalid targets use non-pickable chrome during Path B.
4. **Out of scope** — Protocol synchro bar (**`C`** / LMB one-shot), exploration movement, map pan/zoom, battle-log toggle (**`V`**), dev HUD.

**Implementation:** `MenuFocusPointerHover`, `MenuFocusNavigator.SetItems`, `CommandRailButtonRowInput`, `PartyFormationGridTargetPicker` / `EnemyFormationGridTargetPicker`, `CombatPlanningPartyPicker`, `WindowedListPaneView` / `ItemListPickerView` pointer activate. Dev reference: [shared menu & picker UI](../docs/04-dev/shared-menu-picker-ui.md).

**Tests:** extend Edit Mode coverage — `TargetSelectionViewTests`, `CombatPlanningPartyPickerTests`, `MenuFocusNavigatorTests`, `ItemListPickerViewTests`; Play Mode — command bar hover+click, target hover+click, skill picker row click, planning roster click when Skill flow open.

## Consequences

- **Breaking change** for players used to `Z`/`X`/`C`/`V`/`B` direct commands and `R`/`Esc` Back.
- **Combat HUD** labels: remove per-button `(Z)` hints; show global **Z Confirm · X Cancel · Esc Pause**.
- **Tests:** Edit Mode for navigator (`MenuFocusNavigatorTests`), command bar (`CommandPanelViewTests`), target list (`TargetSelectionViewTests`, `CombatPlayerCommandGateTests`); Play Mode checklist for planning, targeting Path B, LIFO, mouse instant queue. `CombatInputHandlerTests` removed — routing covered by panel/gate fixtures per [unity-input-system-editmode-tests](https://github.com/miramocha/griddungeon-game/blob/main/.cursor/rules/unity-input-system-editmode-tests.mdc).
- **Gamepad (later):** map [gamepad-ready layout](../docs/02-systems/input-bindings.md#gamepad-ready-keyboard-layout-deferred-implementation) — **`Z`/`X`/`V`** → A/B/Y; combat log on **`V`**; **`Tab`/`Esc`** → **Start**; map **`M`** → **View** / **Select** (locked).

## Related

- [Input bindings — Combat](../docs/02-systems/input-bindings.md#combat)
- [Combat — Command planning](../docs/02-systems/combat.md#command-planning--back)
- [ADR 009 — PC input](009-input-bindings-pc.md) (exploration unchanged)
- [ADR 015 — launch combat](015-mvp1-combat.md)
- Implementation: [game #67](https://github.com/miramocha/griddungeon-game/issues/67) (epic — HUD hint labels, summon control deferred), [#68](https://github.com/miramocha/griddungeon-game/issues/68) (navigator), [#69](https://github.com/miramocha/griddungeon-game/issues/69) (command bar), [#70](https://github.com/miramocha/griddungeon-game/issues/70) (targeting Path B), [#80](https://github.com/miramocha/griddungeon-game/issues/80) (WASD on `MenuNavigate`)
