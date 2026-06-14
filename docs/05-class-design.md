# Class Design ù MVP1

Concrete classes, interfaces, and enums for the MVP1 implementation. Derived from [tech notes](04-tech-notes.md), [MVP1 spec](archive/mvp1-spec.md), [ADR 014ù016](../decisions/), and all locked system docs.

> **Status:** design draft ù structure locked for MVP1; **game phase flow locked** ([ADR 017](../decisions/017-game-phase-controller.md), [game phase](02-systems/game-phase.md)); other naming open for bikeshedding before first `.cs` files commit.

---

## MVP1 architecture ù design goals

| Goal | How architecture supports it |
|------|--------------------------------|
| **Test damage + AGI without Unity** | `GridDungeon.Core` simulators + `GridDungeon.Tests` (mostly Core; Runtime when wiring needs it) |
| **Hub ? explore ? combat loop** | `GamePhaseController` + three `IPhaseController`s ([game phase](02-systems/game-phase.md)) |
| **Spec-locked combat** | `CombatController` + `TurnQueue` + `EndOfRoundPipeline`; combat sub-phases not on `GamePhase` |
| **Content in data, not code** | ScriptableObjects in Runtime; **Core DTOs** (`SkillData`, `StatusData`, ù) at simulator boundaries |
| **FOE + map + flee rules** | `ExplorationPhaseController` wires explorer events; `RetreatCellCalculator` + `FoeFleeRetreatPlacement` in Core |
| **Phase vs presentation** | C# owns transitions; optional UVS later listens to `PhaseChanged` only ([ADR 017](../decisions/017-game-phase-controller.md)) |

Phase diagrams, exploration/combat sequences, and Enter/Exit checklists: **[game phase](02-systems/game-phase.md)**.

**Cursor rules:** Shared Unity principles from `griddungeon-game` (hard-linked under [`.cursor/rules/`](../.cursor/rules/)); architecture-specific mapping in [`architecture-design-principles.mdc`](../.cursor/rules/architecture-design-principles.mdc).

---

## Assembly structure

Four assemblies with a strict dependency direction:

```mermaid
flowchart BT
  T[GridDungeon.Tests]
  UI[GridDungeon.UI]
  R[GridDungeon.Runtime]
  C[GridDungeon.Core]
  T --> C
  T --> R
  UI --> R
  R --> C
```

```
GridDungeon.Core       (pure C#, no UnityEngine)
    ?
GridDungeon.Runtime    (MonoBehaviours, ScriptableObjects)
    ?
GridDungeon.UI         (UI Toolkit views, input handlers)

GridDungeon.Tests      (NUnit, references Core + Runtime; domain folders ù game repo Assets/Tests/README.md)
```

| Assembly | `asmdef` path | Notes |
|----------|---------------|-------|
| `GridDungeon.Core` | `Assets/Scripts/Core/GridDungeon.Core.asmdef` | No `UnityEngine` refs; Edit Mode tests via Unity Test Runner ([improvement plan](plans/core-assembly-improvement-plan.md)) |
| `GridDungeon.Runtime` | `Assets/Scripts/Runtime/GridDungeon.Runtime.asmdef` | References Core |
| `GridDungeon.UI` | `Assets/Scripts/UI/GridDungeon.UI.asmdef` | References Runtime; UI Toolkit bindings |
| `GridDungeon.Tests` | `Assets/Tests/GridDungeon.Tests.asmdef` | References Core + Runtime; Edit Mode layout in game repo [Assets/Tests/README.md](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Tests/README.md) |

---

## Enums & value types (Core)

Defined in `GridDungeon.Core`. Shared across all layers.

```csharp
enum GamePhase       { Hub, Exploration, Combat }
enum FacingDirection { North, East, South, West }
enum CombatantKind   { Core, Summon, Guest, Enemy }
enum FormationRow    { Front, Back }
enum SkillType       { Physical, Elemental, Heal, Buff, Debuff, Deploy, Passive }
enum DamageElement   { None, Slash, Pierce, Fire, Ice, Volt }
enum BodyPart        { None, Head, Arm, Leg }
enum BattleResult    { Victory, Wipe, Flee }

// Status categories ù mirrors StatusDefinition.category
enum StatusCategory  { Control, BindLimb, DoT, StatBuff, StatDebuff, BattleMod }

// Skill presentation ù MVP1 only uses Fixed
enum SkillPresentation { Fixed, Cinematic, CinematicQTE }
```

### Value structs

```csharp
readonly struct GridPosition { int X; int Y; int Level; /* + operator, Equals; ADR 019 */ }
readonly struct CellEdge     { GridPosition Cell; FacingDirection Side; }
```

---

## Data layer ù ScriptableObject definitions (Runtime)

All read-only at runtime. Created in the Unity editor and referenced by `ContentDatabase`.

### Character & class

```csharp
// Assets/Content/Classes/
class ClassDefinition : ScriptableObject
{
    string classId;               // "vanguard", "breaker", etc.
    string displayName;
    FormationRow preferredRow;
    CharacterBaseStats baseStats; // HP/MP/STR/TEC/AGI/VIT/LUC at level 1
    float[] statGrowth;           // per-level multipliers
    string[] allowedWeaponTypes;
    SkillTreeLayout skillTree;    // tree of SkillNodeDefinition
}

struct CharacterBaseStats { int Hp, Mp, Str, Tec, Agi, Vit, Luc; }

class SkillNodeDefinition
{
    string skillId;
    int maxRank;
    string[] prerequisiteSkillIds; // must be =1 to unlock this node
}
```

### Skills

```csharp
// Assets/Content/Skills/
class SkillDefinition : ScriptableObject
{
    string skillId;
    string displayName;
    string descriptionEn;         // mechanical summary for picker detail / tooltips ù no exact MP/power/% in prose ([mvp1-class-skills](03-content/class-skills.md), [game #149](https://github.com/miramocha/griddungeon-game/issues/149))
    SkillType skillType;
    DamageElement element;
    BodyPart bodyPartTag;         // which bind blocks this skill
    int mpCost;
    float[] powerByRank;          // index 0 = rank 1
    TargetingRule targeting;
    SkillPresentation presentation;
    string cinematicAssetId;      // when presentation != Fixed; Timeline prefab ref ([ADR 027](../decisions/027-combat-cinematic-timeline-events.md))
    StatusInflict? inflictStatus; // optional on-hit status
    string summonDefinitionId;    // set if skillType == Deploy
    // SkillUseContext flags (Combat / Field) ù ADR 035; picker tabs: default All + SkillType ([ADR 035](../decisions/035-skill-use-picker.md))
    // CinematicQTE: qteBonus multipliers on skill or linked SO ù prompt timing on Timeline markers only
}

struct TargetingRule
{
    TargetKind kind;  // SingleEnemy, AllEnemies, SingleAlly, AllAllies, Self, AuxFront, AuxBack
    bool canTargetBack;
    bool pierce;      // ignores front-row melee restriction
}

struct StatusInflict { string statusId; float chance; int durationOverride; }
```

### Status

```csharp
// Assets/Content/Status/
class StatusDefinition : ScriptableObject
{
    string statusId;
    StatusCategory category;
    int defaultDurationTurns;
    float magnitude;           // e.g. 0.05 for 5% poison, 1.25 for Offense Up
    BodyPart bindPart;         // BindLimb only
    bool removedOnDamage;      // sleep wakes on hit
}
```

