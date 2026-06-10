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
- [centralized-ui-services.md](../../docs/04-dev/centralized-ui-services.md) — rule 3: USS owns pixels; C# toggles classes

Default: layout, size, colour, visibility, state → **USS** + `EnableInClassList` / `AddToClassList` / `RemoveFromClassList`.

**Implementation repo:** run scans in **griddungeon-game** (`Assets/Scripts/UI`, `Assets/UI`).

## When to use

- User requests audit of inline `style` vs USS
- PR touches game repo UITK views/presenters
- New view/presenter adds `element.style.*`
- After CommandRail / map marker / HUD refactors

## Scope

| In scope (game repo) | Defer (note only) |
|----------------------|-------------------|
| `Assets/Scripts/UI/**` | `Assets/Scripts/Editor/**` |
| `Assets/Scripts/Runtime/UI/**` | Generated `Library/` |
| Paired `Assets/UI/**/*.uss` | |

## Workflow

```
Task Progress:
- [ ] 1. Scan C# for .style. writes (griddungeon-game)
- [ ] 2. Classify each hit (violation / OK / cleanup)
- [ ] 3. Cross-check USS for existing --hidden / modifier
- [ ] 4. Note inconsistent patterns across presenters
- [ ] 5. Report with severity + fix hint
```

### 1. Scan (griddungeon-game root)

```powershell
rg "\.style\." Assets/Scripts/UI Assets/Scripts/Runtime/UI --glob "*.cs"
rg "\.style\.(display|opacity|width|height|minWidth|maxWidth|minHeight|maxHeight|flexGrow|flexShrink|backgroundColor|color|border|padding|margin|position)\s*=" Assets/Scripts/UI Assets/Scripts/Runtime/UI --glob "*.cs"
rg "--hidden|display:\s*none" Assets/UI --glob "*.uss"
```

### 2. Classify each hit

| Severity | Condition | Example fix |
|----------|-----------|-------------|
| **High** | Discrete state; USS modifier exists or project pattern exists | `style.display` → `EnableInClassList("combat-hud--hidden", !show)` |
| **High** | Duplicates USS on same element | `position: Absolute` after `map-view__marker` class |
| **Medium** | Tween cleanup hardcodes value | `style.opacity = 0f` → `style.opacity = StyleKeyword.Null` after `UiToolkitTweens.Kill` |
| **Medium** | Code-built overlay layout could be USS | Attach stylesheet for inset/position |
| **Keep** | Layout-derived or animated | `left`/`top` from grid, DOTween translate |
| **Keep** | Dynamic asset binding | `style.backgroundImage = new StyleBackground(sprite)` |

### 3. Cross-check

1. Grep USS for `block--hidden`, `--fade-hidden`, etc.
2. Compare presenters — one may already use class toggles (stairs vs gather markers).
3. Missing modifier → report **add USS + toggle**.

### 4. Known good / smells

See full patterns in game repo copy: `griddungeon-game/.cursor/skills/audit-uitk-uss-class-toggles/SKILL.md` (identical checklist).

## Report template

```markdown
## UITK inline-style audit (YYYY-MM-DD)

**Scope:** `path/or/branch`
**Rule:** `unity-ui-toolkit.mdc`

### High — should fix
| File | Line(s) | Issue | Suggested USS / API |

### Medium — cleanup
| File | Line(s) | Issue | Suggested fix |

### Keep (legitimate inline)
| File | Why OK |

### Inconsistencies
### Recommended fix order
```

## Fix guidance (when user asks to implement)

1. BEM modifier in `.uss`; default in UXML when possible.
2. `EnableInClassList` in C#; helpers for repeated families.
3. Tween cleanup: `StyleKeyword.Null`, not hardcoded values.
4. Do not move layout-derived marker coords to USS.

## Out of scope

Story/dialogue edits; uGUI; commits unless requested.

## Related

- `.cursor/rules/unity-ui-toolkit.mdc`
- `.cursor/rules/unity-common-pitfalls.mdc`
- Game skill (full): `griddungeon-game/.cursor/skills/audit-uitk-uss-class-toggles/SKILL.md`
