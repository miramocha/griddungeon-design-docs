---
name: create-uitk-design-mirror
description: >-
  Creates or refreshes UITK design-mirror assets under Assets/UI/Editor/DesignMirror/
  from production shells + placeholder fixtures. Use when the user asks to create
  a mock/mirror, bootstrap design mirror, add a new mirrored component, or
  regenerate placeholder UXML/USS for UX visual editing.
---

# Create UITK design mirror

## When to use

- User asks to **create mock**, **create mirror**, **design mirror for X**
- **Bootstrap mirror**, **add mirrored component**, **regenerate placeholder UI**
- Production shell changed — re-expand mirror hosts from fixture (**refresh**; do not wipe UX layout outside `stripHosts` unless user says regenerate from scratch)

**Not this skill:** promoting mirror → production — use **sync-uitk-design-mirror**.

| Ask | Skill |
|-----|-------|
| New mirror / refresh placeholders from prod | **create-uitk-design-mirror** |
| UX finished editing → promote to production | **sync-uitk-design-mirror** |

## Authority

- [unity-ui-toolkit.mdc](../../rules/unity-ui-toolkit.mdc) — BEM, `name` hooks, no logic in UXML
- [uitk-design-mirror.mdc](../../rules/uitk-design-mirror.mdc) — UX edits only `UI/Editor/DesignMirror/`
- [docs/04-dev/uitk-design-mirror.md](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/04-dev/uitk-design-mirror.md)
- [default-release-scope-language.mdc](../../rules/default-release-scope-language.mdc) — no `phase` / `MVP` / `PoC` in `Assets/**`
- Complements **visualize-uitk-uxml** (read prod tree) and **sync-uitk-design-mirror** (promote back)

## Workflow

```
Task Progress:
- [ ] 1. Resolve component id from user arg or `mirror-manifest.yaml` — stop if manifest `components` is empty and no id was given
- [ ] 2. Read production shellUxml + bindableNames from manifest
- [ ] 3. Grep C# for code-built hosts (*Builder, RailMenuFocus) — annotate static mirror needs
- [ ] 4. Read or create fixture YAML per state (primary `mirror.fixture` + each `states[]` entry — template.md schema)
- [ ] 5. Ensure Assets/UI/Editor/DesignMirror/ exists; write DesignMirror.uxml for primary + each state
- [ ] 6. Seed DesignMirror.uss from production ussTargets (copy selectors UX may edit)
- [ ] 7. Wire Style src — HudOverlay read-only + mirror USS last
- [ ] 8. Append manifest entry if new component
- [ ] 9. Prettier on new .uxml / .uss (prettier-uitk-format)
- [ ] 10. Hand off paths; UX opens mirror UXML in Unity UI Builder — never edit production Screens/
```

Run from **griddungeon-game** root.

### Manifest

`Assets/UI/Editor/DesignMirror/mirror-manifest.yaml` — see [template.md](template.md).

### Fixture

Primary: `mirror.fixture` in manifest. Additional visual states: `states[].fixture` — see [template.md](template.md).

### Row shapes

Static placeholder rows must match `rowTemplate.source` in manifest — [references/row-shapes.md](references/row-shapes.md).

## Create rules

1. **Never write to `Assets/UI/Screens/`** during create — mirror paths only.
2. **Preserve every `bindableNames` `name`** from production shell on the same nodes in mirror.
3. **Expand only `stripHosts`** with static children — tabs, row slots (`windowed-list__slot` × 8, each wrapping one `item-row` when present), sample buttons.
4. **Placeholder copy** from fixture YAML — realistic labels (Stim Draft, 50c, Buy/Sell). **Empty state** — `rows: []`, eight empty slots, blank detail; no `menu-item--focused` row.
5. **Visible steady state** — mirror drops `--hidden` on root; add `pop-in--expanded` on panels with `pop-in` (Builder shows `scale: 0 1` otherwise); populated state includes one `menu-item--focused` row.
6. **States** — when manifest lists `states[]`, emit one `*.DesignMirror.uxml` per state; **share** the component `mirror.uss`. Only primary `mirror.uxml` (or states with `syncToProduction: true`) promote to production shell.
7. **USS** — one editable `*.DesignMirror.uss` per component; UX never opens production USS.
8. **Refresh mode** — merge new bindable names from prod; re-expand hosts from fixture; preserve UX edits outside `stripHosts`.
9. **`.meta`** — Unity Editor generates; run **validate-unity-meta** before commit.
10. **Wording** — no `phase`, `MVP`, `mvp`, or `PoC` in any `Assets/**` file.

## Output deliverables

| Item | Path |
|------|------|
| Mirror UXML (primary) | `Assets/UI/Editor/DesignMirror/.../{Name}.DesignMirror.uxml` |
| Mirror UXML (states) | `.../{Name}.{State}.DesignMirror.uxml` per `states[]` |
| Mirror USS | `Assets/UI/Editor/DesignMirror/.../{Name}.DesignMirror.uss` (shared) |
| Fixture (primary) | `Assets/UI/Editor/DesignMirror/Fixtures/{id}.fixture.yaml` |
| Fixture (states) | `Assets/UI/Editor/DesignMirror/Fixtures/{id}-{state}.fixture.yaml` |
| Manifest row | `mirror-manifest.yaml` `components[]` |
| UX next step | Open `{Name}.DesignMirror.uxml` in Unity UI Builder |

## Canonical example

[examples.md](examples.md) — ItemListPicker first mirror.

## Related

- **sync-uitk-design-mirror** — promote to production
- **prettier-uitk-format** — format changed UXML/USS
- **visualize-uitk-uxml** — ASCII tree of production shell
