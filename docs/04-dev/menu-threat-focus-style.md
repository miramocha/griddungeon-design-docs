---
tags:
  - path/docs/04-dev
  - type/dev
  - scope/required
  - status/active
  - domain/ui
---
# Menu threat focus & backdrop UI style

Authority for migrating **screen-space** UITK toward the frozen **party menu class backdrop** look: flat corners, threat-colored focus (default: transparent row → threat fill + white text; **command rail chips invert** that recipe — see [Command rail inverted focus](#command-rail-inverted-focus-phase-2)), square threat-bordered HP/MP/XP meters.

**Epic:** [griddungeon-game#442](https://github.com/miramocha/griddungeon-game/issues/442)  
**Phase 0 (game):** [#443](https://github.com/miramocha/griddungeon-game/issues/443) — pair with this doc in the same PR window  
**Backdrop stack:** [UI camera stack](ui-camera-stack.md) · [ADR 049](../../decisions/049-ui-camera-stack.md) · [ADR 048](../../decisions/048-party-menu-equipment-inspect.md) (worn rows on backdrop)

**Shipped reference (read-only):** `Assets/UI/Screens/PartyMenu/PartyMenuClassBackdrop.uxml` + `.uss` · `PartyMenuClassBackdropPresenter` (world-space `UiBackdrop` panel)

---

## Frozen backdrop — do not edit for style

`PartyMenuClassBackdrop` is the **visual source of truth**, not a migration target.

| Rule | Detail |
|------|--------|
| **No style edits** | Do **not** change `PartyMenuClassBackdrop.uxml`, `PartyMenuClassBackdrop.uss`, or backdrop presenter **chrome** (`MemberFocusChrome`, `MemberFocusVitals`, `MemberFocusAttrs`, `PartyMenuBackdropEquipValueChrome`) to match screen UI. |
| **Screen migrates toward backdrop** | New shared USS (`MenuThreatFocus.uss`, `StatMeterChrome.uss`) and per-screen imports replicate backdrop recipes at HUD scale. |
| **Allowed backdrop work** | Behavior, data bind, camera/stack, cover-fit, equipment dual-owner fixes — not threat/focus/meter/corner restyling. |
| **Regression** | Epic [#442](https://github.com/miramocha/griddungeon-game/issues/442) done when backdrop is **pixel-identical** before/after all screen phases. |

Worn equipment rows stay on the backdrop per [ADR 048](../../decisions/048-party-menu-equipment-inspect.md); `CharacterDetail` equip slots are screen-space only ([#447](https://github.com/miramocha/griddungeon-game/issues/447)).

---

## Threat focus recipe

Shared focus class: `menu-item--focused` ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md)). Threat focus replaces legacy accent fills on migrated surfaces.

### Interactive (default)

| State | Row background | Label color |
|-------|----------------|---------------|
| **Unfocused** | `transparent` (no fill) | `var(--gd-threat)` |
| **Focused** (`menu-item--focused`) | `var(--gd-threat)` | `var(--gd-white)` |

Empty-value modifiers (e.g. `__equip-value--empty`) keep the same foreground rules; focused empty values use white at full opacity, unfocused empty at reduced threat opacity (~0.55 on backdrop).

**Backdrop reference** — `PartyMenuClassBackdrop.uss`:

```css
.party-menu-class-backdrop__equip-row.menu-item--focused {
    background-color: var(--gd-threat);
}
.party-menu-class-backdrop__equip-row.menu-item--focused
    .party-menu-class-backdrop__equip-tag,
.party-menu-class-backdrop__equip-row.menu-item--focused
    .party-menu-class-backdrop__equip-value {
    color: var(--gd-white);
    opacity: 1;
}
```

**Screen target:** `MenuThreatFocus.uss` — import from `PartyMenu.uss`, `ItemListRow.uss`, `HudOverlay.uss`, etc. per [gap audit](#gap-audit-phase-tagged) below. **Command rail bookmark chips** use the [inverted recipe](#command-rail-inverted-focus-phase-2) in `CommandPanel.uss` / `RailMenu.uss`, not the base `.menu-threat-focus-row` colors from this file.

### Command rail inverted focus (Phase 2)

**Shipped:** [#445](https://github.com/miramocha/griddungeon-game/issues/445). Vertical bookmark chips (hub root menu, combat command rail, party section rail) **invert** the default threat-focus colors so the tucked rail reads as a solid threat column and the focused poke is a white bookmark.

| State | Row background | Label color | Border |
|-------|----------------|-------------|--------|
| **Unfocused** (tucked `translate: -28px`) | `var(--gd-threat)` | `var(--gd-white)` | none (`border-width: 0`) |
| **Focused** (`menu-item--focused`) or **selected** (`rail-menu__item--selected`) | `var(--gd-white)` | `var(--gd-threat)` | none |

**Class hook:** `menu-threat-focus-row` — `RailMenuClasses.ThreatFocusRowClass`; toggled in C# by `CommandRailPanelBuilder` (hub/combat/party section chips). Same class name as `MenuThreatFocus.uss` rows, but **rail USS overrides** win via full selector chains (e.g. `.command-panel .command-panel__btn.rail-menu__item.unity-button.menu-threat-focus-row.menu-item--focused`) so generic `.rail-menu__item.unity-button.menu-item--focused` rules do not leak the default recipe.

**Typography:** `font-size: var(--gd-menu-row-font)` (**18px**) + `-unity-font-definition: var(--gd-rail-menu-font)` (`PartyMenuHeroCosmicIndustry` in palette theme USS) — hero face at HUD row size.

**Unity `Button` press dimming:** explicit `opacity: 1` on `:enabled:hover`, `:enabled:active`, and focused/selected states so engage does not grey the chip.

**Modal rail sibling disable** ([`CommandPanelModalSupport`](shared-menu-picker-ui.md#modal-rail-sibling-disable-commandpanelmodalsupport)):

| Chip | While modal open |
|------|------------------|
| Disabled siblings | Threat fill, white labels, **opacity 0.4** |
| Selected owner (`rail-menu__item--selected:disabled`) | White fill, threat labels, **opacity 1** |

Bookmark geometry (`translate`, chip width, flat caps) is unchanged — [shared menu § Vertical rail bookmark](shared-menu-picker-ui.md#vertical-rail-bookmark-focus-poke).

### Read-only focus variant

When a row can receive focus highlight but must **not** show interactive fill (Formation worn rows on backdrop):

| State | Row background | Label color |
|-------|----------------|---------------|
| **Focused** | `transparent` | `var(--gd-threat)` (empty slots ~0.55 opacity) |

**Backdrop modifier:** `party-menu-class-backdrop--equipment-readonly` on root — see `.party-menu-class-backdrop--equipment-readonly .party-menu-class-backdrop__equip-row.menu-item--focused` in shipped USS.

Screen read-only rows (if any) mirror this with a BEM `--readonly` host modifier + same class toggles; do not invent a second accent color.

---

## Flat corners

**Default for interactive rows and meters:** `border-radius: 0` (square caps).

| Surface | Corner rule |
|---------|-------------|
| Menu rows (rail, picker, party section, equip slots) | Square — no pill caps, no `2px` reason chips |
| Stat meter tracks / fills | Square — USS default (no `border-radius`; Phase 0 [#443](https://github.com/miramocha/griddungeon-game/issues/443)) |
| Command rail vertical chips | Flat caps — `--command-rail-chip-cap-radius: 0` in `CommandRailTokens.uss` (shipped Phase 2 [#445](https://github.com/miramocha/griddungeon-game/issues/445)) |

**Exceptions (keep rounded):**

| Element | Why |
|---------|-----|
| `party-menu-class-backdrop__frame-circle` | Hero silhouette frame — decorative circle, not a list row |
| World / map markers | Exploration map cells, arena plates — not menu threat-focus surfaces |
| Tabbed picker **panel** chrome | Modal shell colors out of epic scope ([#442](https://github.com/miramocha/griddungeon-game/issues/442)) |

STR/TEC/AGI/VIT/LUC **attribute** bars (6px backdrop / screen analog) stay square-bordered; epic meter work is **vitals only** (HP/MP/XP).

---

## Stat meter recipe

Square threat-bordered track, **transparent interior**, colored fill inside.

### Backdrop (reference — 1920×1080 UI-space)

| Piece | USS / token |
|-------|-------------|
| Track | `.party-menu-class-backdrop__attr-bar-track` — `height: 16px`, `border-width: 2px`, `border-color: var(--gd-threat)`, no background fill |
| Fill | `.party-menu-class-backdrop__attr-bar-fill` — width driven in C# (see [Fill math](#fill-math)) |
| HP fill | `--hp` modifier → `background-color: var(--gd-bar-hp)` |
| MP fill | default threat → `background-color: var(--gd-threat)` |
| XP fill | `--xp` modifier → `background-color: var(--gd-bar-xp)` |

Vitals block uses fixed track width `360px` on backdrop; attribute rows use flex-grown track between tag and value.

### Screen (migration target)

| Piece | Target |
|-------|--------|
| Control | `ProgressBar` with shared `StatMeterChrome.uss` |
| Height | `var(--gd-stat-meter-height)` — **12px** on screen HUD |
| Radius | Square — omit `border-radius` (USS default **0**) |
| Track | Threat border, transparent background (match backdrop proportions at 12px) |
| Fills | HP `var(--gd-bar-hp)` · MP `var(--gd-threat)` · XP `var(--gd-bar-xp)` |

**Dedup imports:** `CharacterDetail.uss`, `PartyFormationSlot.uss`, `CombatHud.uss` → `@import` `StatMeterChrome.uss` only; remove per-file pill radius duplicates.

---

## Scale table — backdrop vs screen

Backdrop panel is **1920×1080** world-space UI pixels ([world-space UITK cover-fit](world-space-uitk-cover-fit.md)). Screen HUD uses `GamePanelSettings` reference resolution; row fonts do **not** scale linearly — compensate with theme tokens.

| Element | Backdrop (UI-space) | Screen (HUD) | Notes |
|---------|---------------------|--------------|-------|
| Equip / worn row height | **80px** | **~22px** (`ItemListRow`, party section) | Tag + value single row |
| Derived stat tag/value | **48px** font | **13–16px** typical | ATK/DEF/MATK/MDEF on `CharacterDetail` |
| Level tag/value | **96px** font | N/A on screen | Backdrop-only hero stack |
| Attr / vital value labels | **48px** font | **13–16px** | Pair with meter height |
| Vital meter track | **16px** tall, 2px border | **12px** tall (`--gd-stat-meter-height`) | Width % from fill math |
| Attr bar track (STR…) | **16px** tall | **6px** where shown | Out of vitals meter epic |
| Command rail chip | N/A (screen) | **268px** chip + **28px** poke; flat caps | [Inverted focus](#command-rail-inverted-focus-phase-2); hero font via `--gd-rail-menu-font` ([#445](https://github.com/miramocha/griddungeon-game/issues/445)) |

### Font compensation

Screen rows should **read** like backdrop rows at a glance, not match 48px literally.

| Token | Starting range | Use |
|-------|----------------|-----|
| `--gd-menu-row-font` | **18px** (Phase 1 [#444](https://github.com/miramocha/griddungeon-game/issues/444)) | Party section rows, `ItemListRow`, command rail label **size** — calibrate in Play Mode; document final value in palette theme USS |
| `--gd-rail-menu-font` | `PartyMenuHeroCosmicIndustry` (Phase 2 [#445](https://github.com/miramocha/griddungeon-game/issues/445)) | Command rail bookmark chip labels only (`-unity-font-definition` paired with `--gd-menu-row-font`) |

Prefer theme variables over per-screen `font-size` literals. Backdrop keeps `PartyMenuHeroCosmicIndustry` + `best-fit` ranges. Screen rows default to HUD theme fonts; **command rail chips** explicitly mirror the hero face at 18px via `--gd-rail-menu-font`.

---

## Gap audit (phase-tagged)

Tracker: [#442](https://github.com/miramocha/griddungeon-game/issues/442). Pull order is sequential; each phase assumes the prior shipped.

| Phase | Game issue | Surfaces | Style deliverables |
|-------|------------|----------|-------------------|
| **0** | [#443](https://github.com/miramocha/griddungeon-game/issues/443) | `ProgressBar` vitals on `CharacterDetail`, `PartyFormationSlot`, `CombatHud` | `StatMeterChrome.uss` rewrite; `MenuThreatFocus.uss` scaffold (unwired); square meters (no radius token); MP fill `var(--gd-threat)`; backdrop **unchanged** |
| **1** | [#444](https://github.com/miramocha/griddungeon-game/issues/444) | `PartyMenu.uss` section rail, `ItemListRow` windowed rows | Wire `MenuThreatFocus.uss`; `--gd-menu-row-font` **18px** in palette |
| **2** | [#445](https://github.com/miramocha/griddungeon-game/issues/445) **shipped** | `RailMenu.uss`, `CommandPanel.uss`, `CommandRailTokens.uss` vertical chips | Flat caps; **inverted** threat focus + `menu-threat-focus-row`; `--gd-rail-menu-font`; bookmark `translate: -28px` unchanged |
| **3** | [#446](https://github.com/miramocha/griddungeon-game/issues/446) | `HudOverlay.uss`, `SkillUsePicker.uss`, `CombatHud.uss` roster **focus** | Threat focus on overlay buttons, picker rows, targetable slot chrome (meters from Phase 0) |
| **4** | [#447](https://github.com/miramocha/griddungeon-game/issues/447) | `CharacterDetail.uss` equip slots | Remove `border-radius: 22px`; square threat-focus on `character-detail__equip-slot` |
| **opt** | [#448](https://github.com/miramocha/griddungeon-game/issues/448) | — | `StatBarElement` `UxmlElement` if `ProgressBar` USS remains brittle |

### Out of scope (epic)

- Backdrop USS/UXML/C# style edits
- Tabbed picker modal panel shell / dim colors
- STR/TEC/LUC attribute bar fill colors (vitals meters only)
- uGUI → UITK migration

### Epic acceptance

- [#443](https://github.com/miramocha/griddungeon-game/issues/443)–[#447](https://github.com/miramocha/griddungeon-game/issues/447) closed ([#448](https://github.com/miramocha/griddungeon-game/issues/448) optional)
- [design-docs#83](https://github.com/miramocha/griddungeon-design-docs/issues/83) closed
- Manual: party menu member focus — backdrop pixel-identical
- Screen HP/MP/XP meters match backdrop recipe at 12px scale

---

## Fill math

One display authority in Core; **two bind paths** (custom width % on backdrop, `ProgressBar` on screen).

### Shared formatters (`GridDungeon.Core.Progression`)

| Type | Role |
|------|------|
| `CharacterInspectDisplayFormat` | Placeholders, `FormatVitalValue`, `FormatStatValue`, `FormatHpMp`, level-zero rules |
| `CharacterInspectAttributeBarScale` | STR/TEC/AGI/VIT/LUC bar width — `FillPercent(int value)` clamps to `Max = 200`, returns **0–100** for `LengthUnit.Percent` |

### Vitals — `CharacterInspectDisplayFormat.ResolveVitalFill`

```csharp
// index: 0 = HP, 1 = MP, 2 = XP
ResolveVitalFill(index, vitals, out float fillCurrent, out float fillMax);
```

| Index | `fillCurrent` | `fillMax` | Level ≤ 0 |
|-------|---------------|-----------|-----------|
| 0 HP | `CurrentHp` | `max(1, MaxHp)` | `0` / `1` |
| 1 MP | `CurrentMp` | `max(1, MaxMp)` | `0` / `1` |
| 2 XP | XP band value from `CharacterProgression.TryGetXpLevelBandProgress` | band high | `0` / `1` |

**Backdrop bind:** `PartyMenuClassBackdropPresenter.MemberFocusVitals` → `PartyMenuBackdropMeterRows.ApplyFillPercent(fill, fillCurrent, fillMax, …)` → `width: (clamp(current,0,max)/max)*100%` on `.party-menu-class-backdrop__attr-bar-fill`.

**Screen bind:** `CharacterDetailStatsBinder` (and combat/hub analogs) set `ProgressBar.highValue` and `ProgressBar.value` directly from model ints — same numeric semantics as `ResolveVitalFill` outputs (HP/MP clamped to max; placeholders when level 0). Prefer calling `ResolveVitalFill` when adding new vitals surfaces to avoid drift.

### Attributes — `CharacterInspectAttributeBarScale.FillPercent`

```csharp
new Length(CharacterInspectAttributeBarScale.FillPercent(statValue), LengthUnit.Percent)
```

Backdrop: `PartyMenuClassBackdropPresenter.MemberFocusAttrs`. Screen: `CharacterDetailStatsBinder` attr rows. Fill color stays `var(--gd-threat)`; only vitals use HP/MP/XP palette tokens.

---

## Implementation map (game repo)

| Asset / type | Path |
|--------------|------|
| Frozen reference USS | `Assets/UI/Screens/PartyMenu/PartyMenuClassBackdrop.uss` |
| Threat focus (screen) | `Assets/UI/Screens/Shared/MenuThreatFocus.uss` (wired Phase 1 [#444](https://github.com/miramocha/griddungeon-game/issues/444)) |
| Command rail chips (inverted) | `Assets/UI/Screens/Shared/CommandPanel.uss`, `RailMenu.uss`, `CommandRailTokens.uss` (Phase 2 [#445](https://github.com/miramocha/griddungeon-game/issues/445)) |
| Rail focus class constant | `Assets/Scripts/UI/Views/RailMenuClasses.cs` — `ThreatFocusRowClass` |
| Stat meters (screen) | `Assets/UI/Screens/Shared/StatMeterChrome.uss` |
| Palette tokens | `Assets/UI/Settings/Themes/GridDungeonPaletteDark.uss` / `GridDungeonPaletteLight.uss` |
| Display math | `Assets/Scripts/Core/Progression/CharacterInspectDisplayFormat.cs` |
| Attr scale | `Assets/Scripts/Core/Progression/CharacterInspectAttributeBarScale.cs` |
| Backdrop fill helper | `Assets/Scripts/Runtime/UI/PartyMenuBackdropMeterRows.cs` |

**Tests:** `PartyMenuClassBackdropFocusShiftTests`, `CharacterProgressionTests` (format + scale), `CharacterDetailViewTests`, UI category via `.\tools\request-test-status.ps1 -Category UI`.

---

## Related

- [Centralized UI services — party menu class backdrop](centralized-ui-services.md#party-menu-class-backdrop--partymenuclassbackdroppresenter--partymenuclassbackdrop)
- [Shared menu & picker UI](shared-menu-picker-ui.md) — `menu-item--focused`, rail bookmark geometry
- [Centralized UI gotchas — worn equip dual DOM owners](centralized-ui-gotchas.md#party-menu-backdrop--worn-equip-rows-dual-dom-owners)
- [Custom party UI](custom-party-ui.md) — floater vs backdrop equipment
