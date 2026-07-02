---
tags:
  - path/docs/03-content
  - type/content
  - scope/required
  - status/accepted
  - domain/content-pipeline
---
# Content schema (ScriptableObjects)

Runtime **ScriptableObject** types, `Assets/Content/` folders, and `ContentDatabase` rows. Field-level rules live in linked system and content docs; **locked string IDs** in [content IDs](content-ids.md).

**Code layout:** game repo [Assets/Scripts/README.md](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/README.md). **C# type catalog:** [05 — Class design](../05-class-design.md).

---

## Content definitions (Runtime ScriptableObjects)

All read-only at runtime. Created in the Unity editor and referenced by `ContentDatabase`.

| Type | Asset folder | Authority |
|------|--------------|-----------|
| `ClassDefinition`, `SkillNodeDefinition` | `Assets/Content/Classes/` | [party & classes](../02-systems/party-and-classes.md), [class skills](class-skills.md) |
| `SkillDefinition` | `Assets/Content/Skills/` | [class skills](class-skills.md), [ADR 035](../../decisions/035-skill-use-picker.md), [combat presentation](../02-systems/combat-presentation.md) |
| `StatusDefinition` | `Assets/Content/Status/` | [combat status & buffs](../02-systems/combat-status-and-buffs.md) |
| `EquipmentDefinition` | `Assets/Content/Equipment/` | [character progression](../02-systems/character-progression.md), [ADR 036](../../decisions/036-party-inventory-model.md) |
| `ItemDefinition` | `Assets/Content/Items/` | [items & inventory](../02-systems/items-and-inventory.md) |
| `EnemyDefinition` | `Assets/Content/Enemies/` | [enemy roster](enemy-roster.md) |
| `LootTableDefinition` | `Assets/Content/LootTables/` | [items & inventory](../02-systems/items-and-inventory.md) |
| `RandomEncounterTableDefinition` | `Assets/Content/RandomEncounterTables/` | [dungeons & encounters](dungeons-and-encounters.md#random-encounter-table), [enemy-roster](enemy-roster.md#foe-vs-random-placement-per-floor); floor assigns `randomEncounterTableId` only |
| `EncounterGroup` | `Assets/Content/EncounterGroups/` | [enemy roster](enemy-roster.md), [FOE encounters](../02-systems/foe-encounters.md); optional `Events[]` combat→story rows ([combat § Encounter events](../02-systems/combat.md#encounter-events-combat--story)) |
| `StoryEventDefinition` | `Assets/Content/StoryEvents/` | [story events](../02-systems/story-events.md), [ADR 028](../../decisions/028-story-visual-novel-events.md) |
| `NavigatorDefinition` | `Assets/Content/Navigators/` | [navigator](../02-systems/navigator.md) |
| `ProtocolSkillDefinition` | `Assets/Content/ProtocolSkills/` | [synchro protocol](../02-systems/synchro-protocol.md) |
| `SummonDefinition` | `Assets/Content/Summons/` | [summons & guests](../02-systems/summons-and-guests.md), [ADR 016](../../decisions/016-summon-control-mvp1.md) |
| `ExplorationFloor` | `Assets/Content/Floors/` | [mapping](../02-systems/mapping.md), [floor editor](../02-systems/floor-editor.md), [ADR 040](../../decisions/040-floor-exit-topology-graph.md); `randomEncounterTableId` → shared table SO |
| `StratumDefinition` | `ContentDatabase` | [dungeons & encounters](dungeons-and-encounters.md), [campaign S1 intro](campaign/s1-intro.md) |
| `CampaignStartConfig` | `ContentDatabase` | Cold start: `CampaignStartType` Hub vs Spawn, `LocationId` / `FloorId` / `HubExitId` — `GameBootstrapPhase` picks initial macro phase |
| `NewGameDefaults` | `ContentDatabase` | `DefaultNavigatorId` seeded by `NewGameBootstrap` on first save |

**Authoring rules:** [dungeons — warp gates](dungeons-and-encounters.md#stratum-entry--warp-gates-locked), [campaign S1 intro](campaign/s1-intro.md), [ADR 040 — exit links](../../decisions/040-floor-exit-topology-graph.md). At launch: only `s1` uses `partyEntryPoint` (spawn start) + blockers; `s2+` adds `hasWarpGate`.

**Chest / gather:** `IsWalkable=false` + `HasChest` + `ChestConfig[]` on floor asset (orthogonally adjacent interact while **facing** chest — [#105](https://github.com/miramocha/griddungeon-game/issues/105)); opened state in `CampaignSaveData.OpenedChestIds` (fixed item + quantity, not loot table); `HasGatherNode` + `lootTableId` on walkable gather cells.

---

## Asset layout (`Assets/Content/`)

Author new instances under the folder matching the SO type in the table above. Subfolders mirror content domain (`Classes/`, `Skills/`, `Enemies/`, `EncounterGroups/`, `Floors/`, …). `ContentDatabase` aggregates references — not a separate on-disk tree.

---

## Related docs

- [Content IDs (locked)](content-ids.md)
- [03 — Content index](README.md)
- [05 — Class design](../05-class-design.md) — assemblies, Core DTO mapping, runtime types
- [Launch class skills](class-skills.md)
- [Stratum 1 enemy roster](enemy-roster.md)
