---
tags:
  - path/docs
  - type/dev
  - scope/required
  - status/accepted
  - domain/phase
---
# Class Design

C# **assembly map** and **shipped type inventory** for the default build. Suffix rules (`*View`, `*Coordinator`, partial seams): [class naming patterns](04-dev/class-naming-patterns.md).

Code: [griddungeon-game](https://github.com/miramocha/griddungeon-game) ([Assets/Scripts/README.md](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/README.md)). Locked IDs and SO schema: [03 — Content](03-content/README.md). Rules and acceptance: [system docs](02-systems/) and [ADRs](../decisions/).

Derived from [tech notes](04-tech-notes.md), [release scope](00-release-scope.md), [ADR 014–016](../decisions/), and locked system docs.

> **Status:** structure locked for required slice; **game phase flow locked** ([ADR 017](../decisions/017-game-phase-controller.md), [game phase](02-systems/game-phase.md)). Naming bikesheds resolve in the game repo, not here.

---

## Architecture — design goals

| Goal | How architecture supports it |
|------|--------------------------------|
| **Test damage + AGI without Unity** | `GridDungeon.Core` simulators + `GridDungeon.Tests` (mostly Core; Runtime when wiring needs it) |
| **Hub → explore → combat loop** | `GamePhaseController` + three `IPhaseController`s ([game phase](02-systems/game-phase.md)) |
| **Spec-locked combat** | `CombatController` + `TurnQueue` + `EndOfRoundPipeline`; combat sub-phases not on `GamePhase` |
| **Content in data, not code** | ScriptableObjects in Runtime; **Core DTOs** (`SkillData`, `StatusData`, …) at simulator boundaries — [content schema](03-content/content-schema.md) |
| **FOE + map + flee rules** | `ExplorationPhaseController` wires explorer events; `RetreatCellCalculator` + `FoeFleeRetreatPlacement` in Core |
| **Phase vs presentation** | C# owns transitions; optional UVS later listens to `PhaseChanged` only ([ADR 017](../decisions/017-game-phase-controller.md)) |

Phase diagrams, exploration/combat sequences, and Enter/Exit checklists: **[game phase](02-systems/game-phase.md)**.

**Cursor rules:** Shared Unity principles from `griddungeon-game` (hard-linked under [`.cursor/rules/`](../.cursor/rules/)); architecture-specific mapping in [`architecture-design-principles.mdc`](../.cursor/rules/architecture-design-principles.mdc). **Type suffix patterns** (`*View`, `*Presenter`, `*Coordinator`, Core simulators): [class naming patterns](04-dev/class-naming-patterns.md) + [`unity-csharp-class-suffix-patterns.mdc`](../.cursor/rules/unity-csharp-class-suffix-patterns.mdc).

---

## Assembly structure

Four assemblies with a strict dependency direction:

```mermaid
flowchart BT
  T[GridDungeon.Tests]
  UI[GridDungeon.UI]
  R[GridDungeon.Runtime]
  Camp[GridDungeon.Campaign]
  C[GridDungeon.Core]
  T --> C
  T --> Camp
  T --> R
  UI --> R
  R --> Camp
  R --> C
  Camp --> C
```

```
GridDungeon.Core       (pure C#, no UnityEngine)
    ^
GridDungeon.Campaign   (S1 policy + story behavior; references Core)
    ^
GridDungeon.Runtime    (MonoBehaviours, ScriptableObjects)
    ^
GridDungeon.UI         (UI Toolkit views, input handlers)

GridDungeon.Tests      (NUnit, references Core + Runtime; domain folders — game repo Assets/Tests/README.md)
```

| Assembly | `asmdef` path | Notes |
|----------|---------------|-------|
| `GridDungeon.Core` | `Assets/Scripts/Core/GridDungeon.Core.asmdef` | No `UnityEngine` refs; simulators + DTOs ([improvement plan](plans/core-assembly-improvement-plan.md)) |
| `GridDungeon.Campaign` | `Assets/Scripts/Campaign/GridDungeon.Campaign.asmdef` | S1 campaign + story behavior; references Core only |
| `GridDungeon.Runtime` | `Assets/Scripts/Runtime/GridDungeon.Runtime.asmdef` | References Core + Campaign |
| `GridDungeon.UI` | `Assets/Scripts/UI/GridDungeon.UI.asmdef` | References Runtime; UI Toolkit bindings |
| `GridDungeon.Tests` | `Assets/Tests/GridDungeon.Tests.asmdef` | References Core + Campaign + Runtime; Edit Mode layout in game repo [Assets/Tests/README.md](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Tests/README.md) |

**Do not put campaign/story behavior in Core** — stratum resolvers, story executors, trigger catalogs, and S1 flag policy live in `GridDungeon.Campaign`. Core keeps DTOs and neutral models only. Enforced in PR review: [unity-core-campaign-assembly.mdc](../.cursor/rules/unity-core-campaign-assembly.mdc).

---

## Enums & value types (Core)

Defined in `GridDungeon.Core/Enums/` (and related Core folders). Shared across all layers.

| Enum | Values |
|------|--------|
| `GamePhase` | `Hub`, `Exploration`, `Combat` |
| `FacingDirection` | `North`, `East`, `South`, `West` |
| `CombatantKind` | `Core`, `Summon`, `Guest`, `Enemy` |
| `FormationRow` | `Front`, `Back` |
| `SkillType` | `Physical`, `Elemental`, `Heal`, `Buff`, `Debuff`, `Deploy`, `Passive` |
| `DamageElement` | `None`, `Slash`, `Pierce`, `Fire`, `Ice`, `Volt` |
| `BodyPart` | `None`, `Head`, `Arm`, `Leg` |
| `BattleResult` | `Victory`, `Wipe`, `Flee` |
| `StatusCategory` | `Control`, `BindLimb`, `DoT`, `StatBuff`, `StatDebuff`, `BattleMod` |
| `SkillPresentation` | `Fixed`, `Cinematic`, `CinematicQTE` (launch uses `Fixed` only for class skills) |
| `EquipSlot` | `Weapon`, `Head`, `Body`, `Legs`, `Accessory` |
| `ItemEffectType` | `HealHp`, `HealMp`, `CureAilment`, `ReviveAlly`, `Identify` |
| `LootResolveMode` | `IndependentEntries`, `PickOneWeighted` |
| `ProtocolEffectType` | `DamageAllEnemies`, `HealAllAllies` |
| `FloorExitDirection` | `Up`, `Down` |
| `FloorExitTargetKind` | `Hub`, `Floor` |
| `FeatureType` | `StairsDown`, `StairsUp`, `Door`, `Chest`, `GatherNode`, `JumpPad`, `HeightStairs` |
| `CombatPhase` | `Idle`, `CommandPlanning`, `TurnPhase`, `EndOfRound` |
| `CombatCommand` | `Attack`, `Guard`, `Skill`, `Item`, `Protocol`, `Flee` |
| `ExplorationAnimationSpeed` | `Slow`, `Normal`, `Fast`, `VeryFast` |
| `ExplorationMapKind` | `Stratum`, `SideDungeon` (optional side dungeons — [ADR 022](../decisions/022-side-dungeons-mvp3.md)) |

**Value structs:** `GridPosition` (X, Y, Level — [ADR 019](../decisions/019-floor-verticality.md)), `CellEdge`, `CharacterBaseStats`, `TargetingRule`, `StatusInflict`, `ElementResistances`, `FloorExitLink`, `FloorTileData`, `FoeSpawnConfig`, `StoryEventTriggerConfig` (floor-authored exploration story trigger: cell + `storyEventId` + optional `RequiredFlagsTrue` / `RequiredFlagsFalse`), and other small DTOs in Core — see game repo `Assets/Scripts/Core/`.

---

## Core — models & simulators

No `UnityEngine` dependency. Lives in `GridDungeon.Core`.

### Models

<a id="map-data-model"></a>

| Type | Role |
|------|------|
| `Combatant`, `CombatantStats`, `StatusInstance`, `BattleModifier`, `EquipmentLoadout` | Runtime combatant state |
| `BattleState`, `RoundSnapshot` | Combat-only state owned by `CombatController` |
| `FloorMapState`, `FeatureState`, `WallMask`, `JumpPadData` | Map reveal and features |
| `FoeInstance` | Map FOE entity instance |
| `SaveGame`, `HubSaveData`, `ExplorationStateSave`, related save structs | Persisted game state ([ADR 036](../decisions/036-party-inventory-model.md)) |
| `CombatEntryContext`, `CombatAction`, `CombatActionResult`, `PartyCommandBatch` | Combat entry and queued commands |
| `TurnQueue` | AGI-ordered turn list (Core type; driven by `CombatController`) |

### Content DTOs (no Unity)

Runtime `ScriptableObject` types stay in `GridDungeon.Runtime`. `ContentDatabase` maps SO → DTO when loading content or starting battle. **Simulators and tests use only DTOs.** SO types and folders: [content schema](03-content/content-schema.md).

| DTO | Source SO |
|-----|-----------|
| `SkillData` | `SkillDefinition` |
| `StatusData` | `StatusDefinition` |
| `NavigatorData` | `NavigatorDefinition` |
| `ProtocolSkillData` | `ProtocolSkillDefinition` |
| `EnemyData` | `EnemyDefinition` |
| `SummonData` | `SummonDefinition` |

### Simulators (stateless, testable)

| Type | Responsibility |
|------|----------------|
| `DamageCalculator` | Physical, elemental, heal formulas |
| `HitChanceCalculator` | Hit chance with blind mod |
| `TurnQueueBuilder` | AGI sort with status effects |
| `FloorExitResolver` | Hub-return / exit-link spawn and facing from `FloorExitLink[]` |
| `EncounterEventEvaluator` | Combat encounter event predicates |
| `StatusSystem` | Apply, refresh, tick, cleanse, skill block checks |
| `ValidTargetCalculator` | Living targets per `TargetingRule` |
| `CombatTargeting` | Player target requirement, resolve, stale check |
| `FleeCalculator` | Flee success percent and roll |
| `RetreatCellCalculator` | Retreat cell from party pose + walkability |
| `FoeFleeRetreatPlacement` | Post-flee grid placement (FOE contact only — [ADR 011](../decisions/011-foe-flee-retreat.md)) |
| `MapRevealCalculator` | Reveal on enter cell and bump |
| `SummonScriptRunner` | Summon action script resolution |
| `InventoryRules`, `InventoryBagCatalog`, `EquipmentStatAggregator` | Bag and equip rules ([ADR 036](../decisions/036-party-inventory-model.md)) |
| `CombatSimulator` | Full round simulation (tests) |
| `GuildPartyRules` | Generic party formation slot rules (no campaign flag writes) |
| `StoryEventTriggerLookup` | Floor trigger cell match + flag gates |

Edit Mode fixtures: [Assets/Tests/README.md](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Tests/README.md).

---

## Runtime — MonoBehaviours & managers

Lives in `GridDungeon.Runtime`. One primary type per system responsibility unless noted.

### Game phase ([ADR 017](../decisions/017-game-phase-controller.md))

Pure C# phase orchestration. **Not** Unity Visual Scripting. Diagrams and Enter/Exit rules: [game phase](02-systems/game-phase.md).

| Type | Role |
|------|------|
| `GamePhaseController` | `TryTransitionTo`, `PhaseChanged` event |
| `IPhaseController` | `OnEnter(from)`, `OnExit(to)` |
| `HubPhaseController` | Hub UI; FOE reset on return from exploration ([ADR 008](../decisions/008-campaign-defaults.md)) |
| `ExplorationPhaseController` | Floor load, explorer/FOE wiring, FPV visibility |
| `CombatPhaseController` | Hide exploration, `StartBattle` / arena teardown |
| `GameState` | Composition root; `RequestTransition`, subsystem refs |

**Transition callers (examples):** `HubController.LeaveHub` → Exploration; FOE contact / `EncounterTrigger` → Combat; `CombatController.OnBattleEnded` → Exploration; wipe → Hub + load save.

### Exploration & map

<a id="exploration"></a>

| Type | Role |
|------|------|
| `DungeonExplorer` | Grid step, facing, interact; `OnPartyStep`, `OnPartyEnteredCell`, `OnBumpWall` |
| `ExplorationAnimationDurations` | Step/turn/bump durations per preset ([ADR 018](../decisions/018-exploration-animation-speed.md)) |
| `DungeonSceneHost` | FPV mount visibility |
| `MapSystem` | `FloorMapState` load/snapshot; reveal on explorer events |
| `FoeSystem` | Spawn, patrol, snapshot, hub reset; `CanRetreatFromFoe` |
| `EncounterTrigger` | Random encounter roll on party step |
| `GatherInteractor` | Gather node interact (instant loot at launch) |

### Party, navigator, protocol

| Type | Role |
|------|------|
| `PartyRuntime` | Six core + two aux slots, Synchro bar mirror |
| `NavigatorRuntime` | Active navigator, unlock roster |
| `AuraSystem` | Passive aura apply/remove |
| `ProtocolSystem` | Synchro gain on core act; Protocol spend at 100% |

### Combat

| Type | Role |
|------|------|
| `CombatController` | Battle lifecycle, command planning, AGI turns, flee |
| `EncounterEventScheduler` | Combat→story rows from `EncounterGroup.Events[]` ([combat § Encounter events](02-systems/combat.md#encounter-events-combat--story)) |
| `CombatScenePresenter` | Arena rig and enemy slot anchors ([combat scene](02-systems/combat-scene.md)) |
| `CombatPresentationGate` | Presentation lock for reactive HUD |
| `EndOfRoundPipeline` | Status ticks and end-of-round log lines |
| `CombatantFactory` | Build `Combatant` from save or `EnemyData` |

S1 tutorial FOE: `EncounterGroupId` `grp_alley_stalker_tutorial` from story `start_combat` or floor FOE spawn; `NoFlee` on `CombatEntryContext` or encounter/enemy defs. Mid-fight unlock VN: `EncounterGroup.Events[]` → `EncounterEventScheduler` ([combat § Encounter events](02-systems/combat.md#encounter-events-combat--story)). Floor spawn metadata: `FoeSpawnConfig.TutorialFirstFoe`, `NoFlee`.

### Hub, codex, content, save

| Type | Role |
|------|------|
| `HubController` | Inn, hospital, shop, guild, navigator office |
| `InnService`, `HospitalService`, `ShopService`, `GuildService`, `NavigatorOffice` | Hub service rules |
| `CodexSystem` | Enemy encounter / weakness / status knowledge |
| `ContentDatabase` | SO lookup + `To*Data` DTO mapping; `CampaignStart`, `NewGameDefaults` |
| `SaveSystem` | Inn save, incremental map/foe/exploration commits |
| `GameBootstrapPhase` | Maps save load result + `CampaignStartConfig` → initial `GamePhase` |
| `FloorPartyEntryBuilder` | Resolves hub-return spawn/facing from `FloorExitResolver` + floor `exitLinks[]` |

---

## Campaign (S1 policy)

Lives in `GridDungeon.Campaign`. References Core only.

| Type | Role |
|------|------|
| `S1CampaignResolver` | S1 floor keys, spawn cells, encounter suppress |
| `HubStratumEntryRules` | Hub stratum entry eligibility (`GuildPartyRules`) |
| `NewGameBootstrap` | Seeds `NewGameDefaults` on empty save (`SaveGameFactory` shell) |
| `StoryEventIds`, `StoryEventTriggerCatalog` | Content IDs and trigger catalog (catalog fallback until floor rows migrated) |
| `ExplorationStoryEventTriggers` | Floor-first resolver with `StoryEventTriggerCatalog` fallback |

**Core (not Campaign):** `StoryEventEffectExecutor`, `StoryEventPlayOnceRules` — effect dispatch + play-once checks. **Runtime:** `StoryEventRunner`, `StoryEventPlayback`.

Authority: [story events](02-systems/story-events.md), [unity-core-campaign-assembly.mdc](../.cursor/rules/unity-core-campaign-assembly.mdc).

---

## UI layer

Lives in `GridDungeon.UI`. UI Toolkit documents + C# presenters. **Reactive HUD at launch:** combat — `CombatHudReactivePresenter` + `CombatPresentationGate` ([#35](https://github.com/miramocha/griddungeon-game/pull/35)); exploration — map marker overlay presenters + `MapGridMarkerAnimator` ([#90](https://github.com/miramocha/griddungeon-game/pull/90)). See [tech notes — UI reactivity](04-tech-notes.md#ui-reactivity), [UI event contract](04-dev/ui-event-contract.md).

### Input routing

| Type | Role |
|------|------|
| `InputRouter` | Binds to `GameState.PhaseChanged`; enables Exploration / Combat / Map / UI action maps |
| `ExplorationInputHandler` | Movement, turn, interact, map toggle |
| `CombatInputHandler` | Commands, protocol menu, target select, confirm/cancel |
| `MapInputHandler` | Pan, zoom, close |

### Shipped views (game repo)

| Concern | Types / assets |
|---------|----------------|
| Exploration HUD | `ExplorationHudView`, `ExplorationMapCoordinator`, `MinimapPanelPresenter`, `ExpandedMapOverlayPresenter` |
| Map markers | `MapPartyMarkerPresenter`, `MapFoeMarkersPresenter`, `MapGatherMarkersPresenter`, `MapGridMarkerAnimator` |
| Combat HUD | `CombatHudView`, `CombatHudReactivePresenter`, `CombatArenaPlateView`, `CombatHudLogView` |
| Party menu | `PartyMenuOverlayView`, `PartyFormationFloaterPresenter`, `PartyFormationGridView` |
| Shared services | `ItemListInventoryPresenter`, `InputHintPresenter`, `CommandRailPresenter`, `CommandRailInfoPresenter`, `ScreenFadePresenter`, `PartyMenuEnvironmentFadePresenter`, `CombatArenaPlatePresenter` — [centralized UI services](04-dev/centralized-ui-services.md) |
| Global input hints | `InputHints`, `TabbedPickerRailHints` |
| Fade facades | `ScreenFades`, `PartyMenuEnvironmentFade` |

**Exploration UI authority:** [exploration UI](02-systems/exploration-ui.md). **Combat UI authority:** [combat](02-systems/combat.md). **Custom pickers:** [custom party UI](04-dev/custom-party-ui.md), [custom skill picker UI](04-dev/custom-skill-picker-ui.md).

### Dev bootstrap HUD

| Asset / type | Path |
|--------------|------|
| `GamePhaseDevHud.uxml`, `GamePhaseDevHud.uss` | `Assets/UI/Screens/Dev/` |
| `GamePhaseDevHudView` | `Assets/Scripts/UI/Dev/` |

Scene menu: **GridDungeon → Scenes → Create Dev Bootstrap** (`DevBootstrap.unity`, not in git).

### Editor tools

| Type | Role |
|------|------|
| `GridDungeonSaveEditorWindow` | Save / campaign flag dev tooling ([PR #84](https://github.com/miramocha/griddungeon-game/pull/84)) |
| `FloorEditorWindow` | Floor Editor → `ExplorationFloor` asset ([ADR 002](../decisions/002-mapping-model.md), [#107](https://github.com/miramocha/griddungeon-game/issues/107)) |
| `FloorEditorFoeSpawnStore`, `FloorEditorStoryEventStore` | Floor Editor parallel stores for FOE spawns and story-event triggers (mode-gated grid overlays) |
| `FloorEditorFoeInspector`, `FloorEditorStoryEventInspector`, `FloorEditorRandomEncountersInspector` | Side-panel editors for FOE / Events / Random Encounters modes |
| `EncounterGroupEditor`, `RandomEncounterTableEditor`, `StoryEventEditor` | UITK `CreateInspectorGUI` content SO inspectors ([unity-editor-ui-toolkit](../.cursor/rules/unity-editor-ui-toolkit.mdc)) |

---

## Key interfaces

`I*` prefix patterns (`I*Host`, `I*View`, `I*Controller`, …): [class naming patterns § Interfaces](04-dev/class-naming-patterns.md#interfaces-common). Shipped contracts worth cross-phase lookup:

| Interface | Role |
|-----------|------|
| `IReadOnlyFloorMapState` | Read-only map state for UI without leaking `MapSystem` internals |
| `ICentralizedUiSurface` | Shared overlay lifecycle vocabulary — [centralized UI services](04-dev/centralized-ui-services.md) |

(`IPhaseController` — see game phase table in [Runtime — Game phase](#game-phase-adr-017) and [game phase](02-systems/game-phase.md).)

---

## Side dungeons (sketch)

**Authority:** [side dungeons](02-systems/side-dungeons.md), [ADR 022](../decisions/022-side-dungeons-mvp3.md). Does **not** change required-slice locked content IDs ([content IDs](03-content/content-ids.md)).

| Concern | Notes |
|---------|-------|
| `ExplorationStateSave.MapKind` | `Stratum` or `SideDungeon` |
| `ExplorationStateSave.LocationId` | Stratum id (`s1`) or side location (`sd01`) |
| `SaveGame.UnlockedSideDungeonIds` | Optional draft field |
| Map / FOE dictionary keys | Stratum: `s1_B1F`; side: `sd01_F1` |

| API | Caller | Phase |
|-----|--------|-------|
| `LeaveHub(stratumId, floorId)` | Hub **Depart** | → Exploration (stratum rules) |
| `EnterSideDungeon(locationId, floorId)` | Hub **Side expedition** | → Exploration (side rules; exit → hub only) |

---

## Moved sections (link compatibility)

<a id="content-definitions-runtime-scriptableobjects"></a>

**Content definitions (ScriptableObjects)** → [content schema](03-content/content-schema.md#content-definitions-runtime-scriptableobjects).

<a id="content-ids-locked"></a>

**Content IDs (locked)** → [content IDs](03-content/content-ids.md#content-ids-locked).

<a id="folder-structure-game-repo"></a>

**Folder layout** → game repo [Assets/Scripts/README.md](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/README.md); content assets → [content schema § asset layout](03-content/content-schema.md#asset-layout-assetscontent).

<a id="skills"></a>

**Skills** — SO types in [content schema](03-content/content-schema.md); IDs in [content IDs](03-content/content-ids.md) and [class skills](03-content/class-skills.md).

<a id="enemies--encounters"></a>

**Enemies & encounters** — [enemy roster](03-content/enemy-roster.md), [dungeons & encounters](03-content/dungeons-and-encounters.md).

---

## Related docs

- [03 — Content](03-content/README.md) — locked IDs, SO schema, rosters
- [Stratum 1 enemy roster](03-content/enemy-roster.md) — locked S1 enemies, groups, skill stubs
- [04 — Tech notes](04-tech-notes.md) — engine stack, save format
- [Release scope](00-release-scope.md) — systems checklist
- [ADR 014 — default exploration & map](../decisions/014-mvp1-exploration-map.md)
- [ADR 015 — default combat](../decisions/015-mvp1-combat.md)
- [ADR 016 — Summon control](../decisions/016-summon-control-mvp1.md)
- [ADR 017 — Game phase controller](../decisions/017-game-phase-controller.md)
- [Game phase](02-systems/game-phase.md)
- [Combat](02-systems/combat.md)
- [Combat status & buffs](02-systems/combat-status-and-buffs.md)
- [Party & classes](02-systems/party-and-classes.md)
- [Launch class skills](03-content/class-skills.md)
- [Character progression](02-systems/character-progression.md)
- [FOE encounters](02-systems/foe-encounters.md)
- [Side dungeons](02-systems/side-dungeons.md)
- [ADR 022 — Side dungeons](../decisions/022-side-dungeons-mvp3.md)
- [Navigator](02-systems/navigator.md)
- [Synchro Protocol](02-systems/synchro-protocol.md)
