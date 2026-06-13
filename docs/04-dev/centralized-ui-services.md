# Centralized UI services (UITK)

How Grid Dungeon hosts **screen-wide overlays** that outlive a single phase HUD — global input hints, the shared party formation floater, screen fade, and similar `UIDocument` roots. Use this when adding a new cross-phase panel or when deciding whether chrome belongs in `ExplorationHud.uxml` vs its own scene object.

**Implementation repo:** [griddungeon-game](https://github.com/miramocha/griddungeon-game) — `Assets/Scripts/Runtime/UI/`, `Assets/Scripts/UI/Views/`, `Assets/UI/Screens/Shared/`.

**Related:** [UI event contract](ui-event-contract.md) (events/commands, not layout), [shared menu & picker UI § Global input hints](shared-menu-picker-ui.md#global-input-hints), [custom party UI](custom-party-ui.md) (formation grid API), [layered UITK panels](layered-uitk-panels.md) (future HUD splits), [04 — Tech notes § UI reactivity](../04-tech-notes.md#ui-reactivity).

---

## Problem

Phase HUDs (`ExplorationHud`, `CombatHud`, `HubHud`) own most screen chrome. Some UI must:

- Appear in **more than one phase** (party strip in exploration and combat).
- Sit **above** phase HUD without being torn down on phase exit.
- Publish **one authoritative copy** (input binds) instead of duplicating footers on every modal.

**Centralized UI services** solve this with **one scene `GameObject` per concern**, its own `UIDocument`, and a fixed place in the `sortingOrder` stack.

```mermaid
flowchart TB
  subgraph phase [Phase HUD documents]
    CH[CombatHud sort 20]
    HH[HubHud sort 20]
  end

  subgraph shared [Centralized services]
    MM[MinimapPanel sort 0]
    EXP[ExpandedMap sort 100]
    PF[PartyFormationFloater sort 10 / 260]
    WH[WalletHudPresenter sort 27]
    PM[PartyMenuOverlay sort 250]
    IH[InputHintPresenter sort 300]
    SF[ScreenFadePresenter sort 10000]
  end

  MM --> PF
  EXP --> PF
  CH --> PF
  HH --> WH
  PM --> WH
  PM --> IH
  CH --> IH
  MM --> IH
  EXP --> IH
  SF -.->|fade beats| MM
```

Phase views **orchestrate** (show/hide, publish hint copy, bind data). They do **not** embed these trees in their UXML.

### Standalone document — no cross-`UIDocument` dock

A centralized service **owns one scene `GameObject` + `UIDocument` + root UXML**. Phase HUDs and overlays call the **facade** (`OpenBag`, `SetHubShopMode`, `CombatItemInput`, …). They do **not**:

- `CloneTree` the service UXML into hub / combat / party phase trees as the **shipped** integration
- Reparent service `VisualElement` nodes into another document’s host (embedded party-menu pane hosts, `InventoryPaneHost`, …)
- Sync layout with **`worldBound` / `GeometryChangedEvent`** to fake embedding across `UIDocument` roots

**When migrating** a panel that today lives inside a phase HUD (embedded clone or “docked” pane), the **final** implementation must move the tree to a centralized presenter and show it as a **full-screen transparent modal** (or other self-contained overlay chrome) at the service’s `sortingOrder`. Align beside fixed rails with **USS modifiers** (e.g. `tabbed-picker--rail-offset`, `left: 240px`) — not by parenting into the phase shell.

| OK | Not OK (reject in review / migration complete) |
|----|------------------------------------------------|
| `ItemListInventory.OpenBag` while party menu section = Inventory | Bag picker cloned into `PartyMenu` dialog panes |
| Hub shop modal at sort **200** via `ItemListInventory.SetHubShopMode` | `ItemListPicker.uxml` cloned on `HubHud` root |
| Combat item via `ItemListInventory.CombatItemInput` | Local `CombatItemPickerHost` + picker clone on `CombatHud` |
| `PartyFormationFloater.ApplyFormationDockState` / `ApplyPartyMenuFloaterDock` — **context** + sort on the **same** floater document | Reparenting floater grid nodes into `PartyMenu.uxml` |

Agent rule: [`centralized-ui-services.mdc`](../../.cursor/rules/centralized-ui-services.mdc).

---

## Pattern — Presenter + facade (+ `GameState` ref)

| Piece | Responsibility |
|-------|----------------|
| **`*Presenter`** inherits `CentralizedUiPresenterBase` (`MonoBehaviour`, `[RequireComponent(typeof(UIDocument))]`) | Owns `UIDocument`, clones UXML/USS, `sortingOrder`, slide/fade animation, context switching. Base provides `ICentralizedUiSurface` boilerplate (`RequestedVisible`, `IsShown`, `IsSettling`, `Show/Hide/HideImmediate`, `OnEnable`/`OnDisable` wiring). |
| **Static facade** extends `CentralizedUiFacade<TPresenter>` (optional, `GridDungeon.UI`) | `InputHints`, `PartyFormationFloater` — thin `Publish` / `SetRevealed` API so phase views avoid hunting components. Base provides `Register`/`Unregister`/`Resolve` + `ICentralizedUiSurface` delegation. |
| **`GameState` serialized ref** (optional, `GridDungeon.Runtime`) | `GameState.InputHint`, `GameState.ScreenFade` — composition root exposes long-lived presenters to Runtime and UI |
| **Phase `*View`** | Subscribes to events; calls facade or presenter; **clears** or **restores** on overlay close / phase exit |

```mermaid
flowchart LR
  subgraph ui [GridDungeon.UI]
    HV[HubHudView / CombatHudView / ExplorationMapCoordinator]
    FH[InputHints / PartyFormationFloater]
  end

  subgraph runtime [GridDungeon.Runtime]
    GS[GameState]
    IP[InputHintPresenter]
  end

  HV --> FH
  FH --> GS
  GS --> IP
  HV -->|direct| FH
```

**Rules**

1. **Runtime does not reference UITK views** — presenters live in Runtime (`InputHintPresenter`, `ScreenFadePresenter`) or UI (`PartyFormationFloaterPresenter`); phase logic stays in controllers.
2. **One publisher per strip** — e.g. only `CombatHudView.RefreshInputHint` owns combat bind copy while combat is idle; overlays call `InputHints.Publish` while open, then `Clear` or restore underlying hint on dismiss.
3. **BEM owns steady state; DOTween owns orchestrated motion** — USS modifiers declare end/layout pixels (`tabbed-picker--hidden`, `party-formation-floater--collapsed`, `command-rail__body--entering`, `input-hint__text--retracted`). Show/hide **animation** uses `UiToolkitTweens` + `UiTransitionSession` ([ADR 039](../../decisions/039-uitk-dotween-show-hide.md)); inline `style` only during tweens and for layout-derived coordinates (map markers). No `transition-duration` on those blocks.
4. **Shared `PanelSettings`** — `Assets/UI/Settings/GamePanelSettings.asset` on every `UIDocument` unless a panel needs a deliberate scale override ([04 — Tech notes](../04-tech-notes.md#combat-hud-ui-toolkit)).
5. **Standalone service document** — one `UIDocument` per concern; phase views orchestrate via facade only. **No** embedding clones in phase UXML and **no** cross-document dock / geometry sync as the shipped integration (see [Standalone document — no cross-`UIDocument` dock](#standalone-document--no-cross-uidocument-dock)).

---

## `sortingOrder` stack (MVP1)

Lower draws first. Values are **convention** — keep new panels in the gaps or extend upward.

| `sortingOrder` | Document | Owner |
|----------------|----------|--------|
| **0** | Exploration minimap (side panel) | `MinimapPanelView` |
| **10** | Party formation floater (exploration / combat) | `PartyFormationFloaterPresenter` |
| **20** | `CombatHud`, `HubHud` | `CombatHudView`, `HubHudView` |
| **25** | Global command rail (bookmark buttons) | `CommandRailPresenter` |
| **255** | Party menu section rail (same `CommandRail` document; raised while overlay open) | `CommandRailPresenter` via `SetPartyMenuRailVisible` |
| **26** | Global command-rail copy (header title, service blurbs, combat prompt) | `CommandRailInfoPresenter` |
| **27** | Global wallet strip (Credits balance) | `WalletHudPresenter` |
| **200** | Skill use picker (combat) + item-list modals (hub shop, combat item) | `SkillUsePickerPresenter`, `ItemListInventoryPresenter` (`HubShop`, `CombatItem`) |
| **100** | Exploration expanded map overlay | `ExpandedMapOverlayView` |
| **150** | Story modal | `StoryEventView` on `StoryHud` |
| **250** | Party menu overlay (hub + exploration pause) | `PartyMenuOverlayView` |
| **251** | Party bag modal + character detail (Formation / Equipment; rail offset) | `ItemListInventoryPresenter` (`PartyBag`), `CharacterDetailPresenter` |
| **260** | Party floater while formation edit docked | `PartyFormationFloaterPresenter` |
| **300** | Global input hint strip | `InputHintPresenter` |
| **10000** | Full-screen fade | `ScreenFadePresenter` |

**Layered HUD refactor (draft):** [ADR 037](../../decisions/037-layered-uitk-panels.md) splits monolith HUDs into more rows in this table; **global** `InputHintPresenter` stays unchanged.

---

## Shipped services

### Command-rail info — `CommandRailInfoPresenter` + `CommandRailInfo`

**Job:** Top-left **non-button copy** for the shared command rail — phase **header title** (`rail-info-header`), service headings/lines, combat targeting/planning prompts. Bookmark buttons stay on `CommandRailPresenter` (`sortingOrder` 25). **Credits** live on `WalletHudPresenter` (top-right).

| Type | Path | Notes |
|------|------|-------|
| Presenter | `Assets/Scripts/Runtime/UI/CommandRailInfoPresenter.cs` | `sortingOrder` **26**; `pickingMode = Ignore`; flush top-left (no outer margin) |
| Facade | `Assets/Scripts/UI/Views/CommandRailInfo.cs` | `SetHeaderTitle`, `SetServiceCopy`, `SetCombatPrompt`, `SyncVisibility`, `Clear` |
| UXML / USS | `Assets/UI/Screens/Shared/CommandRailInfo.uxml`, `CommandRailInfo.uss` | `name="rail-info"`; header block `rail-info-header` (phase-agnostic) |
| Bootstrap | `DevSceneComposition.WireCommandRailInfo` | Child of `GameState`; ref on `m_commandRailInfo` |

**Publishers:** `HubHudView.RefreshCredits` (header title only), `HubHudServicePanelView.Populate`, `CommandPanelView.ShowForCombatant`; visibility synced from `CommandRailPresenter.ApplyVisualContext` (hidden during exploration, party-menu rail, hub-leave transition).

---

### Global command rail — `CommandRailPresenter` + `CommandPanelModalSupport`

**Job:** One **vertical bookmark rail** (`CommandRail.uxml` → `command-rail-panel` / `CommandRail.PanelHost`) shared by hub root menu, hub service actions, combat command bar, and party menu section rail. Phase owners **populate** the panel in code (`CommandRailPanelBuilder` + `RailMenuPresenter`); they do not each own a duplicate rail document.

| Type | Path | Notes |
|------|------|-------|
| Presenter | `Assets/Scripts/UI/Views/CommandRailPresenter.cs` | `sortingOrder` **25** (phase) / **255** (party menu); context: `Hub` / `Combat` / `PartyMenu` / `Hidden` |
| Facade | `Assets/Scripts/UI/Views/CommandRail.cs` | `PanelHost`, `Body`, `SetPartyMenuRailVisible`, `SyncPhaseOwnership` |
| Modal chrome helper | `Assets/Scripts/UI/Views/CommandPanelModalSupport.cs` | Shared **sibling-chip disable** + panel BEM cleanup on the **same** `PanelHost` |
| UXML / USS | `Assets/UI/Screens/Shared/CommandRail.uxml`, `CommandPanel.uss`, `RailMenu.uss` | `command-panel--disabled`, `command-panel--modal-open`, `command-panel--protocol-only` |

**Who populates `PanelHost`**

| Phase / overlay | Owner | When |
|-----------------|-------|------|
| Hub root | `HubRootMenuPanel.Populate` | Hub bind + `RestoreCommandRailPanel` after party menu |
| Hub service (Buy/Sell/Back) | `HubHudServicePanelView` | Shop / guild / inn panels |
| Combat commands | `CommandPanelView.EnsureBuilt` | Combat phase |
| Party menu sections | `PartyMenuOverlayView.PopulateSectionRail` | Tab / Esc overlay open |

**Modal rail sibling disable**

While a **modal child** owns input (picker open, target select, combat log, party pane engaged), non-owner rail chips are `SetEnabled(false)` so W/S does not move focus on siblings. The **active owner** chip keeps `rail-menu__item--selected` and full opacity (`CommandPanel.uss` + `RailMenu.uss` `:disabled` hover suppression).

| Consumer | Modal-open signal | Active owner |
|----------|-------------------|--------------|
| `CommandPanelView` | Skill/item picker, target select, log modal | Command slot that opened the modal (`PendingTargetCommand` for targeting) |
| `HubHudView` | Hub shop buy/sell picker open | Buy or Sell service button (`ItemListInventory.HubMode`) |
| `PartyMenuOverlayView` | Section pane **engaged** (not merely revealed) | Active section chip (`PartyMenuSectionRailFocusRules`) |

Helpers: `CommandPanelModalSupport.SetModalOpen`, `SetEnabledForModal` / `ResolveEnabled`.

**Panel chrome reset (shared host)**

Combat teardown must not leave `command-panel--disabled` on the shared host — hub/party buttons inherit the modifier and look dim. **`CommandPanelModalSupport.ResetPanelChrome`** clears `command-panel--modal-open`, `command-panel--disabled`, and `command-panel--protocol-only`.

| When | Who calls `ResetPanelChrome` |
|------|------------------------------|
| Battle end / null combat actor | `CommandPanelView.ShowForCombatant(null, …)` early return |
| Leave combat context | `CommandRailPresenter.ResolveAndApplyContext` |
| Hub root repopulate | `HubRootMenuPanel.Populate` |
| Party section rail build | `PartyMenuOverlayView.PopulateSectionRail` |

Picker / modal integration detail: [shared menu & picker UI § Modal rail sibling disable](shared-menu-picker-ui.md#modal-rail-sibling-disable-commandpanelmodalsupport).

---

### Wallet HUD — `WalletHudPresenter` + `WalletHud`

**Job:** Top-right **Credits balance** — visible during hub Shop, party inventory pane, and brief transient pulses when balance changes elsewhere (hospital spend, dev grant, future battle loot).

| Type | Path | Notes |
|------|------|-------|
| Presenter | `Assets/Scripts/Runtime/UI/WalletHudPresenter.cs` | `sortingOrder` **27**; `pickingMode = Ignore`; balance lerp + slide in/out |
| Facade | `Assets/Scripts/UI/Views/WalletHud.cs` | `SetReason`, `SyncFromSave`, `NotifyBalanceChanged` |
| UXML / USS | `Assets/UI/Screens/Shared/WalletHud.uxml`, `WalletHud.uss` | `name="wallet-hud"`, `name="wallet-hud-amount"` |
| Bootstrap | `DevSceneComposition.WireWalletHud` | Child of `GameState`; ref on `m_walletHud` |

**Publishers:**

| Context | Owner |
|---------|--------|
| Hub Shop open/close | `HubHudView.OpenServicePanel` / `CloseServicePanel*` |
| Party inventory pane | `PartyMenuOverlayView.SyncWalletHudInventoryReason` |
| Balance delta (transient if hidden) | `HubHudView.RunServiceAction`, `DevPlayModeActions.DevGrantCredits` |

```csharp
WalletHud.SetReason(m_gameState, WalletHudReason.Shop, active: true);
WalletHud.SyncFromSave(m_gameState, animate: false);
WalletHud.NotifyBalanceChanged(m_gameState); // lerp; transient pulse when no Shop/Inventory reason
```

---

### Global input hints — `InputHintPresenter` + `InputHints`

**Job:** Bottom-right **input bind copy only** (`Z Confirm · X Cancel · W/S Command`). Not map legend, HP, quest text, or tutorial body copy.

| Type | Path | Notes |
|------|------|-------|
| Presenter | `Assets/Scripts/Runtime/UI/InputHintPresenter.cs` | `sortingOrder` **300**; `pickingMode = Ignore` |
| Facade | `Assets/Scripts/UI/Views/InputHints.cs` | `Publish(gameState, text)` / `Clear(gameState)` |
| Copy constants | `Assets/Scripts/UI/Views/TabbedPickerRailHints.cs` | Segment order: Z/X → W/S & Q/E → other keys |
| UXML / USS | `Assets/UI/Screens/Shared/InputHint.uxml`, `InputHint.uss` | `name="input-hint"`, `name="input-hint-text"` |
| Bootstrap | `DevSceneComposition.WireInputHint` | Child of `GameState`; ref on `m_inputHint` |

**Publishers (extend this list — do not add a second strip):**

| Phase / overlay | Owner method |
|-----------------|--------------|
| Hub | `HubHudView.RefreshInputHint` / `RestoreInputHint` |
| Combat | `CombatHudView.RefreshInputHint` / `RestoreInputHint` |
| Exploration map | `ExplorationMapCoordinator.RefreshGlobalInputHint` |
| Party menu / pause | `PartyMenuOverlayView.RefreshMenuHint` |
| Story modal | `StoryEventView` → `TabbedPickerRailHints.ModalDismiss` |
| Victory rewards | `BattleRewardScreenView` on show; clear on dismiss |
| Floor transition | `FloorTransitionPresenter` clears on start; map/hub republish on `PresentationReleased` |
| Story end / pause close | `InputRouter.RestoreGlobalInputHintForPhase` |

Full bind table: [shared menu & picker UI § Global input hints](shared-menu-picker-ui.md#global-input-hints). Agent rule: `unity-global-input-hints.mdc`.

```csharp
// Typical publish while a modal owns binds
InputHints.Publish(m_gameState, TabbedPickerRailHints.CombatCommand);

// On dismiss — restore phase hint or clear
InputHints.Clear(m_gameState);
m_combatHud.RestoreInputHint();
```

---

### Party formation floater — `PartyFormationFloaterPresenter` + `PartyFormationFloater`

**Job:** One **party formation grid** shared by exploration strip, combat roster (center column), and formation-edit dock in party menu. Enemy roster stays on `CombatRosterView` inside `CombatHud` ([custom party UI](custom-party-ui.md)).

| Type | Path | Notes |
|------|------|-------|
| Presenter | `Assets/Scripts/UI/Views/PartyFormationFloaterPresenter.cs` | Context machine: `Exploration` / `Combat` / `FormationEdit` / `Hidden` |
| View helper | `Assets/Scripts/UI/Views/PartyFormationFloaterView.cs` | Collapse / `RevealWithDip` animation |
| Facade | `Assets/Scripts/UI/Views/PartyFormationFloater.cs` | `Grid`, `ExplorationSync`, `ApplyFormationDockState`, `ApplyPartyMenuFloaterDock`, `SetCombatSlotClickHandler` |
| Grid | `PartyFormationGridView` + `PartyFormationGrid.uxml` | 8 fixed slots; BEM `party-formation-slot` |
| UXML / USS | `PartyFormationFloater.uxml`, `PartyFormationFloater.uss` | Mount: `party-formation-mount` |
| Bootstrap | `DevSceneComposition.WirePartyFormationFloater` | Sibling `PartyFormationFloater` GO, not under `ExplorationHud` |

**Context ownership**

| Context | `sortingOrder` | Who drives visibility |
|---------|----------------|------------------------|
| Exploration strip | 10 | `ExplorationHudView` → `PartyFormationFloater.SetRevealed`; map fullscreen collapses strip |
| Combat roster | 10 | `CombatHudView` binds highlights / slot clicks via `PartyFormationFloater.Grid` |
| Formation edit | 260 | `PartyMenuOverlayView` → `ApplyPartyMenuFloaterDock(docked: true, formationEdit: true)` |
| Party menu equipment | 260 | `PartyMenuOverlayView` → `ApplyPartyMenuFloaterDock(docked: true, formationEdit: false)` — member focus on floater; clear on section exit (`PartyEquipmentFloaterToolkitView.ClearMemberFocus`) |
| Hidden | — | Phase not exploration/combat and no party-menu dock |

Phase changes flow through `PartyFormationFloater.SyncPhaseOwnership(GamePhase)` (subscribed inside presenter). **Formation bind copy** uses global `InputHints`, not labels on the floater.

```csharp
// Exploration: show strip after phase enter
PartyFormationFloater.SetRevealed(true);

// Combat: wire slot clicks for targeting
PartyFormationFloater.SetCombatSlotClickHandler(OnRosterSlotClicked);
var grid = PartyFormationFloater.Grid;
grid?.SetActingHighlight(actor);

// Party menu formation pane
PartyFormationFloater.ApplyPartyMenuFloaterDock(docked: true, formationEdit: true);

// Party menu equipment pane (floater only — no formation swap chrome)
PartyFormationFloater.ApplyPartyMenuFloaterDock(docked: true, formationEdit: false);
```

Integrator detail (replace grid, events, combat chrome): [custom party UI](custom-party-ui.md).

---

### Skill use picker — `SkillUsePickerPresenter` + `SkillUsePickerOverlay`

**Job:** Combat **Skill** command tabbed overlay — one scene-wide document instead of `CloneTree` on `CombatHud`.

| Type | Path | Notes |
|------|------|-------|
| Presenter | `Assets/Scripts/UI/Views/SkillUsePickerPresenter.cs` | `sortingOrder` **200**; combat phase only |
| Facade | `Assets/Scripts/UI/Views/SkillUsePickerOverlay.cs` | `Input` (`ICombatSkillPickerInput?`), `TabCount`, `OpenStateChanged` |
| UXML / USS | `Assets/UI/Screens/Combat/SkillUsePicker.uxml`, `SkillUsePicker.uss` | `ui:Instance` → `ItemListPickerShell` |
| Host | `CombatSkillPickerHost` + `CombatSkillListPickerAdapter` | Wired inside presenter |
| Bootstrap | `DevSceneComposition.WireSkillUsePicker` | Child of `GameState` |

**Publishers:** `CombatHudView` reads `SkillUsePickerOverlay.Input` for `CommandPanelView`; `InputRouter` routes combat skill binds through the facade. Hide + ignore input when phase ≠ Combat.

---

### Item list inventory — `ItemListInventoryPresenter` + `ItemListInventory`

**Job:** One presenter, **three mutually exclusive contexts** — hub shop, combat item, and party bag — each a **full-screen transparent modal** on this service’s `UIDocument` (never embedded in hub / combat / party menu UXML).

| Type | Path | Notes |
|------|------|-------|
| Presenter | `Assets/Scripts/UI/Views/ItemListInventoryPresenter.cs` | Context machine: `HubShop` / `CombatItem` / `PartyBag` / `Hidden` |
| Facade | `Assets/Scripts/UI/Views/ItemListInventory.cs` | Hub shop, combat item input, bag open/close |
| UXML / USS | `Assets/UI/Screens/Shared/ItemListInventoryOverlay.uxml`, `ItemListInventoryOverlay.uss` | `item-list-inventory-overlay` + `tabbed-picker--modal-centered` + `tabbed-picker--rail-offset` (`left: 240px`); single `ItemListPickerShell` host |
| Bootstrap | `DevSceneComposition.WireItemListInventory` | Child of `GameState` |

**Modal chrome (all contexts)**

| Piece | USS / behavior |
|-------|----------------|
| Overlay root | Full-screen bleed (`left/right/top/bottom: 0`) on service document |
| Panel | Centered `tabbed-picker__panel`; transparent host (no dim) |
| Rail inset | `tabbed-picker--rail-offset` — **240px** left (command / section rail bookmark stays visible) |
| Party menu shell | Quit confirm only — bag UI lives on `ItemListInventory` at sort **251** |

**Context ownership**

| Context | `sortingOrder` | Who drives visibility |
|---------|----------------|------------------------|
| Hub shop buy/sell | 200 | `HubHudView` → `ItemListInventory.SetHubShopMode` / `HideHubShop` |
| Combat item pick | 200 | `CombatItemPickerHost` inside presenter; `CombatHudView` uses `ItemListInventory.CombatItemInput` |
| Party bag | 251 | `PartyMenuOverlayView` → `OpenBag` / `CloseBag` / `RefreshBag` when Inventory section active (above party menu at 250) |
| Hidden | — | Phase exit, overlay close, or context switch |

```csharp
// Hub shop
ItemListInventory.SetHubShopMode(HubShopMode.Buy, content, bag);

// Combat item — CommandPanelView uses facade input
var itemPicker = ItemListInventory.CombatItemInput;

// Party menu inventory section — modal on service document, not embedded pane
ItemListInventory.OpenBag(party.Inventory);
ItemListInventory.CloseBag();
```

Picker integration detail: [shared menu & picker UI § Item list inventory service](shared-menu-picker-ui.md#item-list-inventory-service).

Implementation traps (rapid cancel/reopen, animated hide vs context switch): [centralized UI gotchas § Pop-in exit vs rapid reopen](centralized-ui-gotchas.md#pop-in-exit-vs-rapid-reopen-itemlistpickerview).

---

### Character detail — `CharacterDetailPresenter` + `CharacterDetail`

**Job:** One **single-combatant inspect panel** (stats + optional worn equipment rows) for party menu **Formation** and **Equipment** sections. Separate `UIDocument` at sort **251** — same full-bleed + `tabbed-picker--rail-offset` modal chrome as party bag ([`ItemListInventoryOverlay.uxml`](https://github.com/miramocha/griddungeon-game/blob/main/Assets/UI/Screens/Shared/ItemListInventoryOverlay.uxml)). Not embedded in `PartyMenu.uxml`.

| Type | Path | Notes |
|------|------|-------|
| Presenter | `Assets/Scripts/UI/Views/CharacterDetailPresenter.cs` | Context: `Hidden` / `PartyMenuFormation` / `PartyMenuEquipment`; `sortingOrder` **251** when visible |
| View | `Assets/Scripts/UI/Views/CharacterDetailView.cs` | Toolkit bind API; slot engage via `MenuFocusNavigator` |
| Facade | `Assets/Scripts/UI/Views/CharacterDetail.cs` | `SetPartyMenuContext`, `Bind`, `Refresh`, `View`, `Hide` |
| UXML / USS | `CharacterDetailOverlay.uxml` (hosts `CharacterDetail.uxml` instance), `CharacterDetail.uss` | Two-layer overlay: outer full bleed + inner rail-offset centered panel |
| Bootstrap | `DevSceneComposition.WireCharacterDetail` | Child `CharacterDetail` GO under `GameState` |

**Publishers:** `PartyMenuOverlayView.ShowActivePaneContent` — Formation → `PartyFormationInspect`; Equipment → `PartyEquipDisplay`; Inventory / Quit / close → `Hide`. Member bind from `PartyFormationToolkitView` / `PartyEquipmentFloaterToolkitView`.

```csharp
CharacterDetail.SetPartyMenuContext(
    CharacterDetailContext.PartyMenuEquipment,
    CharacterDetailLayout.PartyEquipDisplay
);
CharacterDetail.Bind(subject);
CharacterDetail.Hide();
```

**Deferred:** equipment bag picker window on slot confirm; combat analyze host (third caller → optional `GameState` ref).

**Lifecycle:** [game#209](https://github.com/miramocha/griddungeon-game/issues/209) shipped — presenter implements `ICentralizedUiSurface` ([§ Presentation lifecycle](#presentation-lifecycle)).

---

### Exploration map — `ExplorationMapCoordinator`

**Job:** Exploration minimap (side panel) + expanded map overlay — shared `MapGridPaintController`, global input-hint publish. Two `UIDocument` presenters; coordinator owns event wiring and M-toggle choreography.

| Type | Path | Notes |
|------|------|-------|
| Coordinator | `Assets/Scripts/UI/Views/ExplorationMapCoordinator.cs` | Subscriptions, `ToggleExpandedFromInput`, hint publish, chrome visibility |
| Minimap | `Assets/Scripts/UI/Views/MinimapPanelView.cs` | `ICentralizedUiSurface`; `sortingOrder` **0**; `SlideTransition` (`map-minimap--retracted` on slide shell) |
| Expanded | `Assets/Scripts/UI/Views/ExpandedMapOverlayView.cs` | `UniformScaleTransition` (`map-expanded--hidden`, `map-expanded-scale--expanded`); `sortingOrder` **100** |
| Paint | `Assets/Scripts/UI/MapGridPaintController.cs` | Shared grid paint + marker sync across surfaces |
| USS | `MapView.uss` (shared grid), `MinimapPanel.uss`, `ExpandedMapPanel.uss` | Trees built in C# via `MapGridHostBuilder` |
| Orchestrator | `Assets/Scripts/UI/Views/ExplorationHudView.cs` | Party strip hides when expanded open |
| Bootstrap | `DevSceneComposition.WireExplorationMap` | `ExplorationMap` GO → `MinimapPanel` + `ExpandedMapOverlay` children |

**M-toggle (MSK-style):** expanded `UniformScaleTransition` / `ScaleInPresentationDriver.Show()`; minimap `SlideTransition.Hide()` → `map-minimap--retracted` on slide shell (not dimmed/faded).

**Publishers:** `ExplorationMapCoordinator.RefreshGlobalInputHint` / `ClearGlobalInputHint`. Party strip: `ExplorationHudView` → `ExpandedChanged`.

**Visibility:** Coordinator `SyncMapChromeVisibility` → minimap slide retract when expanded opens or chrome suppressed; hub / non-exploration: `HideImmediate()`.

```csharp
m_mapCoordinator.ToggleExpandedFromInput();
m_mapCoordinator.RefreshGlobalInputHint();
```

Legacy `MapView` shim delegates to coordinator until scenes refresh. **Do not** embed map chrome in `ExplorationHud.uxml`.

---

### Screen fade — `ScreenFadePresenter` (no static facade)

**Job:** Full-screen opaque/translucent overlay for floor transitions and other beats.

| Type | Path | Notes |
|------|------|-------|
| Presenter | `Assets/Scripts/Runtime/UI/ScreenFadePresenter.cs` | `sortingOrder` **10000** |
| Access | `GameState.ScreenFade` | `FadeOut` / `FadeIn` / `SetOpaque` / `SetTransparent` |
| Bootstrap | Wired on `GameState` with `FloorTransitionPresenter` | See `DevSceneComposition.WireFloorTransition` |

Callers hold a `GameState` reference; there is no `ScreenFades.Publish` facade — fade is **imperative** and short-lived.

---

### Other scene-wide documents (same family, different API)

These use the **multi-`UIDocument` bootstrap** pattern but are **phase/modal-specific** rather than a static facade:

| Document | Sort | Role |
|----------|------|------|
| `PartyMenuOverlay` | 250 | Hub party menu + exploration pause shell |
| `StoryHud` | 150 | Story event modal |
| `FloorTransitionPresenter` | (uses fade + vignette) | Stairs transition; clears global hints on start |

Treat them as **overlays** with their own `*View` lifecycle, not as generic “services.” Only add a `PartyFormationFloater`-style facade when **three or more** unrelated callers need the same panel.

---

## Scene graph (Dev Bootstrap)

`GridDungeon → Scenes → Create Dev Bootstrap` creates siblings under `GameState`:

```
GameState
├── InputHint          (InputHintPresenter)
├── CommandRailInfo    (CommandRailInfoPresenter)
├── WalletHud          (WalletHudPresenter)
├── ScreenFade         (ScreenFadePresenter)
├── PartyFormationFloater (PartyFormationFloaterPresenter)
├── SkillUsePicker (SkillUsePickerPresenter)
├── ItemListInventory (ItemListInventoryPresenter)
├── CharacterDetail (CharacterDetailPresenter)
├── ExplorationMap (ExplorationMapCoordinator)
│   ├── MinimapPanel (MinimapPanelView)
│   └── ExpandedMapOverlay (ExpandedMapOverlayView)
├── ExplorationHud (ExplorationHudView — orchestrator only)
├── CombatHud
├── HubHud
├── PartyMenuOverlay
└── StoryHud
```

Wiring: `Assets/Scripts/Editor/DevBootstrapSceneCreator.cs`, `DevSceneComposition.cs`. After clone, run **Create Dev Bootstrap** if console reports missing floater or hint refs.

---

## Adding a new centralized service

Use this checklist when a panel must survive phase changes or serve multiple HUDs:

1. **Name the concern** — one reason to change (hints, party strip, fade). Do not merge unrelated chrome.
2. **New `GameObject` + `UIDocument`** under `GameState` (or documented sibling), UXML in `Assets/UI/Screens/Shared/` if cross-phase.
3. **Pick `sortingOrder`** from the table above; document the value in the presenter constant.
4. **Inherit `CentralizedUiPresenterBase`** ([#229](https://github.com/miramocha/griddungeon-game/issues/229)) — do **not** re-implement `ICentralizedUiSurface` boilerplate directly. Required shape:
   - `Awake` / first domain call → `EnsureOverlay()`: build UXML, assign `m_document.panelSettings` + `sortingOrder`, cache `Q()` refs, create `m_presentation` (step 5), call `WirePresentationSubscription()`.
   - `OnEnable` → `WirePresentationSubscription()` (safe to call again after domain-side `EnsureOverlay`).
   - `OnDisable` → `TeardownPresentationSubscription()` + `HideImmediate()`.
   - Override abstract `Show()` / `Hide()` / `HideImmediate()` — delegate to `m_presentation` + sync visuals.
   - Non-interactive strips: `root.pickingMode = PickingMode.Ignore`.
5. **Pick a presentation driver** — set `m_presentation` inside `EnsureOverlay`:

| Driver | Factory | When to use |
|--------|---------|-------------|
| **PopIn** | `CentralizedUiPresentation.CreatePopIn(root)` | Full-screen modal pickers, character detail, skill picker |
| **Slide** | `CentralizedUiPresentation.CreateSlide(panel, retractedClass)` | Strips that retract off-screen (wallet HUD, input hint) |
| **Collapse** | `CentralizedUiPresentation.CreateCollapse(root)` | Floaters that collapse / dip in place (party formation) |
| Custom | `new CentralizedUiPresentation(root, myDriver)` | Specialised only (e.g. rail-enter on `CommandRail`) — internal; document choice in service row |

6. **Facade (optional)** — static access without serialized refs ([#230](https://github.com/miramocha/griddungeon-game/issues/230)). Hold `static readonly CentralizedUiFacade<TPresenter> s_facade = new(debugName: "MyService")`; expose thin `Register`/`Unregister` (called from presenter `OnEnable`/`OnDisable`); delegate `RequestedVisible`, `IsShown`, `IsSettling`, `Show`/`Hide`/`HideImmediate`, and `PresentationChanged` to `s_facade`; domain calls via `s_facade.Resolve()?.Method()`. **Not applicable** to `GameState`-forwarding variants (`InputHints`, `WalletHud` resolve through a `GameState` reference instead).
7. **`GameState` field (optional)** — when Runtime systems must drive the panel (`ScreenFade`, `InputHint`).
8. **Wire bootstrap** — `DevSceneComposition.Wire…` + menu item so clones stay consistent.
9. **Ownership doc** — list which views publish/clear; add row to [Global input hints](shared-menu-picker-ui.md#global-input-hints) publishers table if it touches bind copy.
10. **Tests** — Edit Mode under `Assets/Tests/UI/` for sort order, visibility, hint publish/clear (see existing `InputHint` / floater fixtures).

### Code skeleton — presenter

```csharp
namespace GridDungeon.Runtime.UI
{
    [RequireComponent(typeof(UIDocument))]
    public sealed class MyOverlayPresenter : CentralizedUiPresenterBase
    {
        const int k_SortOrder = 200; // pick from sortingOrder table

        [SerializeField] PanelSettings m_panelSettings = null!;
        [SerializeField] VisualTreeAsset m_layout = null!;

        UIDocument m_document = null!;
        bool m_overlayBuilt;

        void Awake() => EnsureOverlay();

        void OnEnable()
        {
            MyOverlay.Register(this);   // omit if no facade / GameState-forwarding only
            WirePresentationSubscription();
        }

        void OnDisable()
        {
            MyOverlay.Unregister(this);
            TeardownPresentationSubscription();
            HideImmediate();
        }

        public override void Show()
        {
            EnsureOverlay();
            m_presentation?.Show();
        }

        public override void Hide() => m_presentation?.Hide();

        public override void HideImmediate() => m_presentation?.HideImmediate();

        void EnsureOverlay()
        {
            if (m_overlayBuilt)
            {
                return;
            }

            m_document = GetComponent<UIDocument>();
            m_document.panelSettings = m_panelSettings;
            m_document.sortingOrder = k_SortOrder;

            var root = m_document.rootVisualElement;
            m_layout.CloneTree(root);
            // cache root.Q<Label>("my-label") etc. here

            // swap CreatePopIn → CreateSlide / CreateCollapse per step 5
            m_presentation = CentralizedUiPresentation.CreatePopIn(root);
            WirePresentationSubscription();
            m_overlayBuilt = true;
        }
    }
}
```

### Code skeleton — facade

```csharp
namespace GridDungeon.UI.Views
{
    /// <summary>Static access to the scene-wide <see cref="MyOverlayPresenter"/>.</summary>
    public static class MyOverlay
    {
        static readonly CentralizedUiFacade<MyOverlayPresenter> s_facade = new(
            debugName: "MyOverlay"
        );

        public static void Register(MyOverlayPresenter p) => s_facade.Register(p);

        public static void Unregister(MyOverlayPresenter p) => s_facade.Unregister(p);

        public static bool RequestedVisible => s_facade.RequestedVisible;

        public static bool IsShown => s_facade.IsShown;

        public static bool IsSettling => s_facade.IsSettling;

        public static event Action? PresentationChanged
        {
            add => s_facade.PresentationChanged += value;
            remove => s_facade.PresentationChanged -= value;
        }

        // domain calls — add service-specific methods below
        public static void Open(/* context args */) => s_facade.Resolve()?.Open(/* args */);

        public static void Show() => s_facade.Show();

        public static void Hide() => s_facade.Hide();

        public static void HideImmediate() => s_facade.HideImmediate();
    }
}
```

**Do not**

- Embed a second copy of the panel inside phase UXML "for convenience."
- **Dock** or reparent the service tree into another `UIDocument` host, or ship `worldBound` geometry sync as the integration — use modal + `sortingOrder` + rail-offset USS instead.
- Duplicate bind footers on modals when `InputHints` already covers the context.
- Put gameplay rules or `CombatController` logic inside presenters.

**Migrating an embedded picker into this pattern**

1. Add or extend a centralized presenter + facade under `GameState` bootstrap.
2. Move picker UXML to the service overlay (`Assets/UI/Screens/Shared/`).
3. Replace phase `CloneTree` / local presenter with facade calls only.
4. Leave phase hosts empty if the shell still needs a section hook (e.g. party inventory pane).
5. Verify grep: no `CloneTree(ItemListPicker` on phase HUDs; no embedded bag panes in `PartyMenu`; no `Dock*` APIs on the facade.

---

## Presentation lifecycle

**Status:** Contract shipped (#207); abstract base `CentralizedUiPresenterBase` + generic `CentralizedUiFacade<T>` shipped ([#229](https://github.com/miramocha/griddungeon-game/issues/229), [#230](https://github.com/miramocha/griddungeon-game/issues/230)). **All** centralized services in [Scene graph](#scene-graph-dev-bootstrap) must inherit `CentralizedUiPresenterBase` on the presenter (migration tracked on [game#206](https://github.com/miramocha/griddungeon-game/issues/206)).

**Epic:** [griddungeon-game#206](https://github.com/miramocha/griddungeon-game/issues/206) — transition-agnostic show/hide for centralized UITK services (PopIn modals, slide strips, collapse floaters).  
**ADR:** [038 — Centralized UI presentation lifecycle](../../decisions/038-centralized-ui-presentation-lifecycle.md) · [039 — UITK show/hide via DOTween](../../decisions/039-uitk-dotween-show-hide.md)  
**Issue index:** [github-drafts/centralized-ui-lifecycle-issues.md](github-drafts/centralized-ui-lifecycle-issues.md).

### Mandatory rule (new + migrated services)

Every **centralized UI service** (`GameState` child with its own `UIDocument` listed in [Shipped services](#shipped-services) or [Scene graph](#scene-graph-dev-bootstrap)) **must**:

1. Inherit **`CentralizedUiPresenterBase`** on the presenter (satisfies `ICentralizedUiSurface`; base owns `CentralizedUiPresentation` + `IPresentationDriver` delegation).
2. Expose **`RequestedVisible`**, **`IsShown`**, **`IsSettling`** on the static facade when one exists — not domain-only flags that imply visibility (`IsVisible`, `IsOpen`, context ≠ hidden).
3. Route **phase exit**, **context enum swap**, and **competing overlay** teardown through **`HideImmediate()`**.
4. Keep **visual driver names internal** — PopIn, slide, collapse, USS classes stay out of public facades.

**Documented exceptions (no `ICentralizedUiSurface` required):**

| Service | Why |
|---------|-----|
| `ScreenFadePresenter` | Beat-driven opaque/transparent; imperative `FadeOut`/`FadeIn` on `GameState.ScreenFade` — not authority-toggled chrome |
| Phase HUDs (`HubHud`, `CombatHud`, `ExplorationHud`) | Not centralized services — phase-owned documents |

Passive copy rails (`CommandRailInfoPresenter`) should still implement the interface where visibility toggles exist; use immediate `Hide` when there is no settle animation.

### Problem (pre-#207)

PopIn-style centralized services each reimplemented show/hide flags (`IsActive`, `IsClosing`, deferred `schedule.Execute`, …). [#207](https://github.com/miramocha/griddungeon-game/issues/207) shipped `ICentralizedUiSurface` + `CentralizedUiPresentation`. [#229](https://github.com/miramocha/griddungeon-game/issues/229) extracted `CentralizedUiPresenterBase` to eliminate repeated boilerplate across all 8 presenters; [#230](https://github.com/miramocha/griddungeon-game/issues/230) extracted `CentralizedUiFacade<T>` for the 6 static facades. **`ItemListInventory` / `ItemListPickerView`** remains the **reference consumer**; **`CharacterDetail`** ([#209](https://github.com/miramocha/griddungeon-game/issues/209)) is the second fixed PopIn consumer. Remaining traps (rapid reopen, context swap, domain flags vs `IsShown`): [centralized UI gotchas](centralized-ui-gotchas.md).

### Public contract (transition-agnostic)

Facades and presenters expose **intent and presentation state** — not PopIn, slide, collapse, or USS names.

| Member | Meaning |
|--------|---------|
| `RequestedVisible` | Authority wants the panel open (context ≠ hidden) |
| `IsShown` | Panel presented for current authority — stays **true through exit settle** until dismiss animation completes |
| `IsSettling` | Animated dismiss (or chained dismiss) in flight after `Hide()` — `Show()` clears; use instead of legacy `IsClosing` |
| `Show()` | Request on-screen presentation |
| `Hide()` | Same-authority dismiss (may settle) |
| `HideImmediate()` | Authority change — phase exit, context enum swap, competing overlay — cancel deferred callbacks |

```csharp
// Shipped: GridDungeon.UI — ICentralizedUiSurface.cs (game#207)
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

**Do not** put `PlayEnter`, `IsClosing`, `PopIn`, or animation duration on this interface. Visual drivers (`IPresentationDriver`, e.g. PopIn vs collapse) stay **internal** to each presenter.

### Lifecycle rules

| Call | When |
|------|------|
| `Hide()` | Player dismiss; same context authority |
| `HideImmediate()` | Phase leave, `SetContext` swap, another overlay at same sort takes focus |
| `SetContext(Hidden)` | System → `HideImmediate()` |
| `SetContext(open)` | `HideImmediate()` if leaving another open context, then `Show()` |
| Data refresh while settling | `Show` path — not refresh-only while `IsSettling` |

### Animation stack (DOTween)

**Shipped:** [game PR #240](https://github.com/miramocha/griddungeon-game/pull/240) · **ADR:** [039](../../decisions/039-uitk-dotween-show-hide.md)

| Type | Path | Role |
|------|------|------|
| `UiToolkitTweens` | `Assets/Scripts/Runtime/UI/UiToolkitTweens.cs` | DOTween helpers for `VisualElement.style` (opacity, translate, scale, width/height) |
| `UiTransitionSession` | `Assets/Scripts/Runtime/UI/UiTransitionSession.cs` | Per-target generation; `Begin` bumps **before** kill; `KillWithoutCompleting` on detach |
| `BemMotionCompletion` | `Assets/Scripts/Runtime/UI/BemMotionCompletion.cs` | Steady BEM **then** `ClearMotionStyles` on tween complete / reset — [implementation guide](uitk-bem-transition-guide.md#bemmotioncompletion) |
| `VisualPresentationSync` | `Assets/Scripts/Runtime/UI/VisualPresentationSync.cs` | Presenter show/hide gates from steady hidden class + `IsSettling` — [implementation guide](uitk-bem-transition-guide.md#visualpresentationsync) |
| Transition helpers | same folder + `MapViewPanelTransition` | `PopInTransition`, `SlideTransition`, `CollapseTransition`, `FadeTransition`, `CommandRailEnterTransition` |

**Rules:** One duration source in C# constants. Toggle BEM modifiers for **steady** visibility; tween inline `style` during motion; `StyleKeyword.Null` on complete. Map marker opacity uses a **separate DOTween target** so step `Kill` does not cancel fade-in ([`MapMarkerVisibility`](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/UI/MapMarkerVisibility.cs)).

**Detached hosts:** `CentralizedUiPresentation.Hide` → `HideDetached` when animation target has no `panel` (instant dismiss for Edit Mode clones). Panel-attached services still animate `Hide()`.

### Internal drivers (`IPresentationDriver`)

| Driver | Animation family | Used by |
|--------|------------------|---------|
| `PopInPresentationDriver` | Pop-in scale (`PopInTransition`, 420ms) | `ItemListPickerView`, `CharacterDetailPresenter`, `SkillUsePicker` |
| `CollapsePresentationDriver` | Dip / slide (`CollapseTransition`, 260ms; `--collapsed` authority) | `PartyFormationFloater` ([#214](https://github.com/miramocha/griddungeon-game/issues/214)) |
| `SlidePresentationDriver` | Retract translate (`SlideTransition`) | `WalletHud`, `InputHint` ([#215](https://github.com/miramocha/griddungeon-game/issues/215), [#216](https://github.com/miramocha/griddungeon-game/issues/216)) |
| `ScaleInPresentationDriver` | Uniform scale (`UniformScaleTransition`) | `ExpandedMapOverlayView` ([#244](https://github.com/miramocha/griddungeon-game/pull/244)) |
| `FadePresentationDriver` | Opacity fade (`FadeTransition`, 280ms; `map-view--faded` authority) | Legacy map fade paths; marker fade helpers |
| `RailEnterPresentationDriver` (internal) | Opacity + translate enter (`CommandRailEnterTransition`; `--entering` on body) | `CommandRail` ([#217](https://github.com/miramocha/griddungeon-game/issues/217)) |
| `InstantPresentationDriver` | BEM `--hidden` only | Detached / test hosts without `panel` (see [gotchas § Edit Mode tests](centralized-ui-gotchas.md#edit-mode-tests-without-a-panel)) |

Drivers are **internal** to `GridDungeon.Runtime.UI`; facades and presenters expose only `ICentralizedUiSurface` vocabulary.

### Service migration status (MVP1)

Synced to game repo as of [#207](https://github.com/miramocha/griddungeon-game/issues/207)–[#217](https://github.com/miramocha/griddungeon-game/issues/217) implementation. Open tracker: [game#206](https://github.com/miramocha/griddungeon-game/issues/206).

| Service | `ICentralizedUiSurface` | Driver | Issue |
|---------|-------------------------|--------|-------|
| `ItemListPickerView` / `ItemListInventory` | Presenter + view + facade ✅ | PopIn | [#207](https://github.com/miramocha/griddungeon-game/issues/207), [#213](https://github.com/miramocha/griddungeon-game/issues/213) |
| `CharacterDetail` | Presenter + facade ✅ | PopIn | [#209](https://github.com/miramocha/griddungeon-game/issues/209) |
| `SkillUsePicker` | Presenter + facade ✅ | PopIn | [#212](https://github.com/miramocha/griddungeon-game/issues/212) |
| `PartyFormationFloater` | Presenter ✅ | Collapse | [#214](https://github.com/miramocha/griddungeon-game/issues/214) |
| `WalletHud` | Presenter + facade ✅ | Slide | [#215](https://github.com/miramocha/griddungeon-game/issues/215) |
| `InputHint` | Presenter + facade ✅ | Slide | [#216](https://github.com/miramocha/griddungeon-game/issues/216) |
| `CommandRail` | Presenter + facade ✅ | Rail enter | [#217](https://github.com/miramocha/griddungeon-game/issues/217) |
| `CommandRailInfo` | Presenter ✅ (immediate root dismiss; copy block swaps animated) | `RailInfoCopyTransition` (slide+fade / fade) | [#217](https://github.com/miramocha/griddungeon-game/issues/217) |
| `MinimapPanelView` | Presenter ✅ | Slide retract (`map-minimap--retracted`) | [#244](https://github.com/miramocha/griddungeon-game/pull/244) |
| `ExpandedMapOverlayView` | Presenter ✅ | `ScaleInPresentationDriver` + `UniformScaleTransition` | [#244](https://github.com/miramocha/griddungeon-game/pull/244) |
| `ExplorationMapCoordinator` | Orchestration (events, M-toggle, hints) | Coordinates minimap slide + expanded scale | [#244](https://github.com/miramocha/griddungeon-game/pull/244) |
| `PartyMenuOverlayView` | Orchestration only — calls service facades | — | [#208](https://github.com/miramocha/griddungeon-game/issues/208) |
| `ScreenFade` | Exception (imperative fade) | Opacity | — |

---

## Documentation map

| Topic | Authoritative doc |
|-------|-------------------|
| **This pattern** (presenter, sort stack, bootstrap) | **Here** |
| **Presentation lifecycle** (shipped API, migration index) | **Here § Presentation lifecycle** + [ADR 038](../../decisions/038-centralized-ui-presentation-lifecycle.md) + [ADR 039](../../decisions/039-uitk-dotween-show-hide.md) |
| BEM transition helpers (`BemMotionCompletion`, `VisualPresentationSync`) | [UITK BEM transition guide](uitk-bem-transition-guide.md) |
| Implementation gotchas (exit races, flags, map fade vs screen fade, review traps) | [centralized UI gotchas](centralized-ui-gotchas.md) |
| Command rail population, modal sibling disable, hub shop row nav | [shared menu & picker UI § Rail menu](shared-menu-picker-ui.md#rail-menu--chips-and-command-buttons) |
| Input hint copy table + picker policy | [shared menu & picker UI § Global input hints](shared-menu-picker-ui.md#global-input-hints) |
| Party grid API, combat highlights, replace strategies | [custom party UI](custom-party-ui.md) |
| Runtime events for custom HUD | [UI event contract](ui-event-contract.md) |
| Splitting monolith HUD into more documents | [layered UITK panels](layered-uitk-panels.md) |
| Input bind design (player-facing) | [input bindings § Global input hints](../02-systems/input-bindings.md#global-input-hints) |
