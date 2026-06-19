---
name: audit-uitk-uss-class-toggles
description: >-
  Audits Grid Dungeon UI Toolkit C# for unnecessary VisualElement.style writes that
  should be BEM USS class toggles instead. Auto-enables caveman mode (full) for
  audit output. Use when the user asks to audit inline styles, USS vs C# styling,
  style.display/opacity in views, UITK class toggle compliance, or before/after
  UITK refactors.
---

# Audit UITK — USS class toggles vs C# inline style

## On invoke (required)

**First action:** activate **caveman** mode before scan or report.

1. Read and follow the **caveman** skill (`~/.agents/skills/caveman/SKILL.md`, or user invokes `/caveman`).
2. Default intensity: **full** (user may override with `/caveman lite|ultra|…`).
3. Caveman for all user-facing audit prose — summary, findings, fix order, chat wrap-up.
4. **Normal (not caveman):** code citations, fenced commands, report markdown tables, commits/PRs, security warnings.
5. Stays active until user says `stop caveman` or `normal mode`.

## Authority

- `.cursor/rules/unity-ui-toolkit.mdc` — **Prefer USS class toggles over `element.style` in C#**
- `docs/04-dev/centralized-ui-services.md` — rule 3: USS owns pixels; C# toggles classes

Default: layout, size, colour, visibility, state → **USS** + `EnableInClassList` / `AddToClassList` / `RemoveFromClassList`.

## When to use

- User requests audit of inline `style` vs USS
- PR touches `Assets/Scripts/UI/**` or `Assets/Scripts/Runtime/UI/**`
- New view/presenter adds `element.style.*`
- After CommandRail / map marker / HUD refactors

## Scope

| In scope | Defer (note only) |
|----------|-------------------|
| `Assets/Scripts/UI/**` | `Assets/Scripts/Editor/**` (dev tools) |
| `Assets/Scripts/Runtime/UI/**` | One-off experiments unless shipping |
| Paired `Assets/UI/**/*.uss` | Generated `Library/` |

## Workflow

```
Task Progress:
- [ ] 1. Scan C# for .style. writes
- [ ] 2. Classify each hit (violation / OK / cleanup)
- [ ] 3. Cross-check USS for existing --hidden / modifier
- [ ] 4. Note inconsistent patterns across presenters
- [ ] 5. Report with severity + fix hint
```

### 1. Scan (griddungeon-game root)

Player-facing UI:

```powershell
rg "\.style\." Assets/Scripts/UI Assets/Scripts/Runtime/UI --glob "*.cs"
```

High-signal properties (usually should be USS):

```powershell
rg "\.style\.(display|opacity|width|height|minWidth|maxWidth|minHeight|maxHeight|flexGrow|flexShrink|backgroundColor|color|border|padding|margin|position)\s*=" Assets/Scripts/UI Assets/Scripts/Runtime/UI --glob "*.cs"
```

Existing class-toggle usage (baseline):

```powershell
rg "EnableInClassList|AddToClassList|RemoveFromClassList" Assets/Scripts/UI --glob "*.cs" -c
```

USS modifiers already in project:

```powershell
rg "--hidden|display:\s*none" Assets/UI --glob "*.uss"
```

### 2. Classify each hit

| Severity | Condition | Example fix |
|----------|-----------|-------------|
| **High** | Discrete state; USS modifier exists or project pattern exists | `style.display` → `EnableInClassList("combat-hud--hidden", !show)` |
| **High** | Duplicates USS on same element | `position: Absolute` after `map-view__marker` class |
| **Medium** | Tween cleanup hardcodes value | `style.opacity = 0f` → `style.opacity = StyleKeyword.Null` after `UiToolkitTweens.Kill` |
| **Medium** | Code-built overlay layout could be USS | Attach `ScreenFade.uss` for inset/position |
| **Keep** | Layout-derived or animated | `left`/`top` from grid, `MapGridMarkerAnimator` translate, `UiToolkitTweens` |
| **Keep** | Dynamic asset binding | `style.backgroundImage = new StyleBackground(sprite)` |
| **Nit** | Editor-only `style.display` | Optional follow-up |

### 3. Cross-check rules

Before flagging `style.display` / `style.opacity`:

1. Grep USS for block BEM name + `--hidden`, `--fade-hidden`, `--active`, etc.
2. Grep siblings: did another presenter solve same problem with classes? (e.g. `MapStairsMarkersPresenter` uses `map-view__marker--fade-hidden`; gather/party/foe may still use `display`).
3. If modifier missing, report **add USS + toggle** — not only "use class".

### 4. Known good patterns (do not flag)

```csharp
// Discrete layout axis — USS owns pixels
m_root.EnableInClassList("map-view--fullscreen", fullscreen);
MapViewLayoutClasses.SetPanelCellSize(m_root, cellSizePx);

// Marker visibility — opacity transition in USS
marker.EnableInClassList("map-view__marker--fade-hidden", !visible);

// Tween target — inline required during animation
element.style.translate = new Translate(x, y, 0f); // MapGridMarkerAnimator / UiToolkitTweens
```

### 5. Known smells (usually flag)

```csharp
// ❌ when --hidden exists on same block
m_hudRoot.style.display = visible ? DisplayStyle.Flex : DisplayStyle.None;

// ❌ when .hub-hud already absolute fill in USS
element.style.width = Length.Percent(100);
element.style.flexGrow = 1f;

// ❌ redundant with .map-view__marker { position: absolute }
shell.style.position = Position.Absolute;
```

## Report template

```markdown
## UITK inline-style audit (YYYY-MM-DD)

**Scope:** `path/or/branch`
**Rule:** `unity-ui-toolkit.mdc` — prefer USS class toggles

### High — should fix
| File | Line(s) | Issue | Suggested USS / API |
|------|---------|-------|---------------------|

### Medium — cleanup
| File | Line(s) | Issue | Suggested fix |
|------|---------|-------|---------------|

### Keep (legitimate inline)
| File | Why OK |
|------|--------|

### Inconsistencies
- e.g. stairs markers use `--fade-hidden`; gather markers use `display`

### Recommended fix order
1. …
2. …
```

## Fix guidance (when user asks to implement)

1. Add BEM modifier in paired `.uss` (`block--hidden { display: none; }`).
2. Set default state in UXML class list when possible.
3. Replace C# `style.*` with `EnableInClassList("block--modifier", condition)`.
4. Centralize repeated toggles in small static helper (e.g. `MapViewLayoutClasses`, `CommandRailClasses`).
5. After killing tweens: clear inline with `StyleKeyword.Null`, not hardcoded opacity/translate.
6. Do **not** move layout-derived marker coords to USS.

## Out of scope

- Rewriting story/dialogue copy
- uGUI (`UnityEngine.UI`) — separate audit
- Committing fixes unless user asks

## Related

- Rule: `.cursor/rules/unity-ui-toolkit.mdc`
- Pitfall row: `.cursor/rules/unity-common-pitfalls.mdc` (inline styles)
- Examples: `CombatHudView`, `MapView`, `MapStairsMarkersPresenter`, `HubHudReactivePresenter` (mixed)
