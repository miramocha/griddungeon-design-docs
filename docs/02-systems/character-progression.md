# Character Progression

## Stats (MVP1)

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

- Spent at **hub only** on class trees.
- Respec: expensive NPC service or none in MVP1.

## Equipment

| Slot | Notes |
|------|-------|
| Weapon | Class restrictions via `weaponType` + optional `allowedClassIds` on `EquipmentDefinition` ([05 — Class design](../05-class-design-mvp1.md)) |
| Head / Body / Legs | Armor slots (EO three-piece + weapon) |
| Accessory | **1 slot** in MVP1 |

### MVP1 equipment (locked)

Minimal **hub shop stock** and ContentDatabase slice: **1 weapon + 3 armor + 1 accessory** ([mvp1-spec](../mvp1-spec.md), [game #12](https://github.com/miramocha/griddungeon-game/issues/12)). String IDs are locked in [05 — Class design § MVP1 content IDs](../05-class-design-mvp1.md#mvp1-content-ids-locked).

**Display names** use municipal-underworks flavor (contract crew gear); **`equipId` strings stay locked** for saves and ContentDatabase.

**Stat bonuses** add to `CharacterBaseStats` on equip (`Hp`, `Mp`, `Str`, `Tec`, `Agi`, `Vit`, `Luc`). **Resist bonuses** use the `StatusResistBonuses` fields on `EquipmentDefinition` (0 = none). **Shop buy** prices are tuning stubs ([mvp1-spec §6](../mvp1-spec.md#6-open-for-tuning-only-locked-structure)); sell ≈ **50%** of buy unless noted in data.

| `equipId` | Slot | Display name | `weaponType` | `allowedClassIds` | Stat bonus | Resist bonus | Shop buy | MVP1 source |
|-----------|------|--------------|--------------|---------------------|------------|--------------|----------|-------------|
| `guild_shortsword` | Weapon | Contract Cutter | `sword` | *(empty — any core class)* | +2 STR, +1 AGI | — | 150 | Shop (day one) |
| `leather_coif` | Head | Works Hardhat | — | *(empty)* | +2 VIT, +5 HP | — | 60 | Shop (day one) |
| `leather_jacket` | Body | Channel Vest | — | *(empty)* | +4 VIT, +10 HP | — | 120 | Shop (day one) |
| `leather_boots` | Legs | Channel Waders | — | *(empty)* | +2 VIT, +1 AGI | — | 80 | Shop (day one) |
| `scout_charm` | Accessory | Utility Charm | — | *(empty)* | +2 LUC | Poison +5% | 100 | Shop (day one); optional B1F chest loot |

**Shop stock (MVP1):** all five rows above in `ShopService` day-one inventory (identified on purchase). No synthesis recipes in MVP1.

**Loot (optional):** `scout_charm` may drop from the B1F tutorial chest (`C` on [s1_B1F](../03-content/dungeons-and-encounters.md#s1_b1f--outskirts-gate-intro--mouth)) as **unidentified** until shop identify — same `equipId`, `startsIdentified: false` on the inventory instance. Other pieces are shop-only for MVP1.

**Implementation:** `EquipmentDefinition` ScriptableObjects under `Assets/Content/Equipment/`; lookup via `ContentDatabase.GetEquipment(equipId)` ([05 — Class design](../05-class-design-mvp1.md)).

## Identify & codex

- **Unknown equipment** in labyrinth; identify at shop or with skill.
- **Monstrous Codex** (bestiary): weaknesses fill in as you kill/analyze — EO knowledge metagame.

## Synthesis (EO crafting)

**MVP2** hub feature ([release scope](../00-release-scope.md)); materials from [gathering & fishing](gathering-and-fishing.md):

- Combine monster drops + shop materials → weapons/armor
- Recipe list unlocks via quests and experimentation

## Economy

- Gold from FOEs, random fights, chests, quest
- Sinks: hospital, shop, synthesis, return thread items

## Consumables (starter)

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

- [Party & classes](party-and-classes.md)
- [Hub & services](hub-and-services.md)
- [01 — Core loop](../01-core-loop.md)
