---
tags:
  - path/docs/02-systems
  - type/system
  - scope/required
  - status/draft
  - domain/hub
  - domain/combat
---
# Character Progression

**Scope:** [Required](../00-release-scope.md#required-first-playable)

## Stats at launch

| Stat | Affects |
|------|---------|
| **HP** | Survivability |
| **MP** | Skills / spells |
| **STR** | Physical skills |
| **TEC** | Healing & alchemy power |
| **AGI** | Turn order, evasion |
| **LUC** | Crit, drops, resist (minor) |
| **VIT** | Physical defense |

Exact names can mirror EO or be renamed; **AGI for turn order** is mandatory.

## Leveling

- XP from battles to **core party only** (not summons or guests).
- FOE fights often grant bonus XP vs random.
- Level cap per stratum until boss beaten (soft gate — tune per content).
- On level: +stats, **+1 skill point**, occasional auto-unlock skill.

## Skill points

**Locked:** [ADR 034 — Skill point allocation outside combat](../../decisions/034-skill-point-allocation-outside-combat.md).

**When:** Spend unspent points on **class skill trees** whenever the player is **not** in:

| Blocked | Examples |
|---------|----------|
| **Combat** | `GamePhase.Combat` — command planning, AGI playback, battle end flow |
| **Story / VN** | `StoryEventRunner` active ([ADR 028](../../decisions/028-story-visual-novel-events.md)) |
| **Cutscenes / presentation locks** | Floor-transition vignette, guided-tutorial coach blocking input, any full-screen sequence that disables exploration/hub menus |

**Allowed:** **Hub** (Explorers Guild) and **Exploration** (e.g. `Tab` party menu, exploration pause overlay) — same tree UI and rules in both places. Level-ups during a fight apply **after** the battle ends; the player may spend new points on the next safe screen without returning to hub.

**UI entry points At launch:**

| Location | How |
|----------|-----|
| Hub | Explorers Guild → skill tree per roster member |
| Labyrinth | Party / pause menu → **Skills** (when not blocked above) |

- Respec: expensive NPC service or none at launch.

## Equipment

**System authority:** bag, worn loadout, shop, identify, and tabbed bag UI — [items & inventory](items-and-inventory.md) · [ADR 036](../../decisions/036-party-inventory-model.md).

| Slot | Notes |
|------|-------|
| Weapon | Class restrictions via `weaponType` + optional `allowedClassIds` on `EquipmentDefinition` ([05 — Class design](../05-class-design.md)) |
| Head / Body / Legs | Armor slots (EO three-piece + weapon) |
| Accessory | **1 slot** at launch |

### launch equipment (locked)

Minimal **hub shop stock** and ContentDatabase slice: **1 weapon + 3 armor + 1 accessory** ([release scope](../00-release-scope.md), [game #12](https://github.com/miramocha/griddungeon-game/issues/12)). String IDs are locked in [05 — Class design § content IDs](../05-class-design.md#content-ids-locked).

**Display names** use municipal-underworks flavor (contract crew gear); **`equipId` strings stay locked** for saves and ContentDatabase.

**Stat bonuses** add to `CharacterBaseStats` on equip (`Hp`, `Mp`, `Str`, `Tec`, `Agi`, `Vit`, `Luc`). **Resist bonuses** use the `StatusResistBonuses` fields on `EquipmentDefinition` (0 = none). **Shop buy** prices are tuning stubs ([release scope § Tuning](../00-release-scope.md#tuning-locked-structure)); sell ≈ **50%** of buy unless noted in data.

| `equipId` | Slot | Display name | `weaponType` | `allowedClassIds` | Stat bonus | Resist bonus | Shop buy | Launch source |
|-----------|------|--------------|--------------|---------------------|------------|--------------|----------|-------------|
| `guild_shortsword` | Weapon | Contract Cutter | `sword` | *(empty — any core class)* | +2 STR, +1 AGI | — | 150 | Shop (day one) |
| `leather_coif` | Head | Works Hardhat | — | *(empty)* | +2 VIT, +5 HP | — | 60 | Shop (day one) |
| `leather_jacket` | Body | Channel Vest | — | *(empty)* | +4 VIT, +10 HP | — | 120 | Shop (day one) |
| `leather_boots` | Legs | Channel Waders | — | *(empty)* | +2 VIT, +1 AGI | — | 80 | Shop (day one) |
| `scout_charm` | Accessory | Utility Charm | — | *(empty)* | +2 LUC | Poison +5% | 100 | Shop (day one); optional B1F chest loot |

**Shop stock At launch:** all five rows above in `ShopService` day-one inventory (identified on purchase). No synthesis recipes at launch.

**Loot (optional):** `scout_charm` may drop from the B1F tutorial chest (`C` on [s1_B1F](../03-content/../archive/mvp1-s1-floor-layouts-draft.md#s1_b1f--outskirts-gate-intro--gate)) as **unidentified** until shop identify — same `equipId`, `startsIdentified: false` on the inventory instance. Other pieces are shop-only at launch.

**Implementation:** `EquipmentDefinition` ScriptableObjects under `Assets/Content/Equipment/`; lookup via `ContentDatabase.GetEquipment(equipId)` ([05 — Class design](../05-class-design.md)). Runtime flow: [items & inventory](items-and-inventory.md).

## Identify & codex

- **Unknown equipment** in labyrinth; identify at shop ([items & inventory § identify](items-and-inventory.md#equipment-instances--identify)) or with skill (later).
- **Monstrous Codex** (bestiary): weaknesses fill in as you kill/analyze — EO knowledge metagame.

## Synthesis (EO crafting)

**Optional** hub feature ([release scope](../00-release-scope.md)); materials from [gathering & fishing](gathering-and-fishing.md):

- Combine monster drops + shop materials → weapons/armor
- Recipe list unlocks via quests and experimentation

## Economy

- **Credits** from FOEs, random fights, chests, quest — save field `HubSaveData.Credits`; display label swappable ([items & inventory § Hub currency](items-and-inventory.md#hub-currency-credits))
- Sinks: hospital, shop, synthesis, return thread items

## Consumables (starter)

Locked IDs and combat/field context — [items & inventory § consumables](items-and-inventory.md#consumables).

| Item | Use |
|------|-----|
| Patch Kit (`patch_kit`) | Heal HP — crew field dressing |
| Stim Draft (`stim_draft`) | Heal MP — utility focus stimulant |
| Trauma Kit (`trauma_kit`) | Full HP restore (rare) — crew emergency kit |
| Return thread | Exit labyrinth to hub |
| Analysis glass | Reveal enemy weaknesses in fight (optional) |

## Death & save (EO-aligned)

- **Save:** inn at hub.
- **Wipe in labyrinth:** GAME OVER → load last save.
- **Map:** persists per floor/stratum ([ADR 002](../../decisions/002-mapping-model.md)).
- **No roster permadeath** by default.

## Meta (later)

- Grimoire / achievement style rewards for floor completion, full map, FOE clears

## Related docs

- [Items & inventory](items-and-inventory.md)
- [Party & classes](party-and-classes.md)
- [Hub & services](hub-and-services.md)
- [01 — Core loop](../01-core-loop.md)
