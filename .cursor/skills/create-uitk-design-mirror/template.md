# Design mirror — templates

## Fixture schema

`Assets/UI/Editor/DesignMirror/Fixtures/{component-id}.fixture.yaml` (primary / populated state)

```yaml
state: populated
title: "Shop — Buy"
detail: "Stim Draft — restores 40 HP. 50 credits."
tabs:
  - label: Buy
    selected: true
  - label: Sell
rows:
  - name: Stim Draft
    meta: "50c"
    quantity: 3
    focused: true
  - name: Ether Patch
    meta: "30c"
    quantity: 1
modifiers:
  hidden: false
  popInExpanded: true
```

### Empty state fixture

`Assets/UI/Editor/DesignMirror/Fixtures/{component-id}-empty.fixture.yaml`

```yaml
state: empty
title: "Shop — Sell"
detail: ""
tabs:
  - label: Buy
  - label: Sell
    selected: true
rows: []
modifiers:
  hidden: false
  popInExpanded: true
```

| Field | Meaning |
|-------|---------|
| `state` | `populated` (default) or `empty` — documents mirror specimen |
| `title` | `item-list-picker-title` placeholder |
| `detail` | `item-list-picker-detail` placeholder (`""` for empty) |
| `tabs[].label` | Tab button label |
| `tabs[].selected` | Adds `rail-menu__item--selected` |
| `rows[].name` | `item-row__name` text |
| `rows[].meta` | `item-row__meta` text |
| `rows[].quantity` | Optional qty badge (>0) |
| `rows[].focused` | Adds `menu-item--focused` on row (omit when `rows` empty) |
| `rows[].enabled: false` | Adds `item-row--disabled` + optional `reason` (separate fixture if UX needs it) |
| `modifiers.hidden` | When true, add `tabbed-picker--hidden` on root |
| `modifiers.popInExpanded` | When true, add `pop-in--expanded` on `pop-in` panel hosts |

**Empty list:** `rows: []` → emit 8 empty `windowed-list__slot` nodes; no focused row; detail blank.

## Manifest entry template

Append to `Assets/UI/Editor/DesignMirror/mirror-manifest.yaml`:

```yaml
  - id: item-list-picker
    label: Item List Picker (shop overlay profile)
    mirror:
      uxml: Assets/UI/Editor/DesignMirror/Shared/ItemListPicker.DesignMirror.uxml
      uss: Assets/UI/Editor/DesignMirror/Shared/ItemListPicker.DesignMirror.uss
      fixture: Assets/UI/Editor/DesignMirror/Fixtures/item-list-picker.fixture.yaml
    states:
      - id: empty
        label: Empty windowed list (no rows)
        fixture: Assets/UI/Editor/DesignMirror/Fixtures/item-list-picker-empty.fixture.yaml
        uxml: Assets/UI/Editor/DesignMirror/Shared/ItemListPicker.Empty.DesignMirror.uxml
        syncToProduction: false
    production:
      shellUxml: Assets/UI/Screens/Shared/ItemListPickerShell.uxml
      wrapperUxml: Assets/UI/Screens/Shared/ItemListPicker.uxml
      ussTargets:
        - Assets/UI/Screens/Shared/TabbedPicker.uss
        - Assets/UI/Screens/Shared/WindowedList.uss
        - Assets/UI/Screens/Shared/ItemListRow.uss
    bindableNames:
      - item-list-picker
      - item-list-picker-title
      - item-list-picker-tabs
      - item-list-picker-rows
      - item-list-picker-detail
    stripHosts:
      - item-list-picker-tabs
      - windowed-list__slots
    rowTemplate:
      source: ItemListRowBuilder
```

| Manifest field | Meaning |
|----------------|---------|
| `mirror.uxml` / `mirror.fixture` | Primary populated specimen — **sync** promotes this shell layout |
| `states[]` | Extra UX specimens (empty list, future disabled-row sample, …) |
| `states[].syncToProduction` | When `false`, UXML is Builder-only; USS changes still merge from shared `mirror.uss` |

## Naming convention

| Production | Mirror |
|------------|--------|
| `Assets/UI/Screens/Shared/Foo.uxml` | `Assets/UI/Editor/DesignMirror/Shared/Foo.DesignMirror.uxml` |
| — | `Foo.Empty.DesignMirror.uxml` for `states[].id: empty` |
| `TabbedPicker.uss` (etc.) | `Foo.DesignMirror.uss` (merged editable copy) |

Subfolders mirror production layout (`Shared/`, `Hub/`, `Combat/`).
