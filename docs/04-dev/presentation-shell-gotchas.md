---
tags:
  - path/docs/04-dev
  - type/dev
  - scope/required
  - status/active
  - domain/ui
  - domain/phase
---
# Presentation shell — implementation gotchas

Living list of **non-obvious bugs and review traps** when wiring **UITK presentation shells** on the [presentation bus](centralized-ui-services.md#presentation-bus) (`UiPresentationBridge` → projector DTO → `I*Shell.Apply`). Distinct from [centralized UI gotchas](centralized-ui-gotchas.md) (PopIn / `ICentralizedUiSurface` lifecycle on modal services).

**Authority:** [ADR 042](../../decisions/042-presentation-bus.md)  
**Happy path:** [presentation shell implementation](presentation-shell-implementation.md)  
**Reference ship:** combat roster bus ([#314](https://github.com/miramocha/griddungeon-game/issues/314)) — `CombatRosterScreenShell`, `CombatRosterPresentationProjector`

**Implementation repo:** `Assets/Scripts/Runtime/Presentation/`, `Assets/Scripts/UI/Views/*ScreenShell.cs`

---

## How to use this doc

| When | Action |
|------|--------|
| Shell renders but input/chrome is wrong | Check **authority split** and **stale snapshot** sections first |
| Migrating phase HUD chrome onto the bus | Read **hybrid refresh** + **wire lifecycle** before gating direct refresh on `UiPresentationBridge.Instance != null` |
| New `PresentationSurfaceKind` row | Confirm **scene shell vs catalog prefab** and bootstrap checklist |
| Agent implement/review on shell/projector/bridge | Apply [presentation-shell.mdc](../../.cursor/rules/presentation-shell.mdc); cross-check [centralized-ui-services.mdc](../../.cursor/rules/centralized-ui-services.mdc) for modal services |
| Closed a shell/bus bug | Add symptom → cause → fix → test in the same PR or follow-up |

---

## Dual-write — facade + shell re-apply (CommandRailInfo)

**Symptom:** Hub service rail info **flashes then clears** — e.g. Shop sub copy disappears while a title stays; or phase header overwritten with service name.

**Cause:** Facade wrote **both** `CommandRailInfoPresenter` and `CommandRailInfoPresentationProjector`; shell `Apply` re-applied DTO with **hand-rolled if/else** that drifted from presenter API (e.g. required `ServiceLines.Count > 0`, stored service heading in `HeaderTitle`).

**Fix (shipped):**

| Layer | Rule |
|-------|------|
| Facade `CommandRailInfo` | **Bus-first** — projector only when `UiPresentationBridge.Instance != null`; direct presenter only as no-bridge fallback |
| Shell | One line: `Presenter.ApplyPresentationShell(state)` |
| Presenter | **Single mapper** — `ApplyPresentationShell(CommandRailInfoPresentationState)` owns all DTO → view rules |
| DTO | Fields 1:1: `HeaderTitle`, `ServiceHeading`, `ServiceLines`, `CombatPrompt`, `SyncContext`, `Visible`, `HubLeaveHidden` |
| Rail context | `CommandRailPresenter.SyncCommandRailInfo` skips direct presenter when bus wired — `SyncRailContext` + shell apply owns visibility |

**Rule:** New presentation surfaces follow **ConfirmModal / ItemListInventory** pattern — no dual-write; no conditional mapping in shell. Add round-trip test: projector snapshot → `ApplyPresentationShell` → DOM asserts.

**Tests:** `CommandRailInfoScreenShellTests.ApplyPresentationShell_RoundTripFromProjector_MatchesDto`

---

## Authority split — formation bind vs interactive chrome

**Symptom:** Party/enemy plates show name/HP but **attack targeting** does not (`--targetable` missing, clicks ignored).

**Cause:** Phase HUD took a **bus-only** path for highlights — `ApplyHighlightsAndStats(bridge.CurrentCombatRoster)` or equivalent. `OnTargetingChanged` on `CombatController` often fires **before** the projector’s `RebuildAndPublish()` completes, so the bridge snapshot is **one frame stale** (`IsSelectingTarget` / `IsTargetable` flags wrong). `SetTargetHighlights` never runs with live `ValidTargets` → `PickingMode.Ignore` on enemy slots.

**Fix (shipped #314):**

| Concern | Authority | API |
|---------|-----------|-----|
| Formation bind (slot DOM, click handlers) | Live `BattleState` on phase HUD | `RefreshRosters()` → `BindParty` / `BindEnemyFormation` |
| Interactive chrome (targetable, acting, queued, stale) | Live `CombatController` | `RefreshRosterChrome()` → `RefreshTargetHighlights`, `SetActingHighlight`, … |
| Bus DTO | Projector + shell | Snapshot for UVS / future full bus render; shell `Apply` **signals** refresh |

`CombatRosterScreenShell.Apply` → `CombatHudView.ApplyCombatRosterPresentation` → `RefreshRosterChrome()` from **live combat**, not DTO highlight fields.

**Rule:** Do **not** drive **input-sensitive** chrome (targeting, focus, picking mode) from `bridge.Current*` until publish order is guaranteed on every gameplay event. Safe to map **display-only** fields (labels, HP bars) from DTO when stale-by-one-frame is acceptable.

```csharp
// ❌ BAD — stale targeting on OnTargetingChanged
void OnTargetingChanged() =>
    CombatRosterPresentationApplier.ApplyHighlightsAndStats(
        party, enemy, UiPresentationBridge.Instance!.CurrentCombatRoster);

// ✅ GOOD — live combat authority
void OnTargetingChanged() => RefreshTargetHighlights(); // reads m_combat.ValidTargets
```

**Tests:** `CombatRosterPresentationApplierTests` (DTO → USS contract); manual F3 Attack → enemy `--targetable` + click `SelectTarget`.

---

## Hybrid refresh — do not gate formation bind on the bus

**Symptom:** Roster plates **empty** after bus migration; wrapper visible, no slot content.

**Cause:** `if (UiPresentationBridge.Instance != null) return` around **`RefreshRosters()`** — HUD assumed shell/applier would bind from bus, but applier only runs when shell receives `Apply`, and early publishes had `Visible == false` (see **phase order** below).

**Fix:** **Never** skip formation bind when the bridge exists. Bus path adds shell + projector; HUD still calls `RefreshRosters()` from `BattleState` on queue rebuild, formation change, and combat enter.

**Rule:** `UiPresentationBridge.Instance != null` may gate **duplicate chrome refresh**, not **formation bind**.

---

## Double chrome refresh (HUD + shell)

**Symptom:** Redundant work; future risk if one path uses DTO and the other uses live combat.

**Cause:** `CombatController` events wired on **both** phase HUD (`RefreshRosterChrome`) **and** projector → `PresentationShellHost` → shell `Apply` → same `RefreshRosterChrome`.

**Fix (shipped #314):** HUD handlers call `RefreshRosterChromeIfNotOnBus()` — no-op when bus + active shell own chrome. Shell `Apply` remains the bus entry for chrome. **Fallback:** if bridge exists but `PresentationShellHost.ActiveCombatRoster == null` (stale scene), HUD still refreshes directly.

**Rule:** One chrome authority per concern when bus is wired; keep formation bind on HUD regardless.

---

## Projector wire lifecycle — not UIView `OnDisable`

**Symptom:** Roster bus stops publishing after combat HUD disable/re-enable; `CurrentCombatRoster` stale for shell-only consumers.

**Cause:** `CombatHudView.OnDisable` called `CombatRosterProjector.Unwire()` on the **bridge singleton**. Command rail projectors are **not** unwired from phase views.

**Fix (shipped #314):** `UiPresentationBridge.Wire(GameState)` subscribes `PhaseChanged` → `SyncCombatRosterWire()` — wire on `GamePhase.Combat`, unwire on exit. Remove wire/unwire from phase HUD `OnDisable`.

**Rule:** Projector **Wire/Unwire** follows **game phase** or bridge bootstrap — not individual `UIDocument` enable cycles.

---

## Phase order — `PhaseChanged` before `OnEnter`, builder `Visible`

**Symptom:** First bus publish has `Visible == false` and empty slot lists; shells no-op; plates missing until a later event.

**Cause (layered):**

| Trap | What goes wrong |
|------|-----------------|
| **`GamePhaseController` order** | `PhaseChanged` fires **before** `CombatPhaseController.OnEnter` → `StartBattle` |
| **Builder gate** | `CombatRosterPresentationBuilder` sets `Visible = phase == Combat && combat != null && CurrentPhase != Idle` |
| **Early wire** | Projector wired at combat phase flip while `CurrentPhase` still **Idle** |

**Mitigations (shipped #314):**

1. HUD **`RefreshRosters()`** on combat events — not only on bus `Apply`.
2. **`BeginCommandPlanning()` before `RebuildQueue()`** in `BeginTurnPhase` so queue rebuild publishes while planning highlight is valid (command-target acting id).
3. Bootstrap **`BootstrapRosterChrome()`** on HUD `OnEnable` when already in combat.

**Rule:** Treat first bus snapshot after phase enter as **untrusted** for slot content until `StartBattle` / queue rebuild has run.

---

## Scene shell vs catalog `shellPrefab: null`

**Symptom:** Bus publishes; no roster chrome update on bus path; warning in console on Play Mode.

**Cause:** `CombatRoster` catalog row uses **`shellPrefab: null`** + **`usePhaseFilter: Combat`** — intentional **scene-instance** shell (`CombatRosterScreenShell` on `CombatHud` GO). Stale scenes missing that component: `PresentationShellHost` has no `ICombatRosterShell`, bus path silent.

**Fix:**

1. Regenerate **GridDungeon → Scenes → Create Dev Bootstrap** (adds `CombatRosterScreenShell`).
2. `PresentationShellHost` logs warning when combat roster surface resolves with no scene shell and no prefab.
3. HUD fallback when `ActiveCombatRoster == null` (see **double chrome refresh**).

**Rule:** Document per-surface whether the shell is **catalog prefab** or **scene component** in bootstrap checklist ([presentation shell implementation § Recipe B](presentation-shell-implementation.md#recipe-b--new-surface-eg-second-chrome-block)).

| Surface | Shell delivery |
|---------|----------------|
| `CommandRail` | Catalog prefab (+ optional scene instance) |
| `CommandRailInfo` | Scene `CommandRailInfoScreenShell` |
| `CombatRoster` | Scene `CombatRosterScreenShell` on `CombatHud` |
| `SynchroBar` | Scene `SynchroBarScreenShell` on `CombatHud` |
| `ItemListInventory` | Centralized presenter + `ItemListInventoryScreenShell` |

---

## Shell `Apply` before HUD chrome ready

**Symptom:** First bus publish after combat start does not update targeting chrome; works after second event.

**Cause:** `ApplyCombatRosterPresentation` returned early when `!m_rosterChromeReady`; `Wire` / bridge publish could run before HUD finished `OnEnable` slot setup.

**Fix:** Set `m_rosterChromeReady = true` **after** party/enemy roster views and click handlers exist; call `BootstrapRosterChrome()` once at end of `OnEnable` when mid-combat.

**Rule:** Shell `Apply` must tolerate late HUD init **or** HUD must set ready flag before any catch-up `Apply(bridge.Current*)`.

---

## Projector unwired — partial DTO reset

**Symptom:** After combat exit, `CurrentCombatRoster` still reports `IsSelectingTarget == true` or old acting ids while slots are empty.

**Cause:** `RebuildAndPublish` null-combat branch cleared slots + `FormationSignature` only — scalar highlight fields lingered on `m_state`.

**Fix (shipped #314):** `CombatRosterPresentationState.Clear()` — full scalar + list reset before publish when `m_combat == null`.

**Rule:** Unwire/empty publishes must reset **all** DTO fields consumers might read, not only collections.

---

## Edit Mode projector tests — `GameState` phase required

**Symptom:** `CombatRosterPresentationProjectorTests` fail or assert contradictions (`Visible == false` but `PartySlots.Count > 0`).

**Cause:** `projector.Wire(combat, gameState: null)` → builder uses `GamePhase.Hub` → early return with empty/invisible state. `ActingPartyBeat` never fires without `ActingPartyCombatantId`.

**Fix:** Test helper pins `GamePhase.Combat` on a `GameState` with `GamePhaseController` via private field (same pattern as `ExplorationMapCoordinatorTests`):

```csharp
var phases = new GamePhaseController();
SetPrivateField(phases, "m_current", GamePhase.Combat);
SetPrivateField(gameState, "m_phases", phases);
```

**Rule:** Projector integration tests need **`GameState.Current`** aligned with builder gates — passing `GamePhase` only to `Build()` is not enough for `Wire()`.

---

## `Apply` before shell `Awake` (lazy init)

**Symptom:** Null refs first frame in shell `Apply`; works on second publish.

**Cause:** `PresentationShellHost.ApplyCurrentBridgeSnapshots` or bridge catch-up calls `Apply` before shell `Awake` cached its HUD reference.

**Fix:** Call `PresentationShellHostRef.Ensure(ref m_host, this)` in `Awake` and `PresentationShellHostRef.Require(ref m_host, this)` on every shell entry point (`Apply`, public getters, `PlayBeat`) — see `Assets/Scripts/UI/Views/PresentationShellHostRef.cs`. Do not inline `??= GetComponent<T>()` or silently no-op in `Apply` while getters throw.

**Rule:** Shell `Apply` must not assume `Awake`/`OnEnable` order relative to first bus publish. New `*ScreenShell` types must use `PresentationShellHostRef`; skip only shells with no co-located host component (e.g. `CommandRailWorldRigShell`).

---

## Anti-pattern — `UsesBus` disables all HUD refresh

**Symptom:** Mixed empty plates, stale highlights, or duplicated fix layers after partial bus migration.

**Cause:** Single `UiPresentationBridge.Instance != null` flag branching **formation**, **stats**, **highlights**, and **wire lifecycle** together.

**Rule:** Split flags by concern:

| Concern | Bus present |
|---------|-------------|
| Formation bind | HUD always from `BattleState` |
| Interactive chrome | HUD live combat **or** shell `Apply` trigger — not stale DTO |
| Projector wire | Bridge + phase lifecycle |
| Stats on action beat | HUD/reactive presenter; optional DTO sync later |

---

## Missing `using` on new type refs

Presentation shell files are a frequent source of this trap (new projector/builder/shell `.cs` under `Runtime/Presentation/`). **General rule:** [unity-common-pitfalls.mdc](../../.cursor/rules/unity-common-pitfalls.mdc) § Handoff — missing `using`; handoff step in `format-before-handoff-and-commit.mdc`.

---

## Documentation map

| Topic | Doc |
|-------|-----|
| Shell recipe, catalog, checklist | [presentation-shell-implementation.md](presentation-shell-implementation.md) |
| Cursor rule (agent gate) | [presentation-shell.mdc](../../.cursor/rules/presentation-shell.mdc) |
| Bus contract, surfaces | [ui-event-contract § Presentation bus](ui-event-contract.md#presentation-bus) |
| Modal PopIn / `IsSettling` traps | [centralized-ui-gotchas.md](centralized-ui-gotchas.md) |
| Combat roster custom UI | [custom-party-ui.md](custom-party-ui.md) |
| ADR | [042 — presentation bus](../../decisions/042-presentation-bus.md) |

---

## Changelog

| Date | Note |
|------|------|
| 2026-06-23 | § Dual-write — CommandRailInfo bus-first + `ApplyPresentationShell` (Shop rail info flash) |
| 2026-06-23 | Party section rail — `PartySectionRailPresenter.ApplyMenuPresentationShell`; thin shell |
| 2026-06-23 | CommandRail menu shell — `CommandRailPresenter.ApplyPresentationShell`; thin `CommandRailScreenShell` |
| 2026-06-18 | Initial page from combat roster shell ship ([#314](https://github.com/miramocha/griddungeon-game/issues/314)) |
| 2026-06-19 | § Missing `using` — pointer to general `unity-common-pitfalls` handoff rule ([#315](https://github.com/miramocha/griddungeon-game/issues/315)) |
