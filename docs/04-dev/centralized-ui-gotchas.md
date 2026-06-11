# Centralized UI — implementation gotchas

Living list of **non-obvious bugs and review traps** when wiring cross-phase UITK services (`ItemListInventory`, `InputHints`, `CommandRail`, `PartyFormationFloater`, …). For the happy-path pattern, see [centralized UI services](centralized-ui-services.md). For picker APIs and rail focus, see [shared menu & picker UI](shared-menu-picker-ui.md).

**Implementation repo:** [griddungeon-game](https://github.com/miramocha/griddungeon-game) — `Assets/Scripts/UI/Views/`, `Assets/Scripts/Runtime/UI/`.

---

## How to use this doc

| When | Action |
|------|--------|
| Hit a weird modal / picker bug | Search here before adding guards in phase HUDs |
| Adding a new centralized overlay with show/hide animation | Read **Pop-in exit vs reopen** and **Context switches** |
| Reviewing a migration off embedded pickers | Cross-check **Standalone document** + **Modal rail chrome leak** |
| Closed a related bug | Add a short entry (symptom → cause → fix → test) in the same PR or follow-up |

---

## Pop-in exit vs rapid reopen (`ItemListPickerView`)

**Symptom:** Hub → Shop → Buy → **X** → spam **Buy** again — buy list never appears (or flashes then vanishes).

**Cause:** `ItemListPickerView.Hide()` runs a **~420ms** `PopInTransition` exit (`PopInTransition.DurationMs`). During that window:

- `IsActive` stays **true** until the exit callback runs.
- `IsClosing` is **true**.
- A naive reopen that calls **`Refresh`** (because `IsActive`) only updates row data — it does **not** cancel the exit or re-show the shell.
- When the stale exit callback eventually runs, it calls `CompleteHide`, applies the hidden USS class, and fires the hide callback (`SetContext(Hidden)`, `m_hubMode = Hub`).

`Show()` during exit **is** safe for animation: it bumps `PopInTransition` generation and clears `m_isClosing`, which suppresses the stale exit callback. The bug is taking the **Refresh** path while closing.

**Fix (shipped):**

- `ItemListPickerView.Refresh` — if `m_isClosing`, delegate to `Show`.
- `ItemListInventoryPresenter.SetHubShopMode` — use `Refresh` only when `IsActive && !IsClosing`; otherwise `Show`.

**Test:** `ItemListInventoryPresenterTests.SetHubShopMode_RapidReopenAfterCancel_StaysActiveAfterExitAnimation`.

**Rule for new hosts:** Any code that reopens a pop-in picker while an exit may still be running must call **`Show`**, not **`Refresh`**, unless you have explicitly confirmed `!IsClosing`. Treat `IsActive` alone as insufficient.

```csharp
// ❌ BAD — reopen during exit animation
if (m_picker.IsActive)
    m_picker.Refresh(model);
else
    m_picker.Show(model);

// ✅ GOOD
if (m_picker.IsActive && !m_picker.IsClosing)
    m_picker.Refresh(model);
else
    m_picker.Show(model);
```

**Same class of bug elsewhere:** Any overlay using `PopInTransition.PlayExit` + deferred `onHidden` (party menu shell, character detail, wallet slide, input hint retract) can race if the host reopens before exit completes. Prefer **`Show` / reopen entry points** that reset closing state, or **`ForceHideImmediate`** when switching authority (phase/context), not `Refresh`-style data-only updates.

---

## `IsActive` ≠ on-screen ≠ modal-open signal

| Flag | Meaning | Trap |
|------|---------|------|
| `ItemListPickerView.IsActive` | Presentation model loaded; exit not finished | Still **true** during exit animation |
| `ItemListPickerView.IsClosing` | `Hide()` started, exit not complete | **true** during the 420ms window |
| `ItemListInventory.IsHubShopActive` | `context == HubShop` **and** `picker.IsActive` | Can stay true briefly after **X** until exit completes |
| Visible to player | Hidden USS class off **and** pop-in expanded | Requires `Show` path, not mid-exit `Refresh` |

Hub shop modal rail disable (`CommandPanelModalSupport`) and input hints key off `IsHubShopActive` / `HubMode` — rapid cancel+reopen can leave rail/hint state wrong if hide callbacks run after a reopen. The pop-in reopen fix above is the primary guard; phase owners should still **`RefreshInputHint` / `RebuildServiceFocus`** after shop mode changes.

---

## Context switches must not use animated hide

**Symptom:** Left combat with item picker mid-close; hub shop opens invisible, or bag + shop contexts fight.

**Cause:** `ItemListInventoryPresenter` owns **one** `ItemListPickerView` across `HubShop` / `CombatItem` / `PartyBag` / `Hidden`. Animated `Hide()` callbacks can fire **after** the next context already called `Show`.

**Fix pattern (shipped):** `ForceHideForContextSwitch` / `HideHubShopInternal(immediate: true)` / `ItemListPickerView.ForceHideImmediate()` — skip exit animation, clear `m_isClosing`, do not rely on deferred callbacks when **authority** changes (phase leave, context enum swap).

**Rule:** Animated hide is for **player dismiss** within the same context. **System dismiss** (phase exit, service close, switch HubShop → PartyBag) uses **immediate** hide.

---

## `PopInTransition` generation cancels stale schedules

`PopInTransition` tracks a per-target **generation**. `PlayEnter` / `Reset` bump generation and pause pending scheduled exit callbacks. A new `Show()` during exit therefore **should not** run the old exit `onComplete` — unless the host never called `Show` and only called `Refresh`.

Documented in `PopInTransition.cs`; do not bypass with hand-rolled delays. If you add a new animated overlay, reuse `PopInTransition` (or the same generation pattern), not ad-hoc `schedule.Execute` without invalidation.

---

## Shared `CommandRail.PanelHost` — chrome leaks

**Symptom:** Hub service buttons look dim/disabled after combat; party rail chips stuck muted.

**Cause:** `command-panel--disabled` / `command-panel--modal-open` left on the **shared** rail host when combat or a modal ends without reset.

**Fix:** `CommandPanelModalSupport.ResetPanelChrome` on combat teardown, hub root repopulate, party section rail build. See [centralized UI services § Panel chrome reset](centralized-ui-services.md#global-command-rail--commandrailpresenter--commandpanelmodalsupport).

---

## Global input hints — publish / clear stack

**Symptom:** Wrong bind line after closing shop, party menu, or story modal; duplicate footers if someone adds a `Label` on the panel.

**Cause:** Overlays publish to `InputHints` while open; underlying phase hint not restored on dismiss, or two publishers active.

**Rules:**

- One strip (`InputHintPresenter`, sort **300**). Constants in `TabbedPickerRailHints`.
- Overlay **publish** on open, **clear** or **restore** phase hint on close (`HubHudView.RestoreInputHint`, `MapView.RefreshGlobalInputHint`, …).
- Non-bind copy (tutorial, save warning) stays on modal body — not the global strip. See [global input hints rule](../../.cursor/rules/unity-global-input-hints.mdc).

---

## Standalone `UIDocument` — no geometry dock

**Symptom:** Bag panel drifts when resolution changes; picker clipped under wrong parent; double input hit targets.

**Cause:** `CloneTree` of service UXML into phase HUD, or `worldBound` / `GeometryChangedEvent` sync across two `UIDocument` roots.

**Rule:** Phase views call facades (`ItemListInventory.OpenBag`, `SetHubShopMode`, …). Modal position comes from **USS** (`tabbed-picker--rail-offset`, full-bleed overlay), not reparenting. Review smell table: [centralized-ui-services.mdc](../../.cursor/rules/centralized-ui-services.mdc).

---

## `ItemListInventory` — one picker, three contexts

Only one context active at a time. Opening bag while shop modal logic still thinks it owns the picker causes focus/picking-mode bugs.

| Context | Sort | Typical owner |
|---------|------|----------------|
| `HubShop` | 200 | `HubHudView` |
| `CombatItem` | 200 | `CombatHudView` / `CommandPanelView` |
| `PartyBag` | 251 | `PartyMenuOverlayView` |
| `Hidden` | — | Phase exit, explicit hide |

`SyncPickingMode` enables host hits when combat item is open **or** picker is **`IsClosing`** (keeps hits coherent through exit). New contexts should follow the same immediate-hide-on-switch rule.

---

## Edit Mode tests without a panel

**Symptom:** Picker tests pass in isolation but Play Mode still breaks on rapid cancel.

**Cause:** `ItemListPickerView` tests that clone UXML **without** a live `panel` run `PopInTransition.PlayExit` **synchronously** (`panel == null` → immediate `onComplete`). Exit-animation races **do not reproduce** unless the host is under a `UIDocument` with `PanelSettings` (see `ItemListInventoryPresenterTests.CreatePresenter`).

**Rule:** Any bug involving animated hide/show needs at least one test with a **real panel** or an explicit `IsClosing` regression test on the presenter path.

---

## Documentation map

| Topic | Doc |
|-------|-----|
| Service pattern, sort stack, bootstrap | [centralized-ui-services.md](centralized-ui-services.md) |
| Picker layout, rail focus, cancel layering | [shared-menu-picker-ui.md](shared-menu-picker-ui.md) |
| Agent review smells (embed/dock) | [centralized-ui-services.mdc](../../.cursor/rules/centralized-ui-services.mdc) |
| **Gotchas (this page)** | **Here** |
