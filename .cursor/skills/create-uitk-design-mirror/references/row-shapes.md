# ItemListRowBuilder — static UXML row shape

Authority: `Assets/Scripts/UI/Views/ItemListRowBuilder.cs`

Mirror rows are **VisualElement** nodes (not runtime-built). Match BEM classes:

```xml
<ui:VisualElement class="item-row menu-item--focused">
    <ui:Label class="item-row__name" text="Stim Draft" />
    <ui:Label class="item-row__meta" text="50c" />
    <ui:VisualElement class="item-row__qty-badge">
        <ui:Label class="item-row__qty-badge__text" text="3" />
    </ui:VisualElement>
</ui:VisualElement>
```

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
