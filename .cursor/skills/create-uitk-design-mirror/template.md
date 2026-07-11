# Design mirror — templates

## Fixture schema

`Assets/UI/Editor/DesignMirror/Fixtures/{component-id}.fixture.yaml`

```yaml
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
  - name: Rusty Blade
    meta: "120c"
    enabled: false
    reason: "Not enough credits"
modifiers:
  hidden: false
```

| Field | Meaning |
|-------|---------|
| `title` | `item-list-picker-title` placeholder |
| `detail` | `item-list-picker-detail` placeholder |
| `tabs[].label` | Tab button label |
| `tabs[].selected` | Adds `rail-menu__item--selected` |
| `rows[].name` | `item-row__name` text |
| `rows[].meta` | `item-row__meta` text |
| `rows[].quantity` | Optional qty badge (>0) |
| `rows[].focused` | Adds `menu-item--focused` on row |
| `rows[].enabled: false` | Adds `item-row--disabled` + optional `reason` |
| `modifiers.hidden` | When true, add `tabbed-picker--hidden` on root |

## Manifest entry template

Append to `Assets/UI/Editor/DesignMirror/mirror-manifest.yaml`:

```yaml
  - id: item-list-picker
    label: Item List Picker (shop overlay profile)
    mirror:
      uxml: Assets/UI/Editor/DesignMirror/Shared/ItemListPicker.DesignMirror.uxml
      uss: Assets/UI/Editor/DesignMirror/Shared/ItemListPicker.DesignMirror.uss
      fixture: Assets/UI/Editor/DesignMirror/Fixtures/item-list-picker.fixture.yaml
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

## Naming convention

| Production | Mirror |
|------------|--------|
| `Assets/UI/Screens/Shared/Foo.uxml` | `Assets/UI/Editor/DesignMirror/Shared/Foo.DesignMirror.uxml` |
| `TabbedPicker.uss` (etc.) | `Foo.DesignMirror.uss` (merged editable copy) |

Subfolders mirror production layout (`Shared/`, `Hub/`, `Combat/`).
