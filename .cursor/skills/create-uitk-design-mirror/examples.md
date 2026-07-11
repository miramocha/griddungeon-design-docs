# Example — ItemListPicker first mirror

## Inputs

| Role | Path |
|------|------|
| Production shell | `Assets/UI/Screens/Shared/ItemListPickerShell.uxml` |
| Production wrapper | `Assets/UI/Screens/Shared/ItemListPicker.uxml` |
| USS targets | `TabbedPicker.uss`, `WindowedList.uss`, `ItemListRow.uss` |
| Row builder | `ItemListRowBuilder.cs` |
| Fixture | `Assets/UI/Editor/DesignMirror/Fixtures/item-list-picker.fixture.yaml` |

## Outputs

```
Assets/UI/Editor/DesignMirror/
├── README.md
├── mirror-manifest.yaml
├── Fixtures/item-list-picker.fixture.yaml
└── Shared/
    ├── ItemListPicker.DesignMirror.uxml
    └── ItemListPicker.DesignMirror.uss
```

## Mirror UXML shape

- Root `item-list-picker` **without** `tabbed-picker--hidden` (visible in UI Builder)
- Panel wraps `item-list-picker-shell` inline (no `<ui:Instance>` — self-contained specimen)
- `item-list-picker-tabs`: static Buy/Sell buttons
- `windowed-list__slots`: 6 static rows from fixture
- `item-list-picker-detail`: fixture detail string

## Mirror USS

- `@import` read-only: `RailMenu.uss`, `PopIn.uss`, `MenuFocus.uss`, `ItemRowQuantity.uss`
- Body: copied selectors from `TabbedPicker`, `WindowedList`, `ItemListRow` (UX-editable)

## UX handoff

> Open `Assets/UI/Editor/DesignMirror/Shared/ItemListPicker.DesignMirror.uxml` in Unity UI Builder. Edit layout and `ItemListPicker.DesignMirror.uss` only. Do not open `Assets/UI/Screens/`.

## After UX edit

Run **sync-uitk-design-mirror** for component `item-list-picker`.
