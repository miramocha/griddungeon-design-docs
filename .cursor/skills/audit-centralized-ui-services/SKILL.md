---
name: audit-centralized-ui-services
description: >-
  Audits Grid Dungeon UI presenters, facades, and phase HUD wiring against
  centralized-ui-services.md and ICentralizedUiSurface. Auto-enables caveman
  mode (full) for audit output. Use when auditing a component for centralized
  UI service compliance, migration readiness, CloneTree embed smells, facade
  lifecycle vocabulary, presentation bus shells/projectors, or before/after
  extracting a picker/overlay to GameState.
---

# Audit centralized UI services

## On invoke (required)

**First action:** activate **caveman** mode before scan or report.

1. Read and follow the **caveman** skill (`~/.agents/skills/caveman/SKILL.md`, or user invokes `/caveman`).
2. Default intensity: **full**.
3. Caveman for user-facing audit prose — summary, findings, fix order.
4. **Normal (not caveman):** code citations, grep commands, report tables, commits/PRs.
5. Stays active until user says `stop caveman` or `normal mode`.

## Authority (read first)

| Doc | Path |
|-----|------|
| Rule | `.cursor/rules/centralized-ui-services.mdc` |
| Shell rule | `.cursor/rules/presentation-shell.mdc` |
| Design | `griddungeon-design-docs/docs/04-dev/centralized-ui-services.md` |
| Gotchas | `griddungeon-design-docs/docs/04-dev/centralized-ui-gotchas.md` |
| Shell gotchas | `griddungeon-design-docs/docs/04-dev/presentation-shell-gotchas.md` |
| Interface | `Assets/Scripts/Core/UI/ICentralizedUiSurface.cs` |
| Epic | [game#206](https://github.com/miramocha/griddungeon-game/issues/206) |

**Gold references (shipped):** `ItemListInventoryPresenter` + `ItemListInventory`, `SkillUsePickerPresenter` + `SkillUsePickerOverlay`, `CharacterDetailPresenter` + `CharacterDetail`, `CommandRailPresenter`, `InputHintPresenter`.

## When to use

- User asks to audit a component against centralized UI services
- PR migrates picker/modal off a phase HUD (`HubHud`, `CombatHud`, `PartyMenu`)
- New cross-phase overlay proposed under `GameState`
- Review facade API (`IsOpen` vs `IsShown`, missing `HideImmediate`)
- Pre-close checklist for lifecycle tickets (#207–#217 family)
- PR touches presentation bus (`*ScreenShell`, `*PresentationProjector`, `UiPresentationBridge`, `PresentationShellHost`)

## Scope

Run greps in **griddungeon-game** unless user scopes docs-only.

| In scope | Defer (note only) |
|----------|-------------------|
| `Assets/Scripts/UI/Views/*Presenter*.cs` | Phase HUD layout-only USS |
| Static facades (`ItemListInventory`, `SkillUsePickerOverlay`, …) | `ScreenFadePresenter` (exception) |
| Phase HUD orchestration (`HubHudView`, `CombatHudView`, …) | Editor dev tools unless shipping |
| `DevBootstrapSceneCreator` / `DevSceneComposition.Wire*` | uGUI |

## Workflow

```
Task Progress:
- [ ] 1. Name target component + intended service role
- [ ] 2. Run smell greps (embed, dock, lifecycle)
- [ ] 3. Score ICentralizedUiSurface checklist
- [ ] 4. Compare to nearest gold reference
- [ ] 5. Check gotchas (settle, context switch, rail chrome, shell bus if applicable)
- [ ] 6. Report with severity + migration steps
```

### 1. Identify audit target

Record:

- **Component** (presenter, facade, phase view, or proposed service)
- **Concern** (picker, floater, hint strip, rail, fade, …)
- **Consumers** (who calls `Show` / open / reads `IsOpen`)

### 2. Smell greps (game repo root)

**Embedded service trees on phase HUDs:**

```powershell
rg "CloneTree\(" Assets/Scripts/UI/Views --glob "*Hud*.cs"
rg "CloneTree\(.*(Picker|Inventory|Overlay|Bag)" Assets/Scripts
```

**Cross-document dock / geometry sync:**

```powershell
rg "worldBound|GeometryChangedEvent|DockBag|UndockBag|SyncBagDock|Sync.*Geometry" Assets/Scripts/UI
```

**Lifecycle vocabulary on facades / public surfaces:**

```powershell
rg "bool IsOpen|IsVisible|IsActive" Assets/Scripts/UI/Views --glob "*Overlay*.cs" "*Inventory*.cs" "*Presenter*.cs"
rg "RequestedVisible|IsShown|IsSettling|HideImmediate" Assets/Scripts/UI/Views
```

**Hand-rolled PopIn (should use `CentralizedUiPresentation`):**

```powershell
rg "PopInTransition\.(PlayEnter|PlayExit)" Assets/Scripts/UI Assets/Scripts/Runtime/UI --glob "*.cs"
```

**Phase HUD owning service host:**

```powershell
rg "SkillUsePicker|ItemListPicker|PartyInventoryBag|CharacterDetail" Assets/Scripts/UI/Views/CombatHudView.cs Assets/Scripts/UI/Views/HubHudView.cs Assets/Scripts/UI/Views/PartyMenuOverlayView.cs
```

**Bootstrap wiring:**

```powershell
rg "Wire(ItemListInventory|SkillUsePicker|CharacterDetail|InputHint)" Assets/Scripts/Editor
```

### 3. `ICentralizedUiSurface` checklist

Score each row: **Pass** / **Fail** / **N/A** / **Partial**.

| # | Requirement | Pass looks like |
|---|-------------|-----------------|
| 1 | Standalone `GameObject` + `UIDocument` under `GameState` | `DevBootstrapSceneCreator` child; not phase UXML embed |
| 2 | Presenter implements `ICentralizedUiSurface` (or composes `CentralizedUiPresentation` + presenter delegates) | `ItemListInventoryPresenter.Lifecycle.cs`, `SkillUsePickerPresenter` |
| 3 | Facade exposes `RequestedVisible`, `IsShown`, `IsSettling` | Not `IsOpen` / context-only flags as visibility |
| 4 | `HideImmediate()` for ownership / lifecycle only | Context enum swap, `OnDisable`, competing overlay — not mid-beat snap while chrome visible |
| 5 | `Hide()` / facade `Clear` for player-visible dismiss | Beat start, service close within phase; see [no hard cuts](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/04-dev/uitk-bem-transition-guide.md#no-hard-cuts-player-visible-showhide) |
| 6 | `sortingOrder` documented constant on presenter | Match table in centralized-ui-services.md § sortingOrder |
| 7 | Modal chrome via USS (`tabbed-picker--modal-centered`, `--rail-offset`) | Not inline `style.left` from foreign `worldBound` |
| 8 | `pickingMode` on service overlay when interactive | `SyncPickingMode` pattern |
| 9 | `DevSceneComposition.Wire…` + bootstrap menu | No serialized picker UXML on phase HUD |
| 10 | Phase view orchestrates via facade only | `SkillUsePickerOverlay.Input`, not `CombatHudView` host fields |
| 11 | No bind footers on modal chrome | `InputHints` / `TabbedPickerRailHints` only |
| 12 | Edit Mode tests for lifecycle | `*PresenterTests`, picker view settle tests |

**Exceptions (document N/A):** `ScreenFadePresenter` — imperative fade, no `ICentralizedUiSurface`.

### 4. Gotcha cross-check

Read [centralized-ui-gotchas.md](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/04-dev/centralized-ui-gotchas.md) for target:

| Gotcha | Audit question |
|--------|----------------|
| Pop-in exit vs rapid reopen | Reopen during `IsSettling` calls `Show`, not data-only refresh? |
| `IsActive` ≠ on-screen | Public API distinguishes settling vs shown? |
| Context switch (shared picker) | `HideImmediate` / `ForceCloseImmediate` on enum swap — not animated hide across authorities? |
| No hard cut | Runtime beat code (`FloorTransitionPresenter`) uses `Hide()` not `HideImmediate` on visible chrome? Phase owner clears at beat start? |
| Modal rail chrome leak | `CommandPanelModalSupport.ResetPanelChrome` on combat leave? |
| OpenStateChanged vs PresentationChanged | Facade notifies consumers when force-closed? |

### 4b. Presentation bus / shell (when target is projector, shell, or bus wiring)

Read [presentation-shell-gotchas.md](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/04-dev/presentation-shell-gotchas.md) and `.cursor/rules/presentation-shell.mdc`.

| Gotcha | Audit question |
|--------|----------------|
| Stale DTO targeting | Input-sensitive chrome from live controller, not `bridge.Current*` on fast events? |
| Formation bind gated on bus | `RefreshRosters()` / `BindParty` still run when bridge exists? |
| HUD unwires projector | Wire/unwire only on bridge + phase lifecycle — not HUD `OnDisable`? |
| Double chrome refresh | HUD uses `IfNotOnBus` (or equivalent) when shell `Apply` owns chrome? |
| Scene shell missing | Catalog `shellPrefab: null` surfaces have scene `I*Shell` + bootstrap row? |
| Gameplay in shell | `Apply` / `PlayBeat` display-only — no `CombatController` / save calls? |
| Partial unwired DTO | `Clear()` all scalar fields on projector unwired publish? |
| Projector tests | `GameState` pinned to correct `GamePhase` for `Wire()` — not `null`? |

### 5. Compare to gold reference

| Target type | Compare against |
|-------------|-----------------|
| Tabbed picker modal | `ItemListInventoryPresenter` (multi-context) or `SkillUsePickerPresenter` (single combat) |
| Party menu satellite panel | `CharacterDetailPresenter` |
| Collapse / slide strip | `PartyFormationFloaterPresenter`, `WalletHudPresenter`, `InputHintPresenter` |
| Rail shell | `CommandRailPresenter` + `CommandRailScreenShell` |
| Bus roster shell | `CombatRosterPresentationProjector` + `CombatRosterScreenShell` |

List **intentional deltas** (e.g. skill rows use `SkillUsePickerToolkitView`, not `ItemListPickerView`).

## Report template

```markdown
## Centralized UI services audit (YYYY-MM-DD)

**Target:** `ComponentName` / `path/`
**Role:** [picker | floater | hint | rail | …]
**Reference:** `GoldPresenter` + facade

### Verdict
[Not a service | Partial migration | Compliant | Regression risk]

### Checklist (ICentralizedUiSurface)
| # | Item | Status | Notes |
|---|------|--------|-------|

### Blocker
| Issue | Location | Fix |
|-------|----------|-----|

### Should fix
| Issue | Location | Fix |
|-------|----------|-----|

### Nit
| Issue | Location | Fix |
|-------|----------|-----|

### Recommended migration order
1. …
2. …

### Validation
- Edit Mode: `Tests → UI → …`
- Manual: DevBootstrap F1/F2/F3 steps
```

## Fix guidance (when user asks to implement)

1. Add `GameState` child + `UIDocument` + presenter; `Wire…` in `DevSceneComposition`.
2. Move UXML to `Assets/UI/Screens/Shared/*Overlay.uxml` with full-bleed wrapper.
3. Static facade: `Register`/`Unregister`, lifecycle vocabulary, domain input (`CombatItemInput`, `Input`, …).
4. Strip `CloneTree` / host fields from phase HUD; subscribe facade events only.
5. Phase sync → presenter `HideImmediate`; remove duplicate teardown from phase view.
6. Tests: presenter lifecycle + view settle window (`SimulateDueExitCompletionForTests` when panel has PopIn).
7. Update `centralized-ui-services.md` migration table if status changes (docs repo / docs#29).

## Out of scope

- Story/dialogue copy edits
- USS class-toggle audit — use `audit-uitk-uss-class-toggles`
- Implementing fixes unless user asks

## Related

- `audit-uitk-uss-class-toggles` — inline `style` vs BEM modifiers
- `test-plan-grid-dungeon` — close-out verification
- `visualize-uitk-uxml` — hierarchy before/after migration
