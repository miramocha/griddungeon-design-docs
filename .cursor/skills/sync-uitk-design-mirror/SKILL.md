---
name: sync-uitk-design-mirror
description: >-
  Promotes UITK design-mirror layout and USS from Assets/UI/Editor/DesignMirror/
  into production bindable shells under Assets/UI/Screens/. Use when the user
  asks to sync design mirror, promote mirror to production, or apply UX UITK changes.
---

# Sync UITK design mirror

## When to use

- UX finished editing mirror in **Unity UI Builder**
- User asks: **sync design mirror**, **promote mirror to production**, **apply UX UITK changes**
- After mirror refresh when production shell structure changed (verify bindable names still match)

**Not this skill:** creating mirror assets — use **create-uitk-design-mirror**.

## Authority

- [uitk-design-mirror.mdc](../../rules/uitk-design-mirror.mdc)
- [unity-ui-toolkit.mdc](../../rules/unity-ui-toolkit.mdc)
- [docs/04-dev/uitk-design-mirror.md](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/04-dev/uitk-design-mirror.md)
- [default-release-scope-language.mdc](../../rules/default-release-scope-language.mdc)

## Workflow

```
Task Progress:
- [ ] 1. Read mirror-manifest.yaml; resolve component id (default item-list-picker)
- [ ] 2. Read mirror UXML + production shellUxml side by side
- [ ] 3. UXML shell sync (rules below) — strip stripHosts children
- [ ] 4. USS merge — map mirror selectors → ussTargets files
- [ ] 5. Wrapper UXML — Style src list only if imports changed
- [ ] 6. Prettier on touched .uxml / .uss (prettier-uitk-format)
- [ ] 7. request-compile-status.ps1
- [ ] 8. request-test-status.ps1 -Category UI (if production UITK touched)
- [ ] 9. Emit change report (selectors, stripped nodes, bindable name check)
```

Run from **griddungeon-game** root.

## UXML shell sync

Target: `production.shellUxml` (e.g. `ItemListPickerShell.uxml`).

1. **Preserve** every `bindableNames` `name` attribute from manifest.
2. **Copy** hierarchy and `class` on non-host nodes (title, detail, scroll bars, body layout).
3. **Strip** all children under each `stripHosts` entry; leave empty hosts for runtime population.
4. **Do not** copy placeholder `text` into production except existing em-dash defaults on labels.
5. **Do not** add new `Button` elements to production unless manifest + `ItemListPickerView` (or owner) updated.
6. **Reject** non–kebab-case `name` or non-BEM classes added in mirror — report blockers.

### ItemListPicker stripHosts

| Host `name` | Action |
|-------------|--------|
| `item-list-picker-tabs` | Remove all child buttons; keep empty `VisualElement` |
| `windowed-list__slots` | Remove all child rows; keep empty `VisualElement` |

## USS merge

Read `mirror.uss` and each path in `production.ussTargets`.

| Mirror section prefix | Target file |
|-----------------------|-------------|
| `.tabbed-picker`, `.item-list-picker-shell` | `TabbedPicker.uss` |
| `.windowed-list` | `WindowedList.uss` |
| `.item-row` | `ItemListRow.uss` |

For each selector block in mirror USS (skip `@import` lines):

1. If selector exists in target — update rule properties to match mirror.
2. If new selector — append to appropriate target file.
3. Report which file received each selector.
4. Reject selectors that break BEM (`block__element--modifier`).

Do **not** open production USS in UI Builder to apply edits — edit files directly, then Prettier.

## Wrapper UXML

`production.wrapperUxml` — update `<Style src="..."/>` only when mirror added/removed shared imports. Do not expand static tree.

## Verification

```powershell
.\tools\request-compile-status.ps1
.\tools\request-test-status.ps1 -Category UI
```

Manual: DevBootstrap F1 hub shop — picker layout matches synced production after UX mirror edit.

## Change report (required)

Deliver before handoff:

- Bindable `name` hooks verified (list pass/fail)
- UXML nodes copied vs stripped (count under each stripHost)
- USS selectors merged per target file
- Files touched list
- Blockers (non-BEM classes, missing names, new buttons without dev review)

## Related

- **create-uitk-design-mirror** — bootstrap / refresh mirror
- **audit-uitk-uss-class-toggles** — if C# style writes touched during same PR
- **visualize-uitk-uxml** — diff aid via `uxml_tree.py`
