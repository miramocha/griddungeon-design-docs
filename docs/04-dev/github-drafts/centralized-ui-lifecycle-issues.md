# GitHub index — Centralized UI presentation lifecycle

**Filed on GitHub.** Use this page as a stable doc link when pointing agents, PRs, or ADRs at the lifecycle refactor. Authoritative API summary: [centralized-ui-services.md § Presentation lifecycle](../centralized-ui-services.md#presentation-lifecycle-in-progress).

---

## Epic

| Repo | # | Title |
|------|---|--------|
| game | [#206](https://github.com/miramocha/griddungeon-game/issues/206) | Tech debt: unified modal show/hide lifecycle for centralized UITK services |

Parent UITK epic: [game#201](https://github.com/miramocha/griddungeon-game/issues/201).

---

## Pull order (implementation)

| Order | Repo | # | Title | Depends |
|-------|------|---|--------|---------|
| 1 | game | [#207](https://github.com/miramocha/griddungeon-game/issues/207) | `ICentralizedUiSurface` + internal `IPresentationDriver`; migrate `ItemListPickerView` | — |
| 2 | game | [#209](https://github.com/miramocha/griddungeon-game/issues/209) | `CharacterDetail` adopt lifecycle | #207 |
| 3 | game | [#208](https://github.com/miramocha/griddungeon-game/issues/208) | `PartyMenuOverlayView` orchestration (detail ↔ bag) | #209 (preferred) |
| 4 | design-docs | [#29](https://github.com/miramocha/griddungeon-design-docs/issues/29) | Docs: vocabulary + gotchas sync | #207 shipped |

---

## Public API (target — not all shipped)

Transition-agnostic. Visual drivers stay internal.

| Term | Meaning |
|------|---------|
| `Show()` | Request on-screen presentation |
| `Hide()` | Same-authority dismiss (may settle) |
| `HideImmediate()` | Authority change — no deferred callbacks |
| `RequestedVisible` | Context/intent open |
| `IsShown` | Settled on-screen |
| `IsSettling` | Between requested and shown (enter or exit) |

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

**Avoid on public surface:** `PlayEnter`, `IsClosing`, `PopIn`, animation ms, USS class names.

---

## Lifecycle rules (authority)

| Call | When |
|------|------|
| `Hide()` | Player dismiss, same context |
| `HideImmediate()` | Phase exit, context enum swap, competing overlay |
| Refresh while settling | `Show` path, not data-only refresh |

Reference behavior today: `ItemListPickerView` (`ItemListInventory`). Primary bug surface: `CharacterDetailPresenter`.

---

## Related docs

| Doc | Role |
|-----|------|
| [centralized-ui-services.md](../centralized-ui-services.md) | Pattern + § Presentation lifecycle |
| [centralized-ui-gotchas.md](../centralized-ui-gotchas.md) | Pop-in exit vs reopen, context switches |
| [shared-menu-picker-ui.md](../shared-menu-picker-ui.md) | Picker shells, rail focus |

---

## Out of scope (epic)

- uGUI migration
- Merging `CharacterDetail` + `ItemListInventory` into one `UIDocument`
- Party formation collapse driver unification (floater stable today)
- Story/dialogue copy
