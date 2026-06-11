# GitHub index — Centralized UI presentation lifecycle

**Filed on GitHub.** Authoritative API + **mandatory `ICentralizedUiSurface` rule:** [centralized-ui-services.md § Presentation lifecycle](../centralized-ui-services.md#presentation-lifecycle).

---

## Epic

| Repo | # | Title |
|------|---|--------|
| game | [#206](https://github.com/miramocha/griddungeon-game/issues/206) | Tech debt: unified modal show/hide lifecycle for centralized UITK services |

Parent UITK epic: [game#201](https://github.com/miramocha/griddungeon-game/issues/201).

**Scope (2026-06):** All centralized `GameState` service documents — PopIn modals, slide strips, collapse floaters — must implement `ICentralizedUiSurface`. Exception: `ScreenFadePresenter` (imperative beat fade).

---

## Pull order (implementation)

| Order | Repo | # | Title | Depends |
|-------|------|---|--------|---------|
| 1 | game | [#207](https://github.com/miramocha/griddungeon-game/issues/207) | Contract + `ItemListPickerView` | — ✅ |
| 2 | game | [#209](https://github.com/miramocha/griddungeon-game/issues/209) | `CharacterDetail` | #207 ✅ |
| 3 | game | [#208](https://github.com/miramocha/griddungeon-game/issues/208) | Party menu orchestration | #209 |
| 4 | game | [#217](https://github.com/miramocha/griddungeon-game/issues/217) | `CommandRail` + `CommandRailInfo` | #207; pairs #208 |
| 5 | game | [#213](https://github.com/miramocha/griddungeon-game/issues/213) | `ItemListInventory` facade lifecycle | #207 |
| 6 | game | [#212](https://github.com/miramocha/griddungeon-game/issues/212) | `SkillUsePicker` | #207 |
| 7 | game | [#215](https://github.com/miramocha/griddungeon-game/issues/215) | `WalletHud` + `SlidePresentationDriver` | #207 |
| 8 | game | [#216](https://github.com/miramocha/griddungeon-game/issues/216) | `InputHint` + slide driver | #215 |
| 9 | game | [#214](https://github.com/miramocha/griddungeon-game/issues/214) | `PartyFormationFloater` + `CollapsePresentationDriver` | #207 |
| 10 | design-docs | [#29](https://github.com/miramocha/griddungeon-design-docs/issues/29) | Docs: vocabulary + gotchas sync | migrations |

---

## Public API (shipped on `GridDungeon.UI`)

```csharp
public interface ICentralizedUiSurface
{
    bool RequestedVisible { get; }
    bool IsShown { get; }
    bool IsSettling { get; }
    event Action? PresentationChanged;
    void Show();
    void Hide();
    void HideImmediate();
}
```

**Required** on every centralized service presenter. **Avoid on public surface:** `PlayEnter`, `IsClosing`, `PopIn`, animation ms, USS class names.

---

## Internal drivers

| Driver | Services |
|--------|----------|
| `PopInPresentationDriver` | Inventory picker, character detail, skill picker |
| `RailEnterPresentationDriver` (or slide) | Command rail panel (`CommandRailEnterTransition`) |
| `SlidePresentationDriver` | Wallet HUD, input hints |
| `CollapsePresentationDriver` | Party formation floater |

---

## Related docs

| Doc | Role |
|-----|------|
| [centralized-ui-services.md](../centralized-ui-services.md) | Pattern + mandatory lifecycle |
| [centralized-ui-gotchas.md](../centralized-ui-gotchas.md) | Pop-in exit vs reopen |
| [shared-menu-picker-ui.md](../shared-menu-picker-ui.md) | Picker shells, rail focus |

---

## Out of scope (epic)

- uGUI migration
- Merging `CharacterDetail` + `ItemListInventory` into one `UIDocument`
- Story/dialogue copy
