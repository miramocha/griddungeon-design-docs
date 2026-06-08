# Shared menu & picker UI (UITK)

How **rail menus**, **item list pickers**, and **skill use pickers** share UITK building blocks in [griddungeon-game](https://github.com/miramocha/griddungeon-game). Use this when skinning hub/combat/party chrome, adding a new tabbed modal, or deciding whether to extend an existing view vs fork.

**Related:** [ADR 026 — Combat menu focus navigation](../../decisions/026-combat-menu-focus-navigation.md) (`MenuFocusNavigator`, `menu-item--focused`), [ADR 035 — Skill use picker](../../decisions/035-skill-use-picker.md), [ADR 036 — Party inventory model](../../decisions/036-party-inventory-model.md), [custom skill picker UI](custom-skill-picker-ui.md), [UI event contract](ui-event-contract.md).

**Shipped ([#185](https://github.com/miramocha/griddungeon-game/issues/185)):** `WindowedListPaneView` (8-row windowing + `IListFocusNavigator`), unified `ItemListPickerView` / `RailMenuPresenter` across hub shop, party bag, and combat item picker; tabbed overlays use a **transparent** full-screen host (no modal dim).

**Implementation root:** `Assets/Scripts/UI/Views/` · `Assets/UI/Navigation/` · `Assets/UI/Screens/Shared/` · feature UXML under `Assets/UI/Screens/{Combat,Hub}/`.

---

## Overview — three families, one focus stack

Grid Dungeon does **not** use one mega-widget for every menu. MVP1 has three **families** that **compose** shared primitives:

| Family | Primary types | Orientation | Typical use |
|--------|---------------|-------------|-------------|
| **Rail menu** | `RailMenuPresenter` → `RailMenuView` or `MenuFocusNavigator` | Vertical **or** horizontal | Command bar, hub services, party section rail, **category tab chips** |
| **Item list picker** | `ItemListPickerView` (+ thin adapters) | Horizontal tabs + windowed rows | Hub shop buy/sell, party bag, combat **Item** command |
| **Skill use picker** | `SkillUsePickerToolkitView` | Horizontal tabs + windowed rows | Combat **Skill** command (ADR 035) |

All keyboard lists share **`MenuFocusNavigator`** ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md)) and, for long lists, **`WindowedListPaneView`** (8 visible rows + scroll bars).

```mermaid
flowchart TB
  subgraph focus [Focus layer ADR 026]
    MFN[MenuFocusNavigator]
    MFC[MenuFocusClasses.menu-item--focused]
    MFN --> MFC
  end

  subgraph rail [Rail menu family]
    RMP[RailMenuPresenter]
    RMV[RailMenuView chip DOM]
    RMP --> RMV
    RMP --> MFN
  end

  subgraph tabs [Horizontal tabs in pickers]
    PTS[PickerTabStripView]
    PTS --> RMP
  end

  subgraph lists [Row lists in pickers]
    WLP[WindowedListPaneView]
    WLP --> MFN
  end

  subgraph itemPicker [Item list picker]
    ILP[ItemListPickerView]
    ILRB[ItemListRowBuilder]
    ILP --> PTS
    ILP --> WLP
    ILP --> ILRB
  end

  subgraph skillPicker [Skill use picker]
    SUP[SkillUsePickerToolkitView]
    SUP --> PTS
    SUP --> WLP
    SUP --> skillRows[skill-picker__row built in view]
  end

  subgraph consumers [Screens]
    CMD[CommandPanelView combat rail]
    HUB[HubHudView root + service rails]
    PARTY[PartyMenuShellToolkitView section rail]
    SHOP[HubShopPickerPresenter]
    BAG[PartyInventoryBagView]
    CITEM[CombatItemListPickerAdapter]
    CSKILL[CombatSkillPickerHost]
  end

  RMP --> CMD
  RMP --> HUB
  RMP --> PARTY
  ILP --> SHOP
  ILP --> BAG
  ILP --> CITEM
  SUP --> CSKILL
```

---

## Focus navigation contract (`IListFocusNavigator`)

**Job:** One keyboard contract for **linear row lists** — command bar slots, picker rows, windowed panes, equipment slots.

| Type | Implements | Notes |
|------|------------|-------|
| `MenuFocusNavigator` | `IListFocusNavigator` | Flat list; toggles `menu-item--focused` on bound targets ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md)) |
| `WindowedListPaneView` | `IListFocusNavigator` | Owns inner `MenuFocusNavigator` on the **visible slice**; `FocusIndex` is **global** across the full list |
| `ItemListPickerView.RowNavigator` | → `WindowedListPaneView` | Hosts route WASD / confirm / cancel here when the pane is engaged |

