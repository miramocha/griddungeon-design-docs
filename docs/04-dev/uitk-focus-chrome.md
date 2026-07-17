---
tags:
  - path/docs/04-dev
  - type/dev
  - scope/required
  - status/active
  - domain/ui
---
# UITK focus chrome

Authority for **interactive row and chip** fill/label pairs on screen-space UITK. Complements [menu primary focus & backdrop UI style](menu-primary-focus-backdrop-style.md) (backdrop epic, meters, flat corners) and [UITK BEM transition guide](uitk-bem-transition-guide.md).

**Focus class:** `menu-item--focused` ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md)). **Accent ink:** `var(--gd-primary)` (pink swatch-01). **Combat-only harm copy/markers:** `var(--gd-danger)` / `var(--gd-danger-muted)` — same color, semantic alias. **Pair ink:** `var(--gd-white)`. **Do not** use `--gd-accent` (blue) for focus chrome.

**Opacity:** steady-state chrome uses **`opacity: 0` or `1` only** — no fractional wash (e.g. `0.72`) on rows/labels. Transitions may tween opacity.

---

## Three variants

| Variant | USS class | Unfocused | Focused |
|---------|-----------|-----------|---------|
| **Filled** (default) | `menu-focus-filled` | primary bg · white labels | white bg · primary labels |
| **Invert** | `menu-focus-invert` | white bg · primary labels | primary bg · white labels |
| **Transparent** | `menu-focus-transparent` | transparent bg · primary labels | white bg · primary labels |

**When to pick:**

| Surface | Variant |
|---------|---------|
| Primary **panel shell** (`--gd-primary` modal) + rows/tabs inside | **Filled** |
| Neutral/surface panel or bone-anchored list on primary backdrop | **Transparent** |
| White-field list that should **poke** primary fill on focus only | **Invert** (rare) |

**Nested accent** (qty / MP badge on filled/transparent focused row): parent white + primary text → badge **primary bg · white text**. Resting badge: white pill · primary text ([`ItemRowQuantity.uss`](../../griddungeon-game/Assets/UI/Screens/Shared/ItemRowQuantity.uss) + `MenuFocusNestedAccent.uss`).

**Flat chrome:** `border-width: 0`, `border-radius: 0` on focus rows/chips unless a documented exception ([menu primary focus § Flat corners](menu-primary-focus-backdrop-style.md#flat-corners)).

---

## Shared USS layout (game repo)

Under `Assets/UI/Screens/Shared/`:

| File | Role |
|------|------|
| `MenuFocusChromeTokens.uss` | Shared tokens (`--gd-menu-focus-chrome-border-width`, radius) |
| `MenuFocusFilled.uss` | `.menu-focus-filled` row/chip fill + label pairs |
| `MenuFocusInvert.uss` | `.menu-focus-invert` |
| `MenuFocusTransparent.uss` | `.menu-focus-transparent` |
| `MenuFocusNestedAccent.uss` | Badge invert on focused filled/transparent rows |
| `MenuFilledChipButton.uss` | **Button-only** overrides (command rail, confirm modal) — imports filled |

`RailMenu.uss` imports transparent, invert, nested accent, and filled button overrides.

**C# hooks** (`RailMenuClasses.cs`):

- `FocusFilledClass` → `menu-focus-filled`
- `FocusInvertClass` → `menu-focus-invert`
- `FocusTransparentClass` → `menu-focus-transparent`
- `RailMenuFocus.ConfigureFilledChipButton` — filled rail/confirm chips

---

## Host scoping

Screen USS (`ItemListInventoryOverlay.uss`, `SkillUsePickerOverlay.uss`, `PartyEquipmentPickerFloater.uss`, …) owns **panel shell**, tab strip layout, and windowed-list chrome strip. **Colors** for rows/chips come from shared variant USS + variant class on the row root — not duplicated per screen.

---

## Shipped examples

| UI | Variant | Notes |
|----|---------|-------|
| Confirm modal buttons | Filled | `ConfigureFilledChipButton` |
| Command rail vertical chips | Filled | `CommandRailPanelBuilder` |
| Item / bag / shop picker rows | Filled | `ItemListRow.uss` on primary shell |
| Combat skill picker rows | Filled | Same `ItemListRowBuilder` + MP badge |
| Party equip picker floater rows | Transparent | Bone-anchored on primary shell |

---

## Related

- [Shared menu & picker UI](shared-menu-picker-ui.md) — `MenuFocusNavigator`, rail bookmark geometry
- [unity-uitk-palette-colors.mdc](../../.cursor/rules/unity-uitk-palette-colors.mdc) — `--gd-primary`, `--gd-danger`
- [unity-uitk-focus-chrome.mdc](../../.cursor/rules/unity-uitk-focus-chrome.mdc) — agent checklist (game repo mirror)