### Equipment & items

**Runtime behavior:** [items & inventory](02-systems/items-and-inventory.md) ù [ADR 036](../decisions/036-party-inventory-model.md).

```csharp
// Assets/Content/Equipment/
class EquipmentDefinition : ScriptableObject
{
    string equipId;
    EquipSlot slot;            // Weapon, Head, Body, Legs, Accessory
    string[] allowedClassIds;  // empty = unrestricted
    CharacterBaseStats statBonus;
    StatusResistBonuses resistBonuses;
}

enum EquipSlot { Weapon, Head, Body, Legs, Accessory }

struct StatusResistBonuses
{
    float PoisonRes, SleepRes, PanicRes, BindHeadRes, BindArmRes, BindLegRes;
}

// Assets/Content/Items/
class ItemDefinition : ScriptableObject
{
    string itemId;
    string displayName;
    ItemEffectType effectType;  // HealHp, HealMp, CureAilment, ReviveAlly, Identify
    float power;
    int maxStack;
}

enum ItemEffectType { HealHp, HealMp, CureAilment, ReviveAlly, Identify }
```

### Enemies & encounters

```csharp
// Assets/Content/Enemies/
class EnemyDefinition : ScriptableObject
{
    string enemyId;
    string displayName;
    FormationRow defaultRow;
    CharacterBaseStats stats;
    ElementResistances resistances;
    string[] skillIds;          // enemy skill pool
    LootTable lootTable;
    int xpReward;
    bool noFlee;
    string[] statusImmuneTags;
}

struct ElementResistances
{
    float Slash, Pierce, Fire, Ice, Volt;
    // 1.0 default; 1.5 weak; 0.5 resist; 0.0 null; -0.25 absorb (post-MVP1)
}

struct LootTable { LootEntry[] Entries; }
struct LootEntry  { string itemId; float dropChance; int minQty; int maxQty; }

// Assets/Content/Encounters/
class EncounterGroup : ScriptableObject
{
    string groupId;
    EnemySlotConfig[] frontRow;  // =3 enemy slots
    EnemySlotConfig[] backRow;   // =3 enemy slots
    BattleBackgroundId background;
    bool tutorialUnbeatable;     // enemies cannot die; HP floor at 1
    bool noFlee;
}

struct EnemySlotConfig { string enemyDefinitionId; bool isRequired; }
```

### Navigator & Synchro Protocol

```csharp
// Assets/Content/Navigators/
class NavigatorDefinition : ScriptableObject
{
    string navigatorId;           // "guild_handler"
    string displayName;
    AuraModifiers aura;           // e.g. synchroGainBonus = 0.05
    string[] protocolSkillIds;    // ["protocol_strike", "protocol_mend"]
    string unlockCondition;       // "" = day one; otherwise quest/stratum id
}

struct AuraModifiers { float SynchroGainBonus; /* expand post-MVP1 */ }

class ProtocolSkillDefinition : ScriptableObject
{
    string protocolSkillId;
    string displayName;
    ProtocolEffectType effectType;   // DamageAllEnemies, HealAllAllies, ù
    float power;
    int participantCount;         // how many core must be alive to activate
    string presentationId;
}

enum ProtocolEffectType { DamageAllEnemies, HealAllAllies }
```

### Summons

```csharp
// Assets/Content/Summons/
class SummonDefinition : ScriptableObject
{
    string summonId;              // "scout_drone"
    string displayName;
    CharacterBaseStats stats;
    int durationRounds;
    FormationRow auxRow;
    SummonAction[] actionScript;  // ordered list; loops when exhausted
}

struct SummonAction { string skillId; TargetKind targetPreference; }
```

### Floors & exploration

```csharp
// Assets/Content/Floors/
class ExplorationFloor : ScriptableObject
{
    string locationId;            // "s1", "sd01", ù ù location-neutral ([ADR 040](../../decisions/040-floor-exit-topology-graph.md))
    string floorId;               // "B1F"
    int gridWidth;
    int gridHeight;
    FloorTileData[] tiles;        // flat array [y * width + x]
    FoeSpawnConfig[] foeSpawns;
    EncounterTable randomEncounters;
    float baseEncounterRate;
    FloorExitLink[] exitLinks;    // 0..N exits per floor ù authoritative routing ([ADR 040](../../decisions/040-floor-exit-topology-graph.md))
    GridPosition partyEntryIntro; // Act 1 cold start (optional)
    GridPosition partyEntryGate; // hub re-entry / stratum gate
    TutorialBlocker[] tutorialBlockers; // cleared when s1_tutorial_dive_started
}

enum FloorExitDirection { Up, Down }   // grid markers ^ / v

enum FloorExitTargetKind { Hub, Floor }

struct FloorExitLink
{
    string exitId;                // stable per floor ù graph / painter authoring id
    GridPosition cell;
    FloorExitDirection direction;
    FloorExitTargetKind targetKind;
    string targetFloorKey;        // e.g. "s1_B2F", "sd01_F1"; empty when Hub
    GridPosition targetSpawnCell;
    FacingDirection targetFacing;
}

struct TutorialBlocker
{
    GridPosition cell;            // door edge or cell flag
    string requiredSaveFlag;      // e.g. "s1_tutorial_dive_started"
}

// Chest: IsWalkable=false + ChestItemId; interact adjacent+facing (#105). Gather: HasGatherNode on walkable cell (G).
struct FloorTileData  { bool IsWalkable; WallMask SolidEdges; bool HasGatherNode; string ChestItemId; }
struct FoeSpawnConfig { string foeId; GridPosition spawnCell; GridPosition[] patrolPath; int stepsPerMove; }
struct EncounterTable { EncounterWeight[] Entries; }
struct EncounterWeight { string groupId; float weight; }

// StratumDefinition (ContentDatabase)
class StratumDefinition
{
    string stratumId;
    bool hasWarpGate;             // false for s1
    string warpFloorId;           // entrance floor when hasWarpGate
    GridPosition warpGateCell;
}
```

