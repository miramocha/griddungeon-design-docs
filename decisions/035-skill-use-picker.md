# ADR 035 — Skill use picker (modal + tabs)

**Status:** Accepted (launch)  
**Date:** 2026-05-30  
**Related:** [ADR 026](026-combat-menu-focus-navigation.md) (focus + Z/X), [ADR 034](034-skill-point-allocation-outside-combat.md) (skill **trees** — separate UI), [ADR 016](016-summon-control-mvp1.md) (summon kits)

## Context

Combat **Skill** today queues the first `AllocatedSkillId` only — no list or categories. Players need a picker for all learned skills in battle, and the same shell should support **field** heal/mend later (Hub/Exploration when safe per ADR 034).

**Skill trees** (spending skill points on class nodes) are a **different** screen — do not merge with this picker.

## Decision (launch)

### 1. Swappable UI (presentation port)

| Layer | Responsibility |
|-------|----------------|
| **Core** | `SkillPickerCatalog`, `SkillUseContext`, DTOs, tab grouping rules — no Unity UI |
| **Runtime** | `ISkillUsePickerView`, `SkillPickerCoordinator`, `CombatSkillPickerHost`, `FieldSkillPickerHost` (later) |
| **UI** | `SkillUsePickerToolkitView` implements `ISkillUsePickerView` — replaceable without changing catalog or combat queue rules |

`CommandPanelView` calls the **host/coordinator** only; it does not build skill lists or own UXML.

### 2. Modal tabs — **All** is default

Picker shows **horizontal tabs**. **Default selected tab: `All`** — lists every skill the actor may use in the current context (combat vs field), in stable sort order (e.g. display name, then `skillId`).

| Tab id | Label (player-facing) | Contents |
|--------|------------------------|----------|
| **`all`** | **All** | **Default.** Union of all rows for this pick — no type filter |
| `physical` | Physical | `SkillType.Physical` |
| `elemental` | Elemental | `SkillType.Elemental` |
| `heal` | Heal / Recovery | `SkillType.Heal` |
| `buff` | Buff | `SkillType.Buff` |
| `debuff` | Debuff | `SkillType.Debuff` |
| `deploy` | Deploy | `SkillType.Deploy` |
| `passive` | Passive | `SkillType.Passive` (hidden if empty) |

**Tab visibility:** Show **`All`** always (when the pick has ≥1 skill). Show a **type tab** only if ≥1 skill in that pick maps to that `SkillType`. Do not show empty type tabs.

**Switching tabs** filters the list; selection + confirm applies the highlighted skill. Disabled rows (MP, bind, context) stay visible on every tab with a short disabled reason.

**Row chrome (launch), [#149](https://github.com/miramocha/griddungeon-game/issues/149)):** each row shows **display name** + **MP cost label** (`CostLabel`, catalog-formatted). **Mechanical description** (`descriptionEn` from content) appears in a **detail panel** for the **focused** row only — not as a subtitle on every row. Description text is **authored** on `SkillDefinition`; do not auto-build it from `SkillData` stats. Copy rules: [mvp1-class-skills](../docs/03-content/class-skills.md).

**Tab navigation (launch) — keyboard):** while the picker is open, cycle visible tabs (wrap at ends):

| Action | Keyboard (launch) | Notes |
|--------|-----------------|-------|
| **Previous tab** | **`Q`** | Does not fire exploration **turn left** — picker owns input scope |
| **Next tab** | **`E`** | Does not fire exploration **turn right** |
| **Select tab** | LMB on tab header | Optional; **`Q`/`E`** sufficient at launch |

Row list within the active tab still uses **arrows / `W`/`A`/`S`/`D`** + **`Z`** confirm / **`X`** cancel ([ADR 026](026-combat-menu-focus-navigation.md)). **`InputRouter`** (or picker host) enables **`SkillPickerTabPrev` / `SkillPickerTabNext`** only while `ISkillUsePickerView.IsOpen`; bind **`Q`/`E`** on Combat (and Field UI scope later).

**Deferred (not (launch)):** gamepad tab cycle — **`L1`** / **`R1`** when [ADR 009](009-input-bindings-pc.md) gamepad support ships; reserve action names in the action map, no implementation required for picker (launch).

**Grouping authority:** `SkillPickerCatalog` in Core returns `SkillPickerPresentationModel` with `Tabs[]` each holding `Rows[]`. UI only renders tabs and rows — no duplicate filter logic in UITK.

Tab id → `SkillType` mapping lives in Core (single table). **No** separate `pickerTabId` on content at launch unless a follow-up ticket needs finer UX than `SkillType`.

### 3. Contexts

| Context | When | Skills shown |
|---------|------|----------------|
| **Combat** | Command **Skill** during planning / summon turn | `AllocatedSkillIds` or summon `skillIds`; filter `useContexts` includes Combat |
| **Field** | Party menu / pause **Use skill** (later slice) | Allocated skills with Field flag; ADR 034 gates (not combat / VN / cutscene) |

### 4. Flow

```
Skill command → Coordinator.BeginPick → Catalog.Build → View.Show(model)
  → default tab All; Q/E change tab → arrows/WASD highlight row → Confirm (Z / LMB)
  → Coordinator completes → Combat: targeting + queue | Field: applier
  → Cancel (X) → close, no queue
```

While picker open: command-bar confirm blocked (same class of gate as targeting — ADR 026); **`Q`/`E`** route to tab cycle, not exploration turn.

## Rejected at launch

| Option | Why |
|--------|-----|
| Type tabs only (no All) | Players expect full list first; EO-style “all skills” tab is familiar |
| Hub-only picker | ADR 034 allows labyrinth when safe |
| Picker inside `CombatController` | Swappable UI + testable catalog |
| Merging skill tree + use picker | Different jobs (allocate vs cast) |

## Consequences

- **Game:** `ISkillUsePickerView`, coordinator, UITK modal with tab strip + list + detail panel; combat host replaces `ResolvePrimarySkillId` shortcut
- **Content:** `SkillDefinition.useContexts` (Combat / Field flags); `skillType` already on SO — drives non-All tabs; `descriptionEn` on all (launch) skills ([mvp1-class-skills](../docs/03-content/class-skills.md))
- **Docs:** [mvp1-class-skills](../docs/03-content/class-skills.md) Type column = tab mapping; pause menu label **Skill trees** (ADR 034) vs **Use skill** for field picker
- **Input:** `SkillPickerTabPrev` / `SkillPickerTabNext` on Combat (+ Field scope); **`Q`/`E`** only at launch — see [input bindings § Skill use picker](../docs/02-systems/input-bindings.md#skill-use-picker-modal). Gamepad **`L1`/`R1`** deferred.
- **Tests:** Core `SkillPickerCatalogTests` (All vs Physical tab counts, empty tab omission); Runtime coordinator + `NullSkillUsePicker`; UI tab wrap with Q/E (no gamepad tests at launch)

## Related

- [Custom skill picker UI (dev)](../docs/04-dev/custom-skill-picker-ui.md) — implement `ISkillUsePickerView`, wire `CombatSkillPickerHost`
- [Combat](combat.md), [character progression § Skill points](../docs/02-systems/character-progression.md#skill-points)
- [05 — class design](../docs/05-class-design.md) — `SkillType`, `SkillDefinition`
- [Game #52](https://github.com/miramocha/griddungeon-game/issues/52) — skill rules; [#12](https://github.com/miramocha/griddungeon-game/issues/12) — ContentDB
