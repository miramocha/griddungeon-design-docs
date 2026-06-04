# ADR 036 — Party inventory & equipment model

**Status:** Proposed  
**Date:** 2026-06-03  
**Related:** [ADR 035](035-skill-use-picker.md) (tabbed modal UX), [ADR 026](026-combat-menu-focus-navigation.md) (focus + Z/X), [ADR 034](034-skill-point-allocation-outside-combat.md) (party menu gates), [items & inventory](../docs/02-systems/items-and-inventory.md)

**Tracker:** [design-docs #22](https://github.com/miramocha/griddungeon-design-docs/issues/22) · [game epic #151](https://github.com/miramocha/griddungeon-game/issues/151)

## Context

MVP1 needs a single place for **party bag**, **worn gear**, shop, loot ([#31](https://github.com/miramocha/griddungeon-game/issues/31)), and chest grants. Today the game uses `PartyRuntime.GatheredItemIds` (flat string list), shop stubs, and `EquipmentLoadout` on `Combatant` without save or stat application.

Equipment IDs and consumable IDs are locked ([05 — Class design](../docs/05-class-design-mvp1.md#mvp1-content-ids-locked), [character progression § MVP1 equipment](../docs/02-systems/character-progression.md#mvp1-equipment-locked)).

## Decision (MVP1)

### 1. Two containers + gold

| Container | Scope | Persisted on |
|-----------|--------|--------------|
| **Party bag** | Shared fixed slots — consumables, unequipped gear, (MVP2) materials | `SaveGame.PartyInventory` |
| **Worn loadout** | Five slots per core character | `CharacterSaveData.Equipment` |
| **Gold** | Currency | `HubSaveData.Gold` — **not** a bag slot |

**Save authority:** `SaveGame` is source of truth; `PartyRuntime` mirrors inventory on load.

### 2. Fixed bag slots (EO-style)

- **`partyBagSlotCount`** default **30** — tuning constant ([mvp1-spec §6](../docs/mvp1-spec.md#6-open-for-tuning-only-locked-structure)).
- Each slot: **empty**, **one consumable/material stack**, or **one equipment instance** — never both; no multi-slot stacks.
- Equipped items **do not** consume bag slots.

### 3. Equipment instances

- Bag rows: `EquipmentInstance` (`instanceId`, `equipId`, `isIdentified`).
- Worn: `EquipmentLoadout` stores **`equipId`** per slot after equip.
- Shop buy → **identified** instance (or direct equip flow). Chest may grant **unidentified** (`scout_charm` tutorial).
- **Identify** at shop — gold cost; flips `isIdentified` on bag instance.
- **Duplicate `equipId`** allowed as separate bag instances.

### 4. Core vs Runtime vs UI

| Layer | Responsibility |
|-------|----------------|
| **Core** | `PartyInventory`, `InventoryRules`, `InventoryBagCatalog`, `EquipmentStatAggregator`, `LootResolver` |
| **Runtime** | `ItemDefinition` / `EquipmentDefinition` SOs, `ContentDatabase`, `ShopService`, coordinators |
| **UI** | `IInventoryBagView`, UITK party-inventory panel — **no** stack or equip rules in views |

### 5. Category-tabbed bag UI (required MVP1)

Party menu **Inventory** ([`Tab`](../docs/02-systems/input-bindings.md)) shows horizontal tabs — **same rules as ADR 035**:

| Tab id | Label | Filter |
|--------|-------|--------|
| **`all`** | All | **Default** — all occupied slots by index |
| `consumables` | Consumables | `InventorySlotKind.Consumable` |
| `equipment` | Equipment | `InventorySlotKind.Equipment` |
| `materials` | Materials | MVP2 — hidden until ≥1 material slot |

- **`InventoryBagCatalog`** in Core builds tabs + rows; UI renders only.
- **`Q` / `E`** cycle tabs while bag modal open; scoped input (no exploration turn steal).
- **Combat `Item` command:** consumable **row list** only — **no** bag tab strip ([ADR 026](026-combat-menu-focus-navigation.md)).

### 6. Migration

On load, map legacy `GatheredItemIds` → `PartyInventory` stacks (e.g. `patch_kit` × N) or clear in dev saves — implement in [#152](https://github.com/miramocha/griddungeon-game/issues/152).

## Rejected for MVP1

- Unlimited bag size — EO fixed slots from day one.
- Separate material pouch asset — one `PartyInventory`, kind per slot (MVP2 materials tab).
- `ItemCategory` on every `ItemDefinition` — slot kind is enough for tabs.
- Full tabbed bag inside combat Item picker — combat uses filtered consumable list only.
- Codex-driven identify as MVP1 blocker — shop identify sufficient.

## Consequences

- New Core types and save wire fields; breaking change for saves using `GatheredItemIds`.
- `input-bindings` gains inventory modal `Q`/`E` scope (parallel to skill picker).
- Hub shop reactive motion “inventory slot update” ([hub-and-services](../docs/02-systems/hub-and-services.md)) targets real bag slots.
- [#12](https://github.com/miramocha/griddungeon-game/issues/12) / [#31](https://github.com/miramocha/griddungeon-game/issues/31) / [#105](https://github.com/miramocha/griddungeon-game/issues/105) implement against this model.

## Acceptance (move to Accepted when)

- [ ] [items-and-inventory.md](../docs/02-systems/items-and-inventory.md) reviewed
- [ ] Cross-links merged; mvp1-spec row added
- [ ] No open questions on instance vs equipId-only for shop gear (locked above)
