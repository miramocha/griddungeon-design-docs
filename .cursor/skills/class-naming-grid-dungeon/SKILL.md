---
name: class-naming-grid-dungeon
description: >-
  Pick C# type suffix and assembly before creating or renaming classes. Read
  class-naming-patterns.md via review-config.json. Use when adding new C# types,
  choosing View vs Presenter vs Coordinator, splitting god classes, or renaming
  type suffixes in griddungeon-game.
---

# Grid Dungeon class naming

## When to use

- Adding a new `class`, `interface`, or `struct` under `Assets/Scripts/` or `Assets/Tests/`
- **Renaming** a type or changing its role suffix (`*View` → `*Presenter`, etc.)
- Splitting a large type — `partial class` vs new public type
- User asks what to call a class or which suffix fits

Skip for trivial edits inside an existing type (no new/rename).

## Authority chain

| Order | Source | Use for |
|-------|--------|---------|
| 1 | `.cursor/review-config.json` → `classNaming.patternsDoc` | **Decision flow**, locked suffix distinctions, partial-class seams |
| 2 | `.cursor/rules/unity-csharp-class-suffix-patterns.mdc` | Compressed assembly → suffix table |
| 3 | `classNaming.shippedTypesDoc` | **Duplicate-name lookup only** — not for picking suffixes |
| 4 | `unity-core-campaign-assembly.mdc` | Core vs Campaign placement |

## Workflow

```
- [ ] 1. Read patternsDoc — at minimum § Decision flow + the suffix section for your layer
- [ ] 2. Pick assembly (Core / Campaign / Runtime / UI / Tests / Editor)
- [ ] 3. Pick suffix from decision flow — not from the nearest existing type name
- [ ] 4. Grep codebase (or shippedTypesDoc) for name collision
- [ ] 5. Choose folder + namespace (mirror path: GridDungeon.UI.Views, …)
- [ ] 6. If host file would exceed ~300 lines, plan partial `{Type}.{Concern}.cs` before coding
- [ ] 7. One primary public type per file; filename = class name
```

## Quick suffix picks (confirm in patternsDoc)

| Question | Lean toward |
|----------|-------------|
| Pure math / eligibility? | Core `*Calculator` / `*Rules` / `*Resolver` |
| Stratum or story policy? | Campaign |
| Binds UXML, no overlay lifecycle? | UI `*View` |
| Owns `UIDocument` / centralized overlay? | UI `*Presenter` |
| DOTween on phase HUD chrome only? | UI `*ReactivePresenter` |
| Modal/pick flow without tree? | `*Coordinator` or `*Host` |
| Subsystem authority? | Runtime `*Controller` / `*System` / `*Service` |
| Scene composition root (visibility)? | Runtime `*Host` (`DungeonSceneHost`) |
| Rail/tab focus over existing tree? | UI `*Focus` / `*Navigator` — not `*Presenter` |

## Output before coding

State briefly (in chat or PR):

- **Name:** `FooBarPresenter`
- **Assembly / folder:** `GridDungeon.UI` / `Assets/Scripts/UI/Views/`
- **Why:** owns `UIDocument` overlay lifecycle — not a bind-only `*View`

## Related rules

- [unity-csharp-class-creation.mdc](../../rules/unity-csharp-class-creation.mdc) — always-on reminder
- [code-review-config.mdc](../../rules/code-review-config.mdc) — review gate on adds/renames
- [class naming patterns](../../docs/04-dev/class-naming-patterns.md) — full authority (design-docs)
