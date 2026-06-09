# ADR 036 — Party inventory & equipment model

**Status:** Proposed  
**Date:** 2026-06-03  
**Related:** [ADR 035](035-skill-use-picker.md) (tabbed modal UX), [ADR 026](026-combat-menu-focus-navigation.md) (focus + Z/X), [ADR 034](034-skill-point-allocation-outside-combat.md) (party menu gates), [items & inventory](../docs/02-systems/items-and-inventory.md)

**Tracker:** [design-docs #22](https://github.com/miramocha/griddungeon-design-docs/issues/22) · [game epic #151](https://github.com/miramocha/griddungeon-game/issues/151)

## Context

MVP1 needs a single place for **party bag**, **worn gear**, shop, loot ([#31](https://github.com/miramocha/griddungeon-game/issues/31)), and chest grants. Today the game uses `PartyRuntime.GatheredItemIds` (flat string list), shop stubs, and `EquipmentLoadout` on `Combatant` without save or stat application.

Equipment IDs and consumable IDs are locked ([05 — Class design](../docs/05-class-design-mvp1.md#mvp1-content-ids-locked), [character progression § MVP1 equipment](../docs/02-systems/character-progression.md#mvp1-equipment-locked)).

## Decision (MVP1)

### 1. Two containers + hub Credits

| Container | Scope | Persisted on |
|-----------|--------|--------------|
| **Party bag** | Shared fixed slots — consumables, unequipped gear, (MVP2) materials | `SaveGame.PartyInventory` |
| **Worn loadout** | Five slots per core character | `CharacterSaveData.Equipment` |
| **Credits** | Hub wallet (integer) | `HubSaveData.Credits` — **not** a bag slot |

**Naming:** backend/save field is **`Credits`** (not `Gold`). **Display label** ("Credits", "Funds", etc.) comes from content or localization and may change per settings without a save migration. See [items & inventory § Hub currency](../docs/02-systems/items-and-inventory.md#hub-currency-credits).

**Save authority:** `SaveGame` is source of truth; `PartyRuntime` mirrors inventory on load.

### 2. Fixed bag slots (EO-style)

- **`partyBagSlotCount`** default **30** — tuning constant ([mvp1-spec §6](../docs/mvp1-spec.md#6-open-for-tuning-only-locked-structure)).
- Each slot: **empty**, **one consumable/material stack**, or **one equipment instance** — never both; no multi-slot stacks.
- Equipped items **do not** consume bag slots.

### 3. Equipment instances

- Bag rows: `EquipmentInstance` (`instanceId`, `equipId`, `isIdentified`).
- Worn: `EquipmentLoadout` stores **`equipId`** per slot after equip.
- Shop buy → **identified** instance (or direct equip flow). Chest may grant **unidentified** (`scout_charm` tutorial).
- **Identify** at shop — Credits cost; flips `isIdentified` on bag instance.
- **Duplicate `equipId`** allowed as separate bag instances.

### 4. Core vs Runtime vs UI

| Layer | Responsibility |
|-------|----------------|
| **Core** | `PartyInventory`, `InventoryRules`, `InventoryBagCatalog`, `EquipmentStatAggregator`, `LootResolver` |
| **Runtime** | `ItemDefinition` / `EquipmentDefinition` SOs, `ContentDatabase`, `ShopService`, coordinators |
| **UI** | `PartyMenuShell`, `IInventoryBagView`, `IPartyEquipmentView` — **no** stack or equip rules in views |

### 5. Party menu shell (required MVP1)

**`Tab`** opens a **party menu overlay** in **hub** and **exploration** when safe ([ADR 034](034-skill-point-allocation-outside-combat.md)) — not combat.

**Top-level sections (v1):** vertical list, **hub service style** — **W/S** moves focus; **focused row switches the pane immediately** (no extra confirm to enter a section). **`X`** closes the whole menu. **`Tab`** toggles open/close.

| Section id | Label (player-facing) | Pane |
|------------|------------------------|------|
| `inventory` | **Inventory** | Shared party bag (§6) |
| `equipment` | **Equipment** | Active party worn gear (§7) |
| `formation` | **Formation** | Core front/back swap via shared `PartyFormationGridView` ([custom party UI](../docs/04-dev/custom-party-ui.md)) |

**Deferred (not v1 rows):** Skills ([ADR 034](034-skill-point-allocation-outside-combat.md)) — separate ticket; do not show disabled placeholder rows unless a follow-up UX ticket adds them.

**Rejected for v1:** `Tab` opens bag only with no shell; horizontal top tabs at shell level (Q/E overload with bag categories and member cycle); equip/unequip on hub **Guild** service panel ([hub-and-services](../docs/02-systems/hub-and-services.md)).

**Runtime:** `PartyMenuCoordinator` owns section focus, pane visibility, and input delegation. **`InventoryBagCoordinator`** stays bag-only inside the Inventory pane.

**Game issues:** shell [#166](https://github.com/miramocha/griddungeon-game/issues/166) · equipment pane [#167](https://github.com/miramocha/griddungeon-game/issues/167) · stats/equip rules [#155](https://github.com/miramocha/griddungeon-game/issues/155).

### 6. Inventory pane — category tabs (required MVP1)

Party menu section **Inventory** shows horizontal category tabs — **same rules as ADR 035**:

| Tab id | Label | Filter |
|--------|-------|--------|
| **`all`** | All | **Default** — all occupied slots by index |
| `consumables` | Consumables | `InventorySlotKind.Consumable` |
| `equipment` | Equipment | `InventorySlotKind.Equipment` |
| `materials` | Materials | MVP2 — hidden until ≥1 material slot |

- **`InventoryBagCatalog`** in Core builds tabs + rows; UI renders only.
- **`Q` / `E`** cycle category tabs **only while the Inventory pane is active**; scoped input (no exploration turn steal).
- **Z** on equipment bag rows in Inventory pane: **does not equip** in v1 — equip via **Equipment** pane (§7).
- **Combat `Item` command:** consumable **row list** only — **no** bag tab strip ([ADR 026](026-combat-menu-focus-navigation.md)).

### 7. Equipment pane — worn loadout (required MVP1)

**Members:** **active party cores only** — occupied `PartyRuntime` core slots (up to 6). **Q/E** cycles prev/next member (wrap). Not full guild bench.

**Per member:** five worn slots (Weapon, Head, Body, Legs, Accessory) with display names from `EquipmentDefinition`; empty slots shown explicitly.

**Equip flow (slot-first):**

1. Focus member (**Q/E**).
2. Focus worn slot (**WASD**).
3. **Z** on slot → **bag sub-picker** — bag rows filtered by `EquipSlot`, `classId`, and `InventoryRules` validation (Core `PartyEquipmentCatalog` / filter helper).
4. **Z** on bag row → `InventoryRules.TryEquip` (via `PartyEquipmentOperations`).
5. Filled slot: sub-picker offers **Replace** (pick new item) and **Remove** (`TryUnequip`) before/alongside bag rows.
6. **X** closes sub-picker back to slot grid; shell **X** closes entire party menu.

**Phases:** hub **and** exploration (same shell, same gates). **Explorers Guild** does **not** host equip/unequip buttons in v1 — assign party + roster summary only.

### 8. Migration

On load, map legacy `GatheredItemIds` → `PartyInventory` stacks (e.g. `patch_kit` × N) or clear in dev saves — implement in [#152](https://github.com/miramocha/griddungeon-game/issues/152).

## Rejected for MVP1

- Unlimited bag size — EO fixed slots from day one.
- Separate material pouch asset — one `PartyInventory`, kind per slot (MVP2 materials tab).
- `ItemCategory` on every `ItemDefinition` — slot kind is enough for tabs.
- Full tabbed bag inside combat Item picker — combat uses filtered consumable list only.
- Codex-driven identify as MVP1 blocker — shop identify sufficient.

## Consequences

- New Core types and save wire fields; breaking change for saves using `GatheredItemIds`.
- `input-bindings` documents party menu shell + pane-scoped `Q`/`E` (parallel to skill picker).
- Hub shop reactive motion “inventory slot update” ([hub-and-services](../docs/02-systems/hub-and-services.md)) targets real bag slots.
- [#12](https://github.com/miramocha/griddungeon-game/issues/12) / [#31](https://github.com/miramocha/griddungeon-game/issues/31) / [#105](https://github.com/miramocha/griddungeon-game/issues/105) implement against this model.

## Acceptance (move to Accepted when)

- [ ] [items-and-inventory.md](../docs/02-systems/items-and-inventory.md) reviewed
- [ ] Cross-links merged; mvp1-spec row added
- [ ] No open questions on instance vs equipId-only for shop gear (locked above)
