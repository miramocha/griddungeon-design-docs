# Example — ItemListPicker (reference)

Reference layout for **create-uitk-design-mirror** / **sync-uitk-design-mirror**. Mirror assets are not checked in until a component is bootstrapped; use this doc when registering `item-list-picker` again.

## Inputs

| Role | Path |
|------|------|
| Production shell | `Assets/UI/Screens/Shared/ItemListPickerShell.uxml` |
| Production wrapper | `Assets/UI/Screens/Shared/ItemListPicker.uxml` |
| USS targets | `TabbedPicker.uss`, `WindowedList.uss`, `ItemListRow.uss` |
| Row builder | `ItemListRowBuilder.cs` |
| Fixture (populated) | `Fixtures/item-list-picker.fixture.yaml` |
| Fixture (empty) | `Fixtures/item-list-picker-empty.fixture.yaml` |

## Outputs

```
Assets/UI/Editor/DesignMirror/
├── README.md
├── mirror-manifest.yaml
├── Fixtures/
│   ├── item-list-picker.fixture.yaml
│   └── item-list-picker-empty.fixture.yaml
└── Shared/
    ├── ItemListPicker.DesignMirror.uxml
    ├── ItemListPicker.Empty.DesignMirror.uxml
    └── ItemListPicker.DesignMirror.uss
```

## Populated mirror (`ItemListPicker.DesignMirror.uxml`)

- Root `item-list-picker` **without** `tabbed-picker--hidden` (visible in UI Builder)
- Panel `item-list-picker-panel` with `pop-in pop-in--expanded`
- `item-list-picker-tabs`: static Buy/Sell buttons
- `windowed-list__slots`: 8 `windowed-list__slot` hosts; 5 filled from fixture, 3 empty trailing slots
- One `menu-item--focused` row
- `item-list-picker-detail`: fixture detail string

## Empty mirror (`ItemListPicker.Empty.DesignMirror.uxml`)

- Same shell/bindable `name` hooks and shared USS
- Sell tab selected; title `Shop — Sell`
- Eight **empty** `windowed-list__slot` nodes (matches runtime when tab has no rows)
- Blank `item-list-picker-detail`
- **Not** synced to production shell — UX layout reference only (`syncToProduction: false`)

## Mirror USS

- `@import` read-only: `RailMenu.uss`, `PopIn.uss`, `MenuFocus.uss`, `ItemRowQuantity.uss`
- Body: copied selectors from `TabbedPicker`, `WindowedList`, `ItemListRow` (UX-editable)

## UX handoff

> Open `ItemListPicker.DesignMirror.uxml` (stock rows) or `ItemListPicker.Empty.DesignMirror.uxml` (empty list) in Unity UI Builder. Edit layout and `ItemListPicker.DesignMirror.uss` only.

## After UX edit

Run **sync-uitk-design-mirror** for component `item-list-picker` (primary populated UXML + shared USS).
