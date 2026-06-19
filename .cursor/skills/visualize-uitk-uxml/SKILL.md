---
name: visualize-uitk-uxml
description: >-
  Builds ASCII UI trees, phase visibility tables, and cross-UIDocument maps for
  Unity UI Toolkit UXML. Use when the user asks to visualize, diagram, or explain
  a UXML hierarchy (e.g. CommandRail, HubHud, PartyMenu), trace name hooks to C#,
  or compare rail vs overlay documents.
---

# Visualize UITK UXML

## When to use

- User asks for a **tree**, **diagram**, **map**, or **where is X in UXML**
- Planning refactors across **CommandRail**, HUD shells, overlays, pickers
- Explaining **phase / Tab / context** visibility (hub vs exploration vs combat)
- Handoff docs after touching `Assets/UI/Screens/**/*.uxml`

Complements [unity-ui-toolkit.mdc](../../rules/unity-ui-toolkit.mdc) (BEM + `name` hooks). This skill owns **output format and research steps**.

## Output format (required sections)

Deliver in this order unless the user asks for tree only:

### 1. ASCII tree

- Use ASCII branches from script (`+--`, `` `-- ``, `|` indent) or Unicode box-drawing in chat markdown
- Each line: **UXML `name`** (primary) + short role in brackets
- Include **control `text="..."`** for `Button` / `Label` when static in UXML
- Mark **code-built** hosts: `← Populate()` / `RailMenuPresenter.CreateButton`
- Mark **hidden by default**: `--hidden`, `display: none` hosts

### 2. Phase / state table (when HUD is phase-driven)

| Phase | Input state | Visible branch | Owner presenter |

### 3. Separate UIDocuments (when more than one `UIDocument`)

List each document, `sortingOrder` if known, and what is **not** in CommandRail.

### 4. Optional mermaid

Use only for **multi-document** or **sequence** flows (open Shop, Tab party menu). Follow plan-mode mermaid rules (no spaces in node IDs).

## Workflow

```
Task Progress:
- [ ] 1. Identify root UXML path(s) under Assets/UI/
- [ ] 2. Run uxml_tree.py (or Read UXML if script unavailable)
- [ ] 3. Grep C# for name hooks and presenters
- [ ] 4. Read USS for --hidden / context BEM modifiers
- [ ] 5. Emit tree + tables; link file paths
```

### 1. Find roots

| Ask | Start here |
|-----|------------|
| Global left rail | `Assets/UI/Screens/Shared/CommandRail.uxml` |
| Hub overlay / shop picker | `Assets/UI/Screens/Hub/HubHud.uxml` |
| Party Tab shell | `Assets/UI/Screens/Shared/PartyMenu.uxml` |
| Exploration | C# map hosts (`MapGridHostBuilder` + `MapView.uss`), `PartyFormationFloater.uxml`, `PartyMenu.uxml` |
| Combat | `Assets/UI/Screens/Combat/CombatHud.uxml` |
| Empty rail template | `Assets/UI/Screens/Shared/RailMenuVertical.uxml` |

### 2. Generate tree (griddungeon-game root)

```powershell
python .cursor/skills/visualize-uitk-uxml/scripts/uxml_tree.py Assets/UI/Screens/Shared/CommandRail.uxml
```

Multiple files:

```powershell
python .cursor/skills/visualize-uitk-uxml/scripts/uxml_tree.py `
  Assets/UI/Screens/Shared/CommandRail.uxml `
  Assets/UI/Screens/Hub/HubHud.uxml `
  Assets/UI/Screens/Shared/PartyMenu.uxml
```

Script prints `name`, `class`, `text`, `Style src`, `Instance template`. It does **not** expand UXML templates — note `<ui:Instance>` as `template="..."`.

### 3. Wire C# and presenters

Grep patterns:

```text
rg 'Q<.*>\("[^"]+"\)' Assets/Scripts/UI --glob "*.cs"
rg 'CommandRail\.|UIDocument|sortingOrder' Assets/Scripts/UI
rg 'CloneTree|VisualTreeAsset' Assets/Scripts/UI
```

For each `name="foo"` queried in code, annotate tree node `foo ← HubHudView`.

Presenter → document map (extend as needed):

| Presenter | UXML / mount |
|-----------|----------------|
| `CommandRailPresenter` | `CommandRail.uxml` |
| `HubHudView` | `HubHud.uxml` + clones pickers into `hub-hud` |
| `PartyMenuOverlayView` | `PartyMenu.uxml`; section rail = `CommandRail.PartySectionRailRoot` |
| `MapView` | mounted under `ExplorationHud` |
| `CombatHudView` | `CombatHud.uxml` + cloned pickers |

### 4. USS visibility

Read paired `.uss` for:

- `display: none` + `--hidden` modifiers
- Context selectors (e.g. `command-rail--context-hub`)
- `transition-property` on rail enter (see `CommandRailEnterTransition`)

Annotate tree leaves with **instant hide** vs **animated** when relevant.

## Rules

1. **Separate rail from overlay** — CommandRail is one `UIDocument`; party backdrop and shop pickers are others unless user scopes one file.
2. **Same rail instance** — Hub Tab and Exploration Tab share `party-menu-nav` on `CommandRailPresenter`.
3. **Do not invent nodes** — only UXML, cloned templates, or documented `Populate()` builders.
4. **Cite paths** — use repo paths like `Assets/UI/Screens/Shared/CommandRail.uxml`.
5. **Proportion** — small screen = tree only; architecture questions = tree + table + UIDocuments.

## Canonical example

Full CommandRail walkthrough: [examples.md](examples.md).

## Related

- Code-driven rail refactor plan: `.cursor/plans/` or issue context
- `audit-uitk-uss-class-toggles` — USS class usage, not hierarchy
- Design reference: [shared-menu-picker-ui.md](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/04-dev/shared-menu-picker-ui.md)