**API surface:** `SetFocus`, `MoveNext` / `MovePrevious`, `Confirm`, `Cancel`, `ClearFocus`, `EngageFocus(preferredIndex)` — plus `HasFocus`, `FocusIndex`, and `Confirmed` / `Cancelled` / `FocusChanged` events.

**Engage vs immediate row focus** (`ItemListPickerInputMode`):

| Mode | Row focus when list opens | Typical hosts |
|------|---------------------------|---------------|
| **`Immediate`** | `WindowedListPaneView.SetItems(…, acquireFocus: true)` | Combat **Item** picker (`ItemListPickerView` default) |
| **`EngageOnConfirm`** | Rows render; focus stays on shell/rail until **Z** (`ConfirmOrEngage` → `EngagePane` / `EngageFocus`) | Hub shop (`HubShopPickerPresenter`), party bag (`PartyInventoryBagView`) |

`EngageOnConfirm` also registers row **click** → `EngagePaneAt(index)` so mouse can engage without keyboard.

**Disengage:** `ItemListPickerView.TryBackOut()` → `DisengagePane()` → `ClearFocus` on the row pane, clears detail text, raises `EngagementChanged`. Hosts peel UI layers on **X** / Back (see [Cancel / back layering](#cancel--back-layering-engageonconfirm-hosts) below).

---

## Rail menu — chips and command buttons

**Job:** One visual language for **selectable chips** (tabs) and **stacked actions** (command rail).

### Layering

```mermaid
flowchart TB
  subgraph presenter [RailMenuPresenter facade]
    API[BindFocusConfirmed / SetTabLabels / SetFocusItems / SetSelectedIndex]
  end

  subgraph horizontal [Horizontal mode]
  HRM[RailMenuView horizontal host]
  CHIPS[rail-menu__item VisualElement chips]
  SEL[rail-menu__item--selected]
  HRM --> CHIPS --> SEL
  end

  subgraph vertical [Vertical focus mode]
  BTN[Unity Button + command-panel__btn]
  CHIP[rail-menu__item on button]
  FOC[menu-item--focused via MenuFocusNavigator]
  BTN --> CHIP --> FOC
  end

  API --> HRM
  API --> MFN2[MenuFocusNavigator]
  MFN2 --> BTN
```

| Type | Factory | DOM | Selection vs focus |
|------|---------|-----|-------------------|
| **Horizontal chips** | `RailMenuPresenter.CreateHorizontal(host)` | `RailMenuView` builds `rail-menu__item` + `rail-menu__item-label` | **`--selected`** on active tab (Q/E or click) |
| **Vertical focus rail** | `RailMenuPresenter.CreateVerticalFocus()` | Existing UXML `Button`s; `ConfigureButton` adds `rail-menu__item` | **`menu-item--focused`** via `SetFocusItems`; optional **`--selected`** via `BindSelectionTargets` (party section) |

**Styles:** `Assets/UI/Screens/Shared/RailMenu.uss` (imported by `CommandPanel.uss` and `TabbedPicker.uss`). Unity `Button` rails need the combined selectors (e.g. `.rail-menu__item.unity-button.menu-item--focused`, `.rail-menu__item.unity-button.rail-menu__item--selected`).

### Vertical rail bookmark (focus poke)

Horizontal tab chips stay compact (`11px` / `26px` min-height). **Vertical** command rails use a fixed-width bookmark slide — not width animation.

| Token | Value | USS |
|-------|-------|-----|
| Rail column | `240px` | `.command-rail` |
| Item chip | `268px` | `.command-panel__btn` (poke = **28px**) |
| Unfocused | `translate: -28px 0` | Left edge off-screen; right edge flush with rail |
| Focused / `--selected` | `translate: 0` | Left at rail; right pokes into stage |
| Content inset | `padding-left: 28px` | Matches tuck — wrapped labels stay inside visible rail |

```
[ off-screen 28px ][ rail 240px ][ stage … ]
     unfocused ←──────────────┤
              focused ──────────────────┤→ poke
```

- **No `overflow: hidden`** on the rail — left tuck is clipped by the screen edge.
- **Combat pickers:** `.combat-hud > .tabbed-picker { left: 240px }` so the modal does not cover the rail bookmark.
- **Labels:** `RailMenuPresenter.ConfigureButton` migrates `Button.text` → child `rail-menu__item-label` so long names wrap with the chip (no fixed-width label hack).

### Consumers (vertical)

| Screen | Owner | UXML hook |
|--------|-------|-----------|
| Combat command bar | `CommandPanelView` | `CombatHud.uxml` → `command-panel__btn` |
| Hub root menu | `HubHudView` / `HubRootMenuFocus` | `HubHud.uxml` |
| Hub service back/actions | `HubHudServicePanelView` | per-service panel |
| Party section rail | `PartyMenuShellToolkitView` | `PartyMenu.uxml` → Inventory / Equipment |

### Consumers (horizontal)

| Screen | Owner | Notes |
|--------|-------|-------|
| Tab strips (all pickers) | `PickerTabStripView` | Thin wrapper over `CreateHorizontal` |
| Party equipment member tabs | `PartyEquipmentToolkitView` | `RailMenuPresenter.CreateHorizontal` on `party-equipment-members` |

**Extend:** New vertical rail → clone `command-rail` + `command-panel` from `RailMenuVertical.uxml`, wire `RailMenuPresenter.CreateVerticalFocus()`, bind `MenuFocusNavigator` in your input handler. New horizontal strip → empty host with class `tabbed-picker__tabs` (or `rail-menu rail-menu--horizontal`) and `PickerTabStripView`.

---

## Global input hints

**Status:** Shipped — replaces per-panel bind footers on command rail, hub, party menu, and tabbed pickers.

| Piece | Role |
|-------|------|
| `InputHintPresenter` | `MonoBehaviour` on `InputHint` child; `UIDocument` + `InputHint.uxml` / `InputHint.uss`; **`sortingOrder` 300** |
| `InputHints` | `Publish(gameState, text)` / `Clear(gameState)` — static facade to `GameState.InputHint` |
| `TabbedPickerRailHints` | Shared bind-copy strings for hub, combat, and party pickers |

**Publishers:** `CombatHudView.RefreshInputHint`, `HubHudView.RefreshInputHint`, `PartyMenuOverlayView.RefreshMenuHint` (equipment appends focused slot suffix via `PartyEquipmentToolkitView.MenuHintSlotSuffix`, e.g. `· Weapon`).

**Removed UXML hints:** `cmd-input-hint`, `hub-input-hint`, `party-menu-hint`, `tabbed-picker__hint`, `item-list-picker-hint`, `skill-picker-hint`, `party-equipment-detail` bind footer.

### `TabbedPickerRailHints` copy

| Constant / helper | Copy |
|-------------------|------|
| `HubRoot` | W/S Menu · Z Confirm · X Cancel |
| `HubService` | W/S Action · Z Confirm · X Back |
| `CombatIdle` | L Log · Z Confirm · X Cancel · Esc Pause |
| `CombatCommand` | L Log · W/S Command · Z Confirm · X Cancel · Esc Pause |
| `CombatTarget` | L Log · W/S Target · Z Confirm · X Cancel |
| `LogModal` | L or X Close |
| `ForItemPickerEngage(backVerb)` | Z Confirm · X {backVerb} |
| `ForItemPickerRows(multiTab, backVerb)` | Q/E Tab · W/S Row · Z Confirm · X {backVerb} — or W/S Row · … when single tab |

Party equipment (slots engaged): `Q/E Member · W/S Slots · Z Pick · X Back` + optional ` · {slot}` suffix.

---

## Tabbed picker shell — shared modal chrome

**Job:** Title, optional tabs, **side-by-side** list + detail (`tabbed-picker__body` row), windowed list region — **not** row content. Bind copy lives on **global** `InputHintPresenter`, not modal footers.

```mermaid
flowchart LR
  subgraph shell [TabbedPicker.uss BEM block tabbed-picker]
    T[tabbed-picker__title]
    TB[tabbed-picker__tabs → PickerTabStripView]
    subgraph body [tabbed-picker__body row]
      RW[tabbed-picker__rows → windowed-list]
      D[tabbed-picker__detail]
    end
  end

  T --- TB --- body
```

| Asset | Role |
|-------|------|
| `TabbedPicker.uss` | Panel layout; **transparent** full-screen host (`tabbed-picker { background-color: rgba(0,0,0,0) }` — **no modal dim**); imports `RailMenu.uss` |
| `WindowedList.uss` | `windowed-list`, `windowed-list__slots`, scroll bars |
| `TabbedPickerShellClasses` | BEM constants (`Hidden`, `TabsHidden`, …) |
| `PartyMenu.uss` | **Opaque** full-screen party shell (`rgb(20, 22, 26)`); imports `CommandPanel.uss` + `TabbedPicker.uss` for embedded bag/equipment panes |

**Overlay contrast:**

| Host | Root chrome | List panel |
|------|-------------|------------|
| Hub shop / combat pickers | `tabbed-picker` — transparent; stage/rail stay visible | `tabbed-picker__panel` — dim panel (`rgba(30, 34, 40, 0.97)`) |
| Party menu | `party-menu` — opaque full-screen | `party-menu__dialog` — shares panel metrics with `tabbed-picker__panel` |

Combat HUD offsets the picker overlay so the command rail bookmark stays visible: `.combat-hud > .tabbed-picker { left: 240px }` (`CombatHud.uss`).

**Panel layout:** `tabbed-picker__panel` and `party-menu__dialog` **shrink-wrap** content (`flex-grow: 0` — no fixed viewport-% height). **`tabbed-picker__body`** — horizontal row: windowed list (`flex-grow: 1`) + fixed-width detail column (`168px`). Fixed body height (`288px`) fits eight windowed rows + scroll chrome.

**UXML patterns:**

- **Full-screen overlay:** `tabbed-picker` root + `tabbed-picker__panel` — hub shop (`ItemListPicker.uxml`), combat skill/item pickers.
- **Embedded pane:** same inner structure without overlay root — party bag (`PartyInventory.uxml` inside `party-menu__dialog`).

---

## Item list picker — one view, multiple hosts

**Job:** Render **`ItemListPickerPresentationModel`** — tabs of **`ItemListRowModel`** rows. Catalog/build logic stays in Core/Runtime; view only builds DOM and fires selection.

```mermaid
flowchart TB
  subgraph data [Data builders Runtime / UI]
    HUB[HubShopStockCatalogBuilder]
    BAG[InventoryBagDisplayBuilder]
    COM[CombatItemListPresentationBuilder]
    MAP[InventoryBagPickerMapper]
  end

  subgraph model [Presentation]
    ILPM[ItemListPickerPresentationModel]
    ILRM[ItemListRowModel]
    ILPM --> ILRM
  end

  subgraph view [GridDungeon.UI.Views]
    ILPV[ItemListPickerView]
    LAY[ItemListPickerLayout element names]
    MODE[ItemListPickerInputMode]
    ILPV --> LAY
    ILPV --> MODE
  end

  subgraph adapters [Thin adapters]
    HSP[HubShopPickerPresenter]
    PIB[PartyInventoryBagView implements IInventoryBagView]
    CIA[CombatItemListPickerAdapter implements ICombatItemPickerView]
  end

  HUB --> ILPM
  BAG --> MAP --> ILPM
  COM --> ILPM
  ILPM --> ILPV
  ILPV --> HSP
  ILPV --> PIB
  ILPV --> CIA
```

### `ItemListPickerView` responsibilities

| Concern | Owner |
|---------|--------|
| Tab labels / selection | `PickerTabStripView` → `RailMenuPresenter` horizontal |
| Row window + focus | `WindowedListPaneView` |
| Row DOM | `ItemListRowBuilder` + `ItemListRow.uss` |
| Detail panel | `item-list-picker-detail` label text from `ItemListRowModel.Detail` |
| Confirm / cancel | `RowSelected` / `Cancelled` events |

### Layout profiles (`ItemListPickerLayout`)

Same C# view, different UXML **name hooks** and hidden class. Bind copy: global `InputHintPresenter` (`HubHudView`, `CombatHudView`, `PartyMenuOverlayView`) — not per-picker footer labels.

| Profile | `HiddenClass` | Used by |
|---------|---------------|---------|
| `ShopOverlay` (default) | `tabbed-picker--hidden` | `ItemListPicker.uxml` |
| `PartyInventoryPane` | `party-inventory--hidden` | `PartyInventory.uxml` |

Required element names (party profile uses the same ids):

- `item-list-picker-title`, `item-list-picker-tabs`, `item-list-picker-rows`, `item-list-picker-detail`

### Input modes (`ItemListPickerInputMode`)

| Mode | When | Row focus |
|------|------|-----------|
| **`Immediate`** | Combat **Item** picker | Acquired when `Show` rebuilds rows (`acquireFocus: true`) |
| **`EngageOnConfirm`** | Hub shop buy/sell, party bag pane | Rows visible; **Z** (`ConfirmOrEngage`) calls `EngagePane` / `EngageFocus`; shell or service rail owns focus until then |

**Hub shop:** `HubShopPickerPresenter` wires `EngageOnConfirm` and calls `ConfirmOrEngage()` when entering Buy/Sell so rows engage on open. While the picker is open but **not** pane-engaged, hub **service-rail** W/S is blocked; **Buy/Sell** chips stay **`--selected`** via `SyncShopActionSelectedIndex` (rail selection while picker open). When rows **are** engaged, `HubHudView.ActiveNavigator()` routes to `PickerRowNavigator` and clears service-rail focus items (selection chips still reflect Buy vs Sell).

**Party bag:** **`PartyInventoryBagView`** — implements `IInventoryBagView` + `IInventoryBagKeyboardView`, delegates to `ItemListPickerView` with `EngageOnConfirm`. First **Z** on Inventory may **reveal** the pane (`PartyMenuOverlayView`); second **Z** engages rows. Coordinator (`InventoryBagCoordinator`) unchanged.

### Cancel / back layering (`EngageOnConfirm` hosts)

Intended **two-step** peel — disengage row focus before closing the pane or exiting the screen:

```mermaid
flowchart TD
  subgraph party [Party menu — Inventory pane]
    P0[Section rail focus]
    P1[Pane revealed — rows idle]
    P2[Pane engaged — row focus]
    P0 -->|Z reveal| P1
    P1 -->|Z ConfirmOrEngage| P2
    P2 -->|X TryBackOut + HideActivePane| P0
    P1 -->|X HideActivePane| P0
    P0 -->|X Close| closed[Overlay closed]
  end

  subgraph hub [Hub shop — Buy/Sell]
    H0[Service rail — Buy/Sell/Back]
    H1[Picker open — rows idle]
    H2[Pane engaged — row focus]
    H0 -->|enter Buy/Sell| H1
    H1 -->|Z ConfirmOrEngage| H2
    H1 -->|auto on SetMode| H2
    H2 -->|X TryBackOut then SetShopMode Hub| H0
    H1 -->|X SetShopMode Hub| H0
  end
```

| Host | X / Back when rows **engaged** | X / Back when pane open, rows **idle** | X when pane hidden |
|------|-------------------------------|----------------------------------------|-------------------|
| **Party bag** | `TryBackOut` + `HideActivePane` → section rail | `HideActivePane` → section rail | Close entire party overlay |
| **Hub shop** | `TryBackOut` + `SetShopMode(Hub)` in one **X** → exit Buy/Sell | `SetShopMode(Hub)` → exit Buy/Sell | Close service panel (non-shop) |

Combat **Item** uses **`Immediate`** — **X** / Back closes the whole picker via `CombatPlayerCommandGate.TryBack` → `ICombatItemPickerHost.Cancel()` (no disengage step).

### Combat item picker — host integration

Combat reuses `ItemListPicker.uxml` + **`Immediate`** `ItemListPickerView` (default constructor).

```mermaid
flowchart LR
  CPV[CommandPanelView Item btn]
  HOST[CombatItemPickerHost Runtime]
  ADP[CombatItemListPickerAdapter]
  VIEW[ItemListPickerView Immediate]
  CC[CombatController SubmitPlayerAction]

  CPV -->|OpenForCommandActor| HOST
  HOST -->|Build rows CombatItemListCatalog| ADP
  ADP --> VIEW
  VIEW -->|RowSelected itemId| HOST
  HOST -->|Item command| CC
  CIH[CombatInputHandler] -->|WASD Z X Q E| HOST
```

| Piece | Role |
|-------|------|
| `CombatItemListPickerAdapter` | UITK view port — `Show`/`Hide`, row keyboard via `RowNavigator`; maps `RowSelected` → `itemId` |
| `CombatItemPickerHost` | Runtime orchestration — bag resolve, `CombatItemListCatalog`, `SubmitPlayerAction`, `OpenStateChanged` |
| `CombatHudView` | Clones `ItemListPicker.uxml`, wires adapter + host; exposes `ICombatItemPickerInput` to `CombatInputHandler` / `CommandPanelView` |
| `CombatItemListPresentationBuilder` | `CombatItemListRow[]` → `ItemListPickerPresentationModel` (single tab, tabs hidden in UI) |

**Row styles:** Always import `ItemListRow.uss` on the host UXML (party pane historically missed this and fell back to dark default label text).

---

## Skill use picker — parallel tabbed shell

**Job:** Render **`SkillPickerPresentationModel`** from Core (`SkillPickerCatalog`). Implements **`ISkillUsePickerView`** — swappable port ([ADR 035](../../decisions/035-skill-use-picker.md), [custom skill picker UI](custom-skill-picker-ui.md)).

```mermaid
flowchart LR
  CAT[SkillPickerCatalog Core]
  SPM[SkillPickerPresentationModel]
  SUP[SkillUsePickerToolkitView]
  HOST[CombatSkillPickerHost Runtime]

  CAT --> SPM --> SUP
  HOST --> SUP
```

### What is shared with item list picker

| Shared | Skill-specific |
|--------|----------------|
| `PickerTabStripView` + `RailMenu.uss` tabs | `SkillPickerPresentationModel` / `SkillPickerRowModel` |
| `WindowedListPaneView` + `WindowedList.uss` | Row DOM: `skill-picker__row` in `SkillUsePicker.uss` |
| `TabbedPicker.uss` shell | `CreateRowElement` inline in view (name, cost, disabled reason) |
| `MenuFocusNavigator` on rows | `ISkillUsePickerView` / `ICombatSkillPickerKeyboardView` ports |

**Not** using `ItemListPickerView` today — skill rows have a different column layout (MP cost, disabled reason) and a Runtime presentation type owned by ADR 035. A future refactor could introduce a generic `TabbedListPickerView<TRow>` or a row-builder delegate; MVP1 keeps **`SkillUsePickerToolkitView`** separate to avoid coupling item economy to combat skill catalog.

### UXML

`Assets/UI/Screens/Combat/SkillUsePicker.uxml` — same shell classes as shop picker; row host `skill-picker-rows` (class `windowed-list`).

---

## Windowed list pane (`WindowedListPaneView`)

**Job:** Fixed-height list region with **eight slot elements always allocated** (`DefaultVisibleRowCount = 8`). When `ItemCount > 8`, only a **window** of rows is mounted in slots; up/down scroll bars indicate off-window items; **global** `FocusIndex` is stable while the window slides.

Used by: `ItemListPickerView`, `SkillUsePickerToolkitView`, party equipment slot list, equipment sub-picker.

### Windowing model

| Concern | Behavior |
|---------|----------|
| Slot pool | Always **8** `windowed-list__slot` children under `windowed-list__slots` (empty slots stay in DOM) |
| Window start | `WindowStart` — first global index shown in slot 0 |
| Windowed mode | Root gets `windowed-list--windowed` when `ItemCount > visibleRowCount` |
| Focus slide | `MoveNext` / `MovePrevious` on global list; `EnsureWindowContainsFocus` repositions window before `SyncDom` |
| Short lists | `ItemCount ≤ 8` — all rows visible; scroll bars **hidden** (`windowed-list__scroll--hidden`), not collapsed |
| Row DOM | Row `VisualElement`s are **re-parented** into slot hosts on each sync (detach on clear) |

### Scroll bars

| Class | Meaning |
|-------|---------|
| `windowed-list__scroll--up` / `--down` | Bar chrome (always reserves space when not collapsed) |
| `windowed-list__scroll--hidden` | No more items above/below window — bar non-interactive |
| Click | `ScrollUp` / `ScrollDown` — shifts window by one row |

### Focus (`IListFocusNavigator`)

Inner `MenuFocusNavigator` runs on the **visible slice** only. `WindowedListPaneView` implements `IListFocusNavigator` and forwards `Confirm` / `Cancel` / `EngageFocus` / `ClearFocus`. `SetItems(…, acquireFocus: false)` supports `EngageOnConfirm` idle rows.

| Piece | Class / type |
|-------|----------------|
| Root | `windowed-list` |
| Slots column | `windowed-list__slots` → `windowed-list__slot` × 8 |
| Scroll hints | `windowed-list__scroll--up` / `--down` |
| Focus ring | `menu-item--focused` on row elements via inner navigator |

Inside party menu dialogs, `PartyMenu.uss` disables focus **scale** (`scale: 1 1`) so borders are not clipped by scroll/slot overflow.

---

## Consumer matrix

| Feature | Rail (vertical) | Tab strip | List view | Presentation builder | Runtime port |
|---------|-----------------|-----------|-----------|----------------------|--------------|
| Combat command bar | `CommandPanelView` | — | — | — | `CombatInputHandler` |
| Hub root / services | `HubHudView` | — | — | — | `HubInputHandler` |
| Hub shop buy/sell | — | `PickerTabStripView` | `ItemListPickerView` | `HubShopStockCatalogBuilder` | `HubShopPickerPresenter` |
| Party menu section | `PartyMenuShellToolkitView` | — | — | — | `PartyMenuInputHandler` |
| Party inventory | — | ✓ | `ItemListPickerView` via `PartyInventoryBagView` | `InventoryBagDisplayBuilder` → mapper | `IInventoryBagKeyboardView` |
| Party equipment members | — | `RailMenuPresenter` | slots + picker | `PartyEquipmentCatalog` | `IPartyEquipmentKeyboardView` |
| Combat Item | — | ✓ (single tab) | `ItemListPickerView` via adapter | `CombatItemListPresentationBuilder` | `ICombatItemPickerHost` |
| Combat Skill | — | ✓ | `SkillUsePickerToolkitView` | `SkillPickerCatalog` (Core) | `ICombatSkillPickerHost` |

---

## Extension guide

### New category-tabbed **item** modal

1. Build `ItemListPickerPresentationModel` (or use `ItemListPickerPresentationBuilder.FromCategoryTabs`).
2. Clone `ItemListPicker.uxml` or embed the inner panel in your screen.
3. `new ItemListPickerView(root)` (or custom `ItemListPickerLayout` if element names differ).
4. Wire keyboard: Q/E → `SelectNextTab` / `SelectPreviousTab`; WASD → `RowNavigator` or `MoveRowFocus*`; Z/X → confirm/cancel on `RowNavigator`.
5. Import styles: `TabbedPicker.uss`, `WindowedList.uss`, `ItemListRow.uss`.

### New **skill** or non-item row shape

- If rows match item columns (name, trailing meta, qty badge) → prefer **item list picker**.
- If rows need skill-specific columns → follow **`SkillUsePickerToolkitView`**: share `PickerTabStripView` + `WindowedListPaneView`, own row USS + builder, implement the appropriate Runtime port (`ISkillUsePickerView` or new interface in Runtime, not Core).

### New **command rail** or section strip

- Vertical actions: `RailMenuPresenter.CreateVerticalFocus()` + `ConfigureButton` on each `Button`.
- Horizontal sections/tabs: `PickerTabStripView` or `CreateHorizontal` directly.

### Do not

- Put catalog/filter logic in `GridDungeon.UI` views (asmdef boundary).
- Add uGUI overlays for these menus without explicit approval ([UITK rule](../../.cursor/rules/unity-ui-toolkit.mdc)).
- Duplicate `rail-menu__item` styles — extend `RailMenu.uss` or use BEM modifiers.

---

## Tests (Edit Mode)

| Fixture | Path |
|---------|------|
| `WindowedListPaneViewTests` | `Tests/UI/` — 8-slot pool, windowing, scroll bar visibility |
| `ItemListPickerViewTests` | `Tests/UI/` — shop-style tabs + row selection |
| `PartyInventoryBagViewTests` | `Tests/UI/` — party layout + engage-on-confirm |
| `CombatItemListPickerAdapterTests` | `Tests/UI/` — combat adapter + presentation builder |
| `SkillUsePickerToolkitViewTests` | `Tests/UI/` — skill tabs + row confirm |
| `MenuFocusNavigatorTests` | `Tests/UI/` — focus wrap/skip |
| `CommandPanelViewTests` | `Tests/Combat/` — command rail focus |

Manual: Dev bootstrap **F1** hub shop, **Tab** party inventory, **F3** combat Skill / Item pickers.

---

## File map (game repo)

| Path | Purpose |
|------|---------|
| `Assets/UI/Screens/Shared/InputHint.uxml` | Global bind-hint overlay |
| `Assets/UI/Screens/Shared/InputHint.uss` | Bottom-right chip styles |
| `Assets/Scripts/Runtime/UI/InputHintPresenter.cs` | Overlay presenter (`sortingOrder` 300) |
| `Assets/Scripts/UI/Views/InputHints.cs` | `Publish` / `Clear` facade |
| `Assets/Scripts/UI/Views/TabbedPickerRailHints.cs` | Shared bind-copy strings |
| `Assets/UI/Screens/Shared/RailMenu.uss` | Chip + button rail styles |
| `Assets/UI/Screens/Shared/CommandPanel.uss` | Vertical rail panel |
| `Assets/UI/Screens/Shared/TabbedPicker.uss` | Modal shell |
| `Assets/UI/Screens/Shared/WindowedList.uss` | Windowed list chrome |
| `Assets/UI/Screens/Shared/ItemListRow.uss` | Item row BEM |
| `Assets/UI/Screens/Shared/ItemListPicker.uxml` | Shop overlay template |
| `Assets/UI/Screens/Shared/PartyInventory.uxml` | Party bag pane template |
| `Assets/UI/Screens/Combat/SkillUsePicker.uxml` | Skill modal template |
| `Assets/Scripts/UI/Views/RailMenuPresenter.cs` | Rail facade |
| `Assets/Scripts/UI/Views/PickerTabStripView.cs` | Horizontal tabs |
| `Assets/Scripts/UI/Views/WindowedListPaneView.cs` | Windowed list + `IListFocusNavigator` (#185) |
| `Assets/Scripts/UI/Views/WindowedListPaneClasses.cs` | BEM constants for windowed list |
| `Assets/Scripts/UI/Views/ItemListPickerView.cs` | Unified item picker |
| `Assets/Scripts/UI/Views/HubShopPickerPresenter.cs` | Hub shop modal + `EngageOnConfirm` wiring |
| `Assets/Scripts/UI/Views/PartyInventoryBagView.cs` | Party bag adapter |
| `Assets/Scripts/UI/Views/CombatItemListPickerAdapter.cs` | Combat UITK adapter |
| `Assets/Scripts/Runtime/Combat/CombatItemPickerHost.cs` | Combat Item command orchestration |
| `Assets/Scripts/UI/Views/SkillUsePickerToolkitView.cs` | Skill picker |
| `Assets/Scripts/UI/Navigation/IListFocusNavigator.cs` | Shared list focus contract |
| `Assets/Scripts/UI/Navigation/MenuFocusNavigator.cs` | ADR 026 focus index |
| `Assets/UI/Screens/Shared/PartyMenu.uss` | Opaque party shell + rail bookmark |
| `Assets/UI/Screens/Combat/CombatHud.uss` | Combat picker `left: 240px` offset |
