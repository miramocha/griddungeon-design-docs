# ItemListRowBuilder — static UXML row shape

Authority: `Assets/Scripts/UI/Views/ItemListRowBuilder.cs`, `WindowedListPaneView` (slot pool).

Picker rows live inside **`windowed-list__slot`** hosts (8 slots × 12.5% list height). Do not place `item-row` directly under `windowed-list__slots` — rows stretch to natural height without slots.

```xml
<ui:VisualElement class="windowed-list__slot">
    <ui:VisualElement class="item-row menu-item--focused">
        <ui:Label class="item-row__name" text="Stim Draft" />
        <ui:Label class="item-row__meta" text="50c" />
        <ui:VisualElement class="item-row__qty-badge">
            <ui:Label class="item-row__qty-badge__text" text="3" />
        </ui:VisualElement>
    </ui:VisualElement>
</ui:VisualElement>
```

Mirror lists: emit **8** `windowed-list__slot` nodes; fill leading slots with fixture rows; leave trailing slots empty (matches `WindowedListPaneView.DefaultVisibleRowCount`).

## Empty state

When `rows: []` in fixture (`state: empty`):

```xml
<ui:VisualElement class="windowed-list__slots">
    <ui:VisualElement class="windowed-list__slot" />
    <!-- × 8 — no item-row children -->
</ui:VisualElement>
```

No `menu-item--focused`. Detail label `text=""`. Use a separate `*.Empty.DesignMirror.uxml` + manifest `states[]` entry.

## Disabled row (optional separate fixture)

Use `item-row--disabled` + `item-row__reason` only when UX needs to style blocked purchases — not in populated or empty default specimens.

| Modifier | Class |
|----------|-------|
| Disabled row | `item-row--disabled` on row |
| Disabled reason | child `item-row__reason` Label |
| Focus chrome | `menu-item--focused` on row |
| Qty badge | omit when quantity ≤ 0 |

## Tab strip (PickerTabStripView)

Host: `item-list-picker-tabs` with `tabbed-picker__tabs rail-menu rail-menu--horizontal`.

```xml
<ui:Button class="rail-menu__item rail-menu__item--selected" text="Buy">
    <ui:Label class="rail-menu__item-label" text="Buy" />
</ui:Button>
```

Selected tab: `rail-menu__item--selected`. Authority: `RailMenuClasses`, `PickerTabStripView`.