**Authoring rules:** [dungeons ù warp gates](03-content/dungeons-and-encounters.md#stratum-entry--warp-gates-locked), [campaign S1 intro](03-content/campaign/s1-intro.md), [ADR 040 ù exit links](../../decisions/040-floor-exit-topology-graph.md). MVP1: only `s1` uses `partyEntryIntro` + blockers; `s2+` adds `hasWarpGate`.

---

## Core layer ù models & simulators (pure C#)

No `UnityEngine` dependency. Lives in `GridDungeon.Core`.

### Combatant model

```csharp
class Combatant
{
    string Id;
    string DefinitionId;          // classId or enemyId
    CombatantKind Kind;
    FormationRow Row;
    int SlotIndex;                // 0-2 for core; 0 for aux

    CombatantStats Stats;         // runtime copy; modified each round
    int CurrentHp;
    int CurrentMp;

    List<StatusInstance> Statuses;
    List<BattleModifier> BattleMods;
    List<string> AllocatedSkillIds;
    EquipmentLoadout Equipment;   // null for enemies

    bool IsDead => CurrentHp <= 0;
    bool IsAux  => Kind is CombatantKind.Summon or CombatantKind.Guest;
}

struct CombatantStats { int Hp, Mp, Str, Tec, Agi, Vit, Luc; }

class StatusInstance
{
    string DefinitionId;
    int TurnsRemaining;
    int AppliedRound;
    string SourceCombatantId;
}

class BattleModifier
{
    string ModId;              // "guard", "charge"
    float Magnitude;
    int TurnsRemaining;        // -1 = until consumed
}

class EquipmentLoadout
{
    string WeaponId;
    string HeadId;
    string BodyId;
    string LegsId;
    string AccessoryId;
}
```

### Battle state (combat-only)

Owned by `CombatController` for the duration of a fight. Not a `GamePhase`.

```csharp
class BattleState
{
    Combatant[] CoreSlots;       // 6
    Combatant?[] AuxSlots;       // 2
    Combatant[] EnemySlots;      // 6 max, sparse
    TurnQueue Queue;
    int Round;
    CombatEntryContext Entry;
    bool FleeEnabled;            // retreat cell + encounter noFlee
    float SynchroBar;              // Synchro Charge; copy from PartyRuntime at StartBattle
}

class RoundSnapshot
{
    BattleState State;
    IReadOnlyDictionary<string, SkillData> Skills;
    IReadOnlyDictionary<string, StatusData> Statuses;
}
```

### Core content DTOs (no Unity)

Runtime `ScriptableObject` types stay in `GridDungeon.Runtime`. `ContentDatabase` maps SO ? DTO when loading content or starting battle. **Simulators and tests use only these types.**

```csharp
readonly record struct SkillData(
    string Id, SkillType Type, DamageElement Element, BodyPart BodyPart,
    int MpCost, float Power, TargetingRule Targeting, StatusInflict? Inflict);

readonly record struct StatusData(
    string Id, StatusCategory Category, int DefaultDurationTurns,
    float Magnitude, BodyPart BindPart, bool RemovedOnDamage);

readonly record struct NavigatorData(string Id, AuraModifiers Aura, string[] ProtocolSkillIds);

readonly record struct ProtocolSkillData(
    string Id, ProtocolEffectType EffectType, float Power, int ParticipantCount);

readonly record struct EnemyData(
    string Id, CharacterBaseStats Stats, ElementResistances Resistances,
    string[] SkillIds, bool NoFlee, string[] StatusImmuneTags);

readonly record struct SummonData(
    string Id, CharacterBaseStats Stats, int DurationRounds,
    FormationRow AuxRow, SummonAction[] ActionScript);
```

### Simulators (stateless, testable)

```csharp
static class CombatSimulator
{
    static RoundResult SimulateRound(RoundSnapshot snapshot);
}

static class DamageCalculator
{
    static int CalculatePhysical(Combatant attacker, Combatant defender,
        SkillData skill, IReadOnlyList<BattleModifier> mods);
    static int CalculateElemental(Combatant attacker, Combatant defender,
        SkillData skill, ElementResistances resistances);
    static int CalculateHeal(Combatant caster, SkillData skill);
}

static class HitChanceCalculator
{
    static float Calculate(Combatant attacker, Combatant defender, float blindMod = 0f);
}

static class TurnQueueBuilder
{
    static List<Combatant> Build(IEnumerable<Combatant> combatants,
        IReadOnlyDictionary<string, StatusData> statuses);
}

static class StatusSystem
{
    static void Apply(Combatant target, StatusInstance instance, StatusData def);
    static void Refresh(Combatant target, string statusId, int newDuration);
    static void Tick(Combatant target, IReadOnlyDictionary<string, StatusData> defs);
    static void Cleanse(Combatant target, StatusCategory category);
    static bool IsBlocked(Combatant actor, SkillData skill);
}

static class InventoryRules { /* TryAdd, TryEquip, bag-full ù ADR 036 */ }
static class InventoryBagCatalog { /* tab filter for party bag UI */ }
static class EquipmentStatAggregator { /* worn bonuses ? CombatantStats */ }

static class ValidTargetCalculator
{
    static IReadOnlyList<Combatant> GetValidTargets(
        BattleState state, TargetingRule rule, bool actorTargetsEnemies);
    // Front-row preference for melee; CanTargetBack / Pierce per skill ù [#56](https://github.com/miramocha/griddungeon-game/issues/56) row-collapse follow-up
}

static class CombatTargeting
{
    static bool RequiresPlayerTarget(CombatAction action, IReadOnlyDictionary<string, SkillData> skills);
    static Combatant? ResolveLivingTarget(BattleState state, CombatAction action, ...);
    static bool IsQueuedTargetStale(BattleState state, CombatAction action, ...);
}

static class FleeCalculator
{
    static float ComputeSuccessPercent(BattleState state);  // clamp 5..95
    static bool RollSuccess(BattleState state, Func<float> rollPercent);
}

static class RetreatCellCalculator
{
    static GridPosition GetRetreatCell(GridPosition partyCell, FacingDirection facing);
    static bool IsRetreatCellWalkable(GridPosition retreatCell, FloorCollisionQuery collision);
}

static class FoeFleeRetreatPlacement
{
    // Post-combat grid cell after flee ù FOE contact only (ADR 011)
    static bool TryResolvePostFleeCell(BattleResult result, CombatEntryContext entry,
        GridPosition partyCell, FloorCollisionQuery isWalkable, out GridPosition placementCell);
}

static class MapRevealCalculator
{
    static IEnumerable<CellEdge> RevealOnEnterCell(GridPosition cell, int gridWidth, int gridHeight);
    static IEnumerable<CellEdge> RevealOnBump(GridPosition fromCell, FacingDirection bumpSide);
}

static class SummonScriptRunner
{
    static CombatAction ResolveNext(SummonData summon, int turnIndex, BattleState state);
}
```

### Map data model

```csharp
class FloorMapState
{
    string FloorKey;              // "s1_B1F"
    bool[,] Visited;
    WallMask[,] Walls;            // per-cell bitmask: N/E/S/W revealed
    Dictionary<GridPosition, FeatureState> Features;
    Dictionary<GridPosition, string> FoeIcons; // last known foe id
}

[Flags] enum WallMask { None = 0, North = 1, East = 2, South = 4, West = 8 }

class FeatureState
{
    FeatureType Type;              // Stairs, Door, Chest, GatherNode
    bool IsInteracted;             // door opened, chest looted
}

enum FeatureType { StairsDown, StairsUp, Door, Chest, GatherNode, JumpPad, HeightStairs }

class JumpPadData { int DeltaForward; int DeltaLevel; }   // e.g. 2 forward, +1 level
```

### FOE instance

```csharp
class FoeInstance
{
    string FoeId;
    string EncounterGroupId;
    GridPosition Cell;
    int PatrolPathIndex;
    bool IsAlive;
    int Tier;                      // used for XP/drop scaling
}
```

### Save data model

```csharp
[Serializable] class SaveGame
{
    HubSaveData Hub;
    CharacterSaveData[] Party;     // 6 characters; each row includes EquipmentLoadout
    PartyInventory Inventory;      // fixed bag slots ù ADR 036
    string ActiveNavigatorId;
    float SynchroBar;
    Dictionary<string, FloorMapStateSave> Maps;   // key: "s1_B1F"
    Dictionary<string, FoeStateSave[]>   FoeState;
    ExplorationStateSave? Exploration;             // null when in hub
}

[Serializable] struct HubSaveData
{
    int Gold;
    HashSet<string> UnlockedWarpGateStrata;       // stratumIds hub may Enter (warp gate unlocked in-world); s1 via campaign flag
}

[Serializable] struct ExplorationStateSave
{
    string StratumId;
    string FloorId;
    GridPosition PartyCell;
    FacingDirection Facing;
}
```

---

## Runtime layer ù MonoBehaviours & managers

Lives in `GridDungeon.Runtime`. One `MonoBehaviour` per system responsibility.

### Game phase (macro flow) ù [ADR 017](../decisions/017-game-phase-controller.md)

Pure C# phase orchestration. **Not** Unity Visual Scripting. See [game phase](02-systems/game-phase.md) for diagrams and Enter/Exit rules.

```csharp
// Core/Enums/GamePhase.cs
enum GamePhase { Hub, Exploration, Combat }

// Runtime/Game/GamePhaseController.cs ù plain C# (not MonoBehaviour)
sealed class GamePhaseController
{
    GamePhase Current { get; private set; }
    event Action<GamePhase, GamePhase> PhaseChanged;  // (previous, next)

    bool TryTransitionTo(
        GamePhase next,
        IReadOnlyDictionary<GamePhase, IPhaseController> controllers);
}

interface IPhaseController
{
    void OnEnter(GamePhase from);
    void OnExit(GamePhase to);
}

sealed class HubPhaseController : IPhaseController
{
    HubController Hub;
    // OnEnter(from): hub UI; if from == Exploration ? FOE reset (ADR 008), ClearExplorationState
    // OnExit: hide hub UI
}

sealed class ExplorationPhaseController : IPhaseController
{
    DungeonExplorer Explorer;
    DungeonView View;
    MapSystem Map;
    FoeSystem Foes;
    EncounterTrigger Encounters;
    // OnEnter: load floor, subscribe Explorer/Foe events, show FPV
    // OnExit: unsubscribe all exploration listeners
}

sealed class CombatPhaseController : IPhaseController
{
    CombatController Combat;
    CombatScenePresenter Scene;
    DungeonView View;
    // OnEnter: hide/dim exploration, StartBattle(context)
    // OnExit: teardown arena, Combat.EndBattle cleanup
}
```

### GameState (composition root)

```csharp
// Single instance on a persistent "Game" GameObject
sealed class GameState : MonoBehaviour
{
    GamePhase Current => _phases.Current;

    GamePhaseController _phases;
    HubPhaseController _hubPhase;
    ExplorationPhaseController _explorePhase;
    CombatPhaseController _combatPhase;

    // Shared subsystems (serialized or injected)
    HubController Hub;
    DungeonExplorer Explorer;
    DungeonView View;
    CombatController Combat;
    MapSystem Map;
    FoeSystem Foes;
    PartyRuntime Party;
    NavigatorRuntime Navigator;
    ProtocolSystem Protocol;
    CodexSystem Codex;
    ContentDatabase Content;
    SaveSystem Save;

    bool RequestTransition(GamePhase phase);  // delegates to _phases.TryTransitionTo

    // UI / systems subscribe here or to _phases.PhaseChanged
    event Action<GamePhase, GamePhase> PhaseChanged;
}
```

**Transition callers (examples):** `HubController.LeaveHub` ? Exploration; `FoeSystem.OnFoeContact` / `EncounterTrigger` ? Combat; `CombatController.OnBattleEnded` ? Exploration; wipe flow ? Hub + load save.

### Exploration

```csharp
class DungeonExplorer : MonoBehaviour
{
    [SerializeField] Transform m_poseRoot; // scene "PartyPose"; grid ? world ù see dungeon navigation ù Party pose

    GridPosition Cell    { get; private set; }
    FacingDirection Facing { get; private set; }

    // Called by ExplorationInputHandler (hold IsPressed; repeat after lerp ù ADR 001)
    void TryStepForward();   // WASD displacement
    void TryStepBack();
    void TryStrafeLeft();
    void TryStrafeRight();
    void TryTurnLeft();      // A/D ù hold repeat after turn lerp; no step events
    void TryTurnRight();
    void TryInteract();
    void StopMovement();     // kill tweens on combat exit
    event Action AnimationCompleted;  // input re-checks hold for repeat
    // Lerp durations from ExplorationAnimationDurations (ADR 018 preset)

    // Fired after each successful step; FoeSystem listens to advance patrol
    event Action OnPartyStep;
    // Fired when party enters a new cell; MapSystem listens
    event Action<GridPosition> OnPartyEnteredCell;
    // Fired when step blocked by wall; MapSystem listens
    event Action<FacingDirection> OnBumpWall;
}

enum ExplorationAnimationSpeed { Slow, Normal, Fast, VeryFast }

static class ExplorationAnimationDurations
{
    static (float step, float turn, float bumpSegment) Get(ExplorationAnimationSpeed speed);
    // Normal: 0.32s / 0.26s / 0.10s ù see ADR 018
}

class DungeonView : MonoBehaviour
{
    void SetVisible(bool visible);
    void RenderCell(GridPosition cell, FacingDirection facing);
}
```

### Map system

```csharp
class MapSystem : MonoBehaviour
{
    FloorMapState CurrentFloor { get; private set; }

    void LoadFloor(string floorKey, FloorMapStateSave? saved);
    FloorMapStateSave Snapshot();

    // Driven by DungeonExplorer events
    void OnPartyEnteredCell(GridPosition cell);
    void OnBumpWall(FacingDirection side);

    // Returns current party cell's revealed map for UI binding
    IReadOnlyFloorMapState GetReadOnly();
}
```

### FOE system

```csharp
class FoeSystem : MonoBehaviour
{
    IReadOnlyList<FoeInstance> ActiveFoes { get; }

    void LoadFloor(string stratumId, string floorId, FoeStateSave[]? saved);
    FoeStateSave[] Snapshot();
    void ResetFloor(string stratumId, string floorId);  // called on hub return (ADR 008)

    // Listens to DungeonExplorer.OnPartyStep
    void OnPartyStep();

    // Delegates to RetreatCellCalculator (Core); used for flee UI enable
    bool CanRetreatFromFoe(GridPosition fightAnchor, FacingDirection facing);

    event Action<FoePatrolMove> OnFoePatrolMoved;   // map FOE marker slide
    event Action OnFoePresenceChanged;            // marker layer refresh
    // FOE contact ? combat: ExplorationPhaseController (no public OnFoeContact today)
    // Target / deferred: event Action<FoeInstance> OnFoeContact; OnFoeVisible;
}

class EncounterTrigger
{
    // Called from ExplorationPhaseController on DungeonExplorer.OnPartyStep
    // After FoeSystem handles contact; no random roll if combat already requested
    bool TryRollRandomEncounter(EncounterTable table, float baseEncounterRate,
        out string encounterGroupId);
}

class GatherInteractor
{
    // TryInteract on gather node ù instant loot (MVP1, no minigame)
    bool TryGather(GridPosition cell, FloorMapState map, PartyRuntime party);
}
```

### Party runtime

```csharp
class PartyRuntime : MonoBehaviour
{
    // Read from SaveGame; mutated by hub services and combat
    Combatant[] CoreSlots   { get; }   // length 6
    Combatant?[] AuxSlots   { get; }   // length 2 (front/back); null = empty
    string ActiveNavigatorId { get; set; }
    float SynchroBar           { get; set; }  // Synchro Charge 0..1

    // All combatants eligible for AGI queue (core + non-null aux + enemies added by CombatController)
    IReadOnlyList<Combatant> AllPartyCombatants { get; }

    // Called by GuildService; updates slot assignment
    void AssignCoreSlot(int slot, Combatant character);

    // Called by CombatController at battle start/end
    void SpawnAux(SummonDefinition def, FormationRow row);
    void DismissAux(FormationRow row);
}
```

### Navigator runtime

```csharp
class NavigatorRuntime : MonoBehaviour
{
    NavigatorDefinition ActiveDefinition { get; private set; }
    IReadOnlyList<string> UnlockedNavigatorIds { get; }

    void SetActiveNavigator(string navigatorId);
    void UnlockNavigator(string navigatorId);
}

static class AuraSystem
{
    static void ApplyPassives(IReadOnlyList<Combatant> coreSix, NavigatorData nav);
    static void RemovePassives(IReadOnlyList<Combatant> coreSix);
}
```

### Synchro Protocol system

```csharp
class ProtocolSystem : MonoBehaviour
{
    // Called by CombatController after each core combatant action (below 100%)
    void OnCoreActed(Combatant actor, NavigatorDefinition nav);

    // Core turn when Synchro Charge == 1: CombatCommand.Protocol + skill id
    bool TryUseProtocolSkill(string protocolSkillId, out ProtocolSkillData skill);

    void SpendBar();   // ? 0 after Protocol use
}
```

### Combat controller

```csharp
class CombatController : MonoBehaviour
{
    BattleState State { get; }
    CombatPhase CurrentPhase { get; private set; }

    void StartBattle(CombatEntryContext context);
    void EndBattle(BattleResult result);

    // Command planning + UI command handlers
    bool IsCommandPlanning { get; }
    Combatant? CommandTarget { get; }
    void SubmitPlayerAction(CombatAction action);   // queues during CommandPlanning
    void SelectCommandTarget(Combatant core);       // roster re-select ù #58 follow-up
    bool CanStepBackCommandPlanning { get; }
    void StepBackCommandPlanning();              // R / Esc ù Back (LIFO) ù game #61
    void SubmitFlee();

    // Events + command methods for HUD: 04-dev/ui-event-contract.md (keep in sync with game repo)
}

enum CombatPhase { Idle, CommandPlanning, TurnPhase, EndOfRound }

class PartyCommandBatch   // Core ù queued commands keyed by combatant id
{
    void Assign(Combatant core, CombatAction action);
    void Remove(string combatantId);   // StepBackCommandPlanning pop ù game #61
    bool TryGet(string combatantId, out CombatAction action);
    // AllLivingCoresAssigned, FirstUnassigned, ù
}

// Protocol: CombatCommand.Protocol + SkillId (protocol_strike / protocol_mend) on core turn when Synchro == 1

class CombatEntryContext
{
    FoeInstance? Foe;          // null = random encounter
    string EncounterGroupId;
    string BattleBackgroundId;
    GridPosition FightAnchor;
    FacingDirection PartyFacing;
    bool NoFlee;
    bool IsFoeContactFight => Foe != null;
    // FOE contact + successful flee ? party steps back one cell (ADR 011); random fights stay put
    bool ShouldMovePartyToRetreatCell(BattleResult result);
}
// S1 tutorial FOE: identify by EncounterGroupId (grp_alley_stalker_tutorial) via CombatTutorialHudRules.IsS1FirstFoeTutorial.
// Floor spawn flag: FoeSpawnConfig.TutorialFirstFoe. Content: EncounterGroup.tutorialUnbeatable, NoFlee on entry.
// Deprecated sketch: enum TutorialCombatKind on CombatEntryContext ù do not add.

class CombatAction
{
    CombatCommand Command;     // Attack, Guard, Skill, Item, Flee
    string? SkillId;
    string? ItemId;
    string? TargetId;          // combatant id
}

enum CombatCommand { Attack, Guard, Skill, Item, Protocol, Flee }

class CombatActionResult
{
    Combatant Actor;
    Combatant? Target;
    bool Hit;
    int DamageDealt;
    int HealingDone;
    string? StatusApplied;
    string? StatusCleansed;
    bool TargetDied;
    float SynchroBarDelta;
}
```

### Turn queue (used by CombatController internally)

```csharp
class TurnQueue
{
    IReadOnlyList<Combatant> Ordered { get; }   // sorted AGI order for UI strip
    Combatant Current { get; }
    void Advance();
    bool IsEmpty { get; }
}
```

### End-of-round pipeline

```csharp
// Invoked by CombatController after last AGI turn
class EndOfRoundPipeline
{
    // Returns log entries for combat log
    IEnumerable<string> Execute(
        IReadOnlyList<Combatant> allCombatants,
        IReadOnlyDictionary<string, StatusData> statusDefs,
        int round);
}
```

### Hub controller & services

```csharp
class HubController : MonoBehaviour
{
    InnService         Inn;
    HospitalService    Hospital;
    ShopService        Shop;
    GuildService       Guild;
    NavigatorOffice    NavOffice;

    void EnterHub();
    void LeaveHub(string destStratumId, string destFloorId);
    // MVP3 ù see ù MVP3 side dungeons sketch
    void EnterSideDungeon(string locationId, string floorId);
}

class InnService
{
    void SaveGame();             // writes SaveSystem; restores HP/MP to full
}

class HospitalService
{
    int GetHealCost(PartyRuntime party);
    void HealParty(PartyRuntime party);      // full HP/MP + cleanse all ailments
    int GetReviveCost(Combatant character);
    void Revive(Combatant character);
}

class ShopService
{
    IReadOnlyList<EquipmentDefinition> Stock { get; }
    IReadOnlyList<ItemDefinition>      ItemStock { get; }
    void Buy(string id, PartyRuntime party);
    void Sell(string id, PartyRuntime party);
    void Identify(string equipId, PartyRuntime party);
}

class GuildService
{
    IReadOnlyList<Combatant> Roster { get; }
    void CreateCharacter(string name, string classId, string portraitId);
    void AssignToParty(string characterId, int coreSlot);
    /// <summary>Hub or exploration party menu ù [ADR 034](../decisions/034-skill-point-allocation-outside-combat.md).</summary>
    void AllocateSkillPoint(string characterId, string skillId);
}

class NavigatorOffice
{
    IReadOnlyList<NavigatorDefinition> AvailableNavigators { get; }
    void SetActiveNavigator(string navigatorId);
}
```

### Codex system

```csharp
class CodexSystem : MonoBehaviour
{
    void RecordEncounter(string enemyId);
    void RecordWeakness(string enemyId, DamageElement element);
    void RecordStatus(string enemyId, string statusId, bool immune);
    bool IsWeaknessKnown(string enemyId, DamageElement element) ;
    bool HasEncountered(string enemyId);
}
```

### Content database

```csharp
// Single ScriptableObject; populated in editor via asset references
class ContentDatabase : ScriptableObject
{
    // Runtime SO lookup (editor assets)
    EnemyDefinition      GetEnemy(string id);
    EncounterGroup       GetEncounterGroup(string id);
    ExplorationFloor         GetFloor(string locationId, string floorId);
    SkillDefinition      GetSkill(string id);
    ClassDefinition      GetClass(string classId);
    StatusDefinition     GetStatus(string statusId);
    NavigatorDefinition  GetNavigator(string navigatorId);
    ProtocolSkillDefinition GetProtocolSkill(string skillId);
    SummonDefinition     GetSummon(string summonId);
    EquipmentDefinition  GetEquipment(string equipId);
    ItemDefinition       GetItem(string itemId);

    // Core DTO mapping (call before simulators / combat start)
    SkillData      ToSkillData(SkillDefinition so);
    StatusData     ToStatusData(StatusDefinition so);
    NavigatorData  ToNavigatorData(NavigatorDefinition so);
    ProtocolSkillData ToProtocolSkillData(ProtocolSkillDefinition so);
    EnemyData      ToEnemyData(EnemyDefinition so);
    SummonData     ToSummonData(SummonDefinition so);
}
```

### Save system

```csharp
class SaveSystem : MonoBehaviour
{
    SaveGame Current { get; private set; }

    void SaveAtInn(PartyRuntime party, NavigatorRuntime nav,
                   MapSystem map, FoeSystem foes);
    void LoadLastSave();

    // Incremental map/foe save during dive (not persisted until inn)
    void CommitMapState(string floorKey, FloorMapStateSave state);
    void CommitFoeState(string floorKey, FoeStateSave[] foes);
    void CommitExplorationState(ExplorationStateSave state);
    void ClearExplorationState();  // called on hub return
}
```

---

## UI layer

Lives in `GridDungeon.UI`. UI Toolkit documents + C# controllers. **Reactive HUD (MVP1):** combat ù `CombatHudReactivePresenter` + `CombatPresentationGate` ([#35](https://github.com/miramocha/griddungeon-game/pull/35)); exploration ù **map marker overlay presenters** + `MapGridMarkerAnimator` ([#90](https://github.com/miramocha/griddungeon-game/pull/90)); hub service motion still target. See [tech notes ù UI reactivity](04-tech-notes.md#ui-reactivity), [combat](02-systems/combat.md#ui-motion--feedback), [mapping](02-systems/mapping.md#map-ui-motion), [exploration UI](02-systems/exploration-ui.md). **Integrator / external HUD:** [UI event contract](04-dev/ui-event-contract.md) (runtime events + examples).

### Input routing

```csharp
// GridDungeon.UI ù subscribes to GameState.PhaseChanged on enable
class InputRouter : MonoBehaviour
{
    void Bind(GameState gameState);  // PhaseChanged += OnPhaseChanged
    void OnPhaseChanged(GamePhase previous, GamePhase next);
    // Enables/disables Input System maps: Exploration, Combat, Map, UI
}

// Stateless handlers ù convert raw actions to system calls
class ExplorationInputHandler
{
    void OnMoveForward(); void OnMoveBack();
    void OnStrafeLeft(); void OnStrafeRight();
    void OnTurnLeft(); void OnTurnRight();
    void OnInteract();
    void OnToggleMap();
}

class CombatInputHandler
{
    void OnCommand(int slot);    // Z/X/C/V/B ? Attack/Guard/Skill/Item/Flee
    void OnProtocolMenu();       // U when Synchro == 100% on core turn
    void OnSelectTarget(string combatantId);
    void OnConfirm(); void OnCancel();
}

class MapInputHandler
{
    void OnPan(Vector2 delta);
    void OnZoom(float delta);
    void OnClose();
}
```

### Dev phase HUD (bootstrap scene)

UI Toolkit panel for **issue #1** macro-phase smoke test. Not shipped in production UI.

| Asset / type | Path |
|--------------|------|
| `GamePhaseDevHud.uxml`, `GamePhaseDevHud.uss` | `Assets/UI/Screens/Dev/` (BEM: `game-phase-dev`, `game-phase-dev__button`, ù) |
| `GamePhaseDevHudView` | `Assets/Scripts/UI/Dev/` ù `[RequireComponent(typeof(UIDocument))]` |

```csharp
// GridDungeon.UI.Dev ù DevBootstrap scene only
class GamePhaseDevHudView : MonoBehaviour
{
    GameState       GameState;       // serialized
    CombatController Combat;        // serialized
    // OnEnable: Q<> cached labels/buttons; PhaseChanged += Refresh
    // Buttons / F1ùF4 ? RequestTransition / RequestCombat / EndBattle(Flee)
}
```

Scene menu: **GridDungeon ? Scenes ? Create Dev Bootstrap** (`DevBootstrap.unity`, not in git ù regenerate after clone).

### View controllers

**Shipped exploration UI** (orchestrator lifecycle, document map, input, map marker overlays, party strip): [exploration UI](02-systems/exploration-ui.md). Runtime events: [UI event contract](04-dev/ui-event-contract.md). Replace plates / picker: [custom party UI](04-dev/custom-party-ui.md), [custom skill picker UI](04-dev/custom-skill-picker-ui.md). Game repo: `ExplorationHudView`, `ExplorationMapCoordinator`, `MinimapPanelView`, `ExpandedMapOverlayView`, `Map*MarkersPresenter`, `PartyMenuOverlayView`, `PartyFormationFloaterPresenter` + `PartyFormationGridView`. Types below are the **target** full read-model sketch (not all shipped).

```csharp
class ExplorationHUD : MonoBehaviour  // root VisualElement for exploration phase
{
    DungeonView       DungeonView;
    MapView           Map;
    PartyStripView    PartyStrip;   // shipped: PartyFormationFloater + PartyFormationGridView
    // CombatLogView Log ù deferred (no exploration log UXML wired; combat uses CombatHudLogView)
}

class CombatHUD : MonoBehaviour       // root VisualElement for combat phase
{
    TurnOrderStripView TurnOrder;
    PartyRowsView      PartyRows;    // shipped: CombatRosterView front/back in CombatHudView
    CommandPanelView   Commands;     // Skill ? CombatSkillPickerHost (ADR 035)
    TargetSelectorView Targets;
    NavigatorView      Navigator;
    SynchroBarView       SynchroBar;
    CombatLogView      Log;
    EnemySlotsView     EnemySlots;
}

// GridDungeon.Editor.Save ù MVP1 save / campaign dev tooling (PR #84)
class GridDungeonSaveEditorWindow : EditorWindow  // GridDungeon ? Tools ? Save Editor
class SaveEditorModel / SaveEditorPanel           // Play: in-memory flags + drift vs disk; Edit: Reload / Write JSON
class CampaignFlagCatalog                       // Editor descriptors ? CampaignFlagId (Core)

// GridDungeon.Editor ù floor level painter ? ExplorationFloor.asset (ADR 002, #107)
class FloorPainterWindow : EditorWindow       // thin shell; UI Toolkit CreateGUI
class FloorPainterPanel : VisualElement         // palette, Apply, ExplorationFloor ObjectField
class FloorPainterGridElement : VisualElement   // per-cell paint + undo
class FloorPainterGridModel                     // session grid (north-up storage, y=0 south)
class FloorPainterMarkerResolver                // scan E/M/^/v ? entry/stairs Vector2Int
class FloorPainterExport                        // BuildTiles + TryApplyToExplorationFloor

class MapView : MonoBehaviour
{
    // 2D schematic from ExplorationFloor + IReadOnlyFloorMapState (ADR 002); not minimap RT
    // Fullscreen overlay; input passes through to ExplorationInputHandler (ADR 014)
    void Show(); void Hide();
    void RenderFloor(IReadOnlyFloorMapState state, GridPosition partyCell, FacingDirection facing);
    void UpdateFoeIcons(IReadOnlyList<FoeInstance> visible);
    void RefreshMap();   // on MapSystem reveal / party / FOE dirty
}

class PartyStripView : MonoBehaviour
{
    void Bind(IReadOnlyList<Combatant> coreSix);
    void Refresh();
}

// Horizontal AGI queue strip; rules in combat.md ù Turn order strip.
class TurnOrderStripView : MonoBehaviour
{
    void Bind(TurnQueue queue);   // TurnQueue.Ordered + Current
    void Advance();               // highlight next slot; OnTurnStart from CombatController
}

class CommandPanelView : MonoBehaviour
{
    void ShowForCombatant(Combatant actor, bool fleeEnabled);
    event Action<CombatAction> OnActionSelected;
}

// Player pick for Attack / single-target skills ù shipped in CombatHudView + CombatRosterView ([#60](https://github.com/miramocha/griddungeon-game/issues/60)).
// Optional dedicated TargetSelectorView not used in MVP1; highlights + LMB on roster slots.

class SynchroBarView : MonoBehaviour
{
    void SetValue(float normalized);  // 0..1
}

class NavigatorView : MonoBehaviour
{
    void Bind(NavigatorDefinition def);
    void SetProtocolReady(bool ready);
}

class CombatLogView : MonoBehaviour
{
    void AppendLine(string text);
    void Clear();
}

class EnemySlotsView : MonoBehaviour
{
    // Arena rig: 6 anchors (EnemySlot_0..5); optional back-row depth offset on 3..5
    Transform[] m_anchors;   // length BattleFormation.MaxEnemySlots (6)
    void SpawnEnemySlot(int slotIndex, EnemyDefinition def);  // slotIndex 0..5
    void MarkDead(int slotIndex);
    void ShowStatusIcons(int slotIndex, IReadOnlyList<StatusInstance> statuses);
}

// CombatScenePresenter (arena rig) ù GetEnemySlotAnchor(slotIndex) for spawn + VFX; MVP1 HUD uses CombatRosterView two-row bind
```

---

## Key interfaces

```csharp
// Allows MapSystem to expose read-only state to UI without leaking internals
interface IReadOnlyFloorMapState
{
    bool IsVisited(GridPosition cell);
    WallMask GetWalls(GridPosition cell);
    bool TryGetFeature(GridPosition cell, out FeatureState feature);
    bool TryGetFoeIcon(GridPosition cell, out string foeId);
}

// IPhaseController ù defined under Game phase above; OnEnter(from) / OnExit(to)
```

### CombatantFactory (Runtime)

```csharp
static class CombatantFactory
{
    static Combatant FromCharacterSave(CharacterSaveData save, ClassDefinition classDef, ContentDatabase db);
    static Combatant FromEnemyData(EnemyData data, FormationRow row, int slotIndex);
}
```

---

## Folder structure (Unity Assets)

```
Assets/
+-- Scripts/
ù   +-- Core/                     GridDungeon.Core.asmdef
ù   ù   +-- Models/               Combatant.cs, BattleState.cs, FoeInstance.cs, FloorMapState.cs, ...
ù   ù   +-- Content/              SkillData.cs, StatusData.cs, EnemyData.cs, NavigatorData.cs, ...
ù   ù   +-- Campaign/             S1CampaignResolver.cs, CombatTutorialHudRules.cs, ù
ù   ù   +-- Simulators/           DamageCalculator.cs, ValidTargetCalculator.cs, CombatTargeting.cs,
ù   ù   ù                         InventoryRules.cs, InventoryBagCatalog.cs, EquipmentStatAggregator.cs,
ù   ù   ù                         FleeCalculator.cs, ActionResolver.cs, RetreatCellCalculator.cs,
ù   ù   ù                         FoeFleeRetreatPlacement.cs, TurnQueueBuilder.cs, ...
ù   ù   +-- SaveData/             SaveGame.cs, FloorMapStateSave.cs, ...
ù   ù   +-- Enums/                GamePhase.cs, CombatantKind.cs, ...
ù   +-- Runtime/                  GridDungeon.Runtime.asmdef
ù   ù   +-- Game/                 GameState.cs, GamePhaseController.cs,
ù   ù   ù                         HubPhaseController.cs, ExplorationPhaseController.cs,
ù   ù   ù                         CombatPhaseController.cs, IPhaseController.cs
ù   ù   +-- Exploration/          DungeonExplorer.cs, DungeonView.cs, FoeSystem.cs,
ù   ù   ù                         EncounterTrigger.cs, GatherInteractor.cs
ù   ù   +-- Map/                  MapSystem.cs
ù   ù   +-- Combat/               CombatController.cs, CombatPresentationGate.cs, CombatScenePresenter.cs, ù
ù   ù   +-- Party/                PartyRuntime.cs, CombatantFactory.cs, NavigatorRuntime.cs, AuraSystem.cs
ù   ù   +-- Protocol/             ProtocolSystem.cs
ù   ù   +-- Hub/                  HubController.cs, InnService.cs, HospitalService.cs, ...
ù   ù   +-- Codex/                CodexSystem.cs
ù   ù   +-- Content/              ContentDatabase.cs
ù   ù   +-- Save/                 SaveSystem.cs
ù   +-- UI/                       GridDungeon.UI.asmdef
ù       +-- Dev/                  GamePhaseDevHudView.cs (dev bootstrap only)
ù       +-- Game/                 GameBootstrap.cs
ù       +-- Input/                InputRouter.cs, ExplorationInputHandler.cs, ...
ù       +-- Views/                ExplorationHudView, ExplorationMapCoordinator, CombatHudView, CombatHudReactivePresenter, ù
ù       ù                         MapPartyMarkerPresenter, MapFoeMarkersPresenter, MapGatherMarkersPresenter, ù
+-- UI/
ù   +-- Settings/                 GamePanelSettings.asset (shared UIDocument panel)
ù   +-- Themes/                   Theme StyleSheets (optional)
ù   +-- Screens/
ù       +-- Dev/                  GamePhaseDevHud.uxml, GamePhaseDevHud.uss
+-- Content/
ù   +-- Classes/                  *.asset (ClassDefinition SOs)
ù   +-- Skills/                   *.asset (SkillDefinition SOs)
ù   +-- Status/                   *.asset (StatusDefinition SOs)
ù   +-- Equipment/                *.asset (EquipmentDefinition SOs)
ù   +-- Items/                    *.asset (ItemDefinition SOs)
ù   +-- Enemies/                  *.asset (EnemyDefinition SOs)
ù   +-- Encounters/               *.asset (EncounterGroup SOs)
ù   +-- Navigators/               *.asset (NavigatorDefinition SOs)
ù   +-- ProtocolSkills/           *.asset (ProtocolSkillDefinition SOs)
ù   +-- Summons/                  *.asset (SummonDefinition SOs)
ù   +-- Dungeons/
ù       +-- Stratum01/            B1F.asset, B2F.asset, B3F.asset
+-- Tests/                        GridDungeon.Tests.asmdef (see game repo Assets/Tests/README.md)
ù   +-- TestCategories.cs
ù   +-- Combat/
ù   +-- Exploration/
ù   +-- Foe/
ù   +-- Map/
ù   +-- GameFlow/
+-- Plugins/
    +-- Demigiant/DOTween/        (Asset Store import ù required, see tech notes)
```

---

## MVP1 content IDs (locked)

These string IDs must be stable across code and SO assets.

**Full skill kit (targeting, effects, stubs):** [MVP1 class skills](03-content/class-skills.md).

| Type | ID | Notes |
|------|----|-------|
| Class | `vanguard`, `breaker`, `medic`, `summoner`, `marksman`, `tactician` | Day-one roster |
| Navigator | `guild_handler` | Sortie Lead; day one; aura: `synchroGainBonus = 0.05` ù [navigator](02-systems/navigator.md) |
| Protocol skill | `protocol_strike`, `protocol_mend` | Damage all enemies / heal all living core ù [synchro-protocol](02-systems/synchro-protocol.md) |
| Summon | `scout_drone` | Summoner-only; 3 rounds; **player-controlled** kit |
| Summon deploy skill | `deploy_scout_drone` | Summoner tree only; `SkillType.Deploy` ? `scout_drone`, aux back ([ADR 016](../decisions/016-summon-control-mvp1.md)) |
| Summon skill | `volt_burst` | On `scout_drone` summon kit only ù not on Summoner class tree |
| Stratum | `s1` | Stratum 1 |
| Floors | `s1_B1F`, `s1_B2F`, `s1_B3F` | Save/map keys |
| Items | `patch_kit`, `stim_draft`, `trauma_kit`, `return_thread`, `analysis_glass` | Starter consumables |
| Equipment | `guild_shortsword`, `leather_coif`, `leather_jacket`, `leather_boots`, `scout_charm` | MVP1 shop slice ù [progression ù MVP1 equipment](02-systems/character-progression.md#mvp1-equipment-locked) |
| Status | `poison`, `sleep`, `panic`, `bind_head`, `bind_arm` | MVP1 subset |
| Stat mods | `offense_up`, `offense_down`, `defense_up`, `defense_down`, `magic_up`, `magic_down`, `speed_up`, `speed_down`, `blind`, `regen` | |
| Enemy | `stray_hound`, `rust_mite`, `gutter_crow`, `scrapling`, `shackle_rat`, `venom_slime`, `alley_thug`, `rubble_guard`, `s1_warden` | [mvp1-enemy-roster](03-content/enemy-roster.md) |
| Enemy skill | `enemy_attack`, `atk_peck_volt`, `atk_bind_arm`, `atk_poison_spit`, `atk_heavy_swing`, `atk_guard_slam`, `atk_warden_bind`, `atk_warden_venom` | Enemy pool only |
| Encounter group | `grp_alley_stalker`, `grp_alley_stalker_tutorial`, `grp_s1_warden`, `grp_b1_chaff_hound`, `grp_b1_chaff_mite`, `grp_b2_chaff`, `grp_b2_shackle_rat`, `grp_b2_venom_slime`, `grp_b3_mix_hounds`, `grp_b3_rubble_pair`, `grp_b3_control` | Slot layouts in roster doc |
| FOE entity | `foe_alley_stalker`, `foe_s1_warden` | Map keys; not `EnemyDefinition` ids |

### Class skills (3 per class ù locked)

| Class | `skill_id` | `skill_id` | `skill_id` |
|-------|------------|------------|------------|
| Vanguard | `vanguard_guard` | `vanguard_shield_bash` | `vanguard_protect` |
| Breaker | `breaker_power_slash` | `breaker_cleave` | `breaker_pierce_drive` |
| Medic | `medic_heal` | `medic_purify` | `medic_revive` |
| Summoner | `summoner_volt_bolt` | `deploy_scout_drone` | `summoner_focus` |
| Marksman | `marksman_aimed_shot` | `marksman_bind_shot` | `marksman_volley` |
| Tactician | `tactician_rally` | `tactician_weaken` | `tactician_field_mend` |

All class skills: **`presentation: Fixed`** ([combat presentation](02-systems/combat-presentation.md)).

**MVP3 side dungeon IDs (draft, not MVP1):** `sd01`, floors `sd01_F1`, `sd01_F2` ù [side dungeons](02-systems/side-dungeons.md).

---

## MVP3 ù side dungeons (sketch)

**Authority:** [side dungeons](02-systems/side-dungeons.md), [ADR 022](../decisions/022-side-dungeons-mvp3.md). Does **not** change MVP1 locked content IDs above.

```csharp
enum ExplorationMapKind { Stratum, SideDungeon }

// Extend ExplorationStateSave (MVP3)
struct ExplorationStateSave
{
    ExplorationMapKind MapKind;
    string LocationId;   // stratumId ("s1") OR side locationId ("sd01")
    string FloorId;      // "B1F" or "F1"
    GridPosition PartyCell;
    FacingDirection Facing;
}

// SaveGame ù MVP3 additions (draft)
[Serializable] class SaveGame
{
    // ... existing MVP1 fields ...
    string[] UnlockedSideDungeonIds;  // e.g. "sd01"
}

// Maps / FoeState dictionary keys:
//   Stratum:  "s1_B1F"
//   Side:     "sd01_F1"
```

| API | Caller | Phase |
|-----|--------|-------|
| `LeaveHub(stratumId, floorId)` | Hub **Enter Stratum** | ? Exploration (stratum rules) |
| `EnterSideDungeon(locationId, floorId)` | Hub **Side expedition** | ? Exploration (side rules; exit ? hub only) |

`ContentDatabase.GetFloor` may resolve by composite key or `(MapKind, locationId, floorId)` ù implementation detail for MVP3.

---

## Related docs

- [MVP1 enemy roster](03-content/enemy-roster.md) ù locked S1 enemies, groups, skill stubs
- [04 ù Tech notes](04-tech-notes.md) ù engine stack, high-level module map, save format
- [MVP1 spec](archive/mvp1-spec.md) ù systems checklist
- [ADR 014 ù MVP1 exploration & map](../decisions/014-mvp1-exploration-map.md)
- [ADR 015 ù MVP1 combat](../decisions/015-mvp1-combat.md)
- [ADR 016 ù Summon control MVP1](../decisions/016-summon-control-mvp1.md)
- [ADR 017 ù Game phase controller](../decisions/017-game-phase-controller.md)
- [Game phase](02-systems/game-phase.md)
- [Combat](02-systems/combat.md)
- [Combat status & buffs](02-systems/combat-status-and-buffs.md)
- [Party & classes](02-systems/party-and-classes.md)
- [MVP1 class skills](03-content/class-skills.md)
- [Character progression](02-systems/character-progression.md)
- [FOE encounters](02-systems/foe-encounters.md)
- [Side dungeons (MVP3)](02-systems/side-dungeons.md)
- [ADR 022 ù Side dungeons MVP3](../decisions/022-side-dungeons-mvp3.md)
- [Navigator](02-systems/navigator.md)
- [Synchro Protocol](02-systems/synchro-protocol.md)
