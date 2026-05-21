# Game Phase (Hub / Exploration / Combat)

Macro runtime modes for MVP1. **Locked:** pure C# orchestration ([ADR 017](../../decisions/017-game-phase-controller.md)). Unity Visual Scripting state graphs are **not** used for phase authority in MVP1.

## Design goals (MVP1)

These goals drive the split between **macro phases** (this doc), **assemblies** ([class design MVP1](../05-class-design-mvp1.md)), and **combat rounds** ([combat](combat.md)).

| Goal | How the architecture supports it |
|------|-----------------------------------|
| **Test damage + AGI without Unity** | Rules live in `GridDungeon.Core` (`DamageCalculator`, `TurnQueueBuilder`, …); `GridDungeon.Tests` references Core only |
| **Hub ↔ explore ↔ combat loop** | `GamePhase` enum + `GamePhaseController.TryTransitionTo` + three `IPhaseController` Enter/Exit hooks |
| **Spec-locked combat flow** | Union → AGI queue → end-of-round stays on `CombatController`; not duplicated in phase controllers |
| **Content in data, not code** | ScriptableObjects in Runtime; Core uses DTOs at boundaries (no `SkillDefinition` in simulators) |
| **FOE + map + flee rules** | `ExplorationPhaseController` wires `DungeonExplorer` events → `MapSystem`, `FoeSystem`; combat entry via `GameState.RequestTransition` |
| **Clear input per mode** | `InputRouter` reacts to `PhaseChanged`; one authoritative phase enum for UI and action maps |
| **Inspectable, reviewable flow** | Phase transitions in C# (grep, diff, PR review); optional UVS later for presentation only |
| **Single responsibility** | `GameState` = composition root; `GamePhaseController` = transitions; phase controllers = lifecycle; subsystems = domain rules |

## Layer stack

Macro phases sit in **Runtime**; they orchestrate subsystems but do not implement combat math or grid rules.

```mermaid
flowchart TB
  subgraph ui [GridDungeon.UI]
    IR[InputRouter]
    HUD[ExplorationHUD / CombatHUD]
  end
  subgraph runtime [GridDungeon.Runtime]
    GS[GameState]
    GPC[GamePhaseController]
    subgraph phases [IPhaseController]
      H[HubPhaseController]
      E[ExplorationPhaseController]
      C[CombatPhaseController]
    end
    subgraph systems [Shared subsystems]
      DE[DungeonExplorer]
      CC[CombatController]
      PR[PartyRuntime]
      SS[SaveSystem]
    end
    GS --> GPC
    GPC --> H & E & C
    H --> HubController
    E --> DE & MapSystem & FoeSystem
    C --> CC & CombatScenePresenter
  end
  subgraph core [GridDungeon.Core]
    SIM[Simulators + models]
    GP[GamePhase enum]
  end
  subgraph tests [GridDungeon.Tests]
    T[NUnit against Core]
  end
  HUD --> GS
  IR --> GPC
  GPC --> GP
  CC & DE --> SIM
  T --> SIM
  ui --> runtime
  runtime --> core
```

**Authority rule:** only `GamePhaseController` changes `GamePhase`. UI and gameplay code call `GameState.RequestTransition`; they do not toggle scenes or input maps directly.

## Terminology

| Term | Scope | Owner |
|------|--------|--------|
| **Game phase** | Hub, Exploration, Combat | `GamePhaseController` |
| **Combat round** | One full AGI cycle + end-of-round ticks | `CombatController` |
| **Combat sub-phase** | Union → turn → end-of-round within one battle | `CombatController` (`CombatPhase` enum) |

Do not conflate **game phase** with **combat sub-phase**.

## Architecture (composition)

```mermaid
flowchart LR
  subgraph root [GameState MonoBehaviour]
    GPC[GamePhaseController]
    HP[HubPhaseController]
    EP[ExplorationPhaseController]
    CP[CombatPhaseController]
    GPC --- HP & EP & CP
  end
  IR[InputRouter] -.->|PhaseChanged| GPC
  Caller[FoeSystem / Hub / Combat] -->|RequestTransition| root
```

ASCII equivalent:

```
GameState (MonoBehaviour, composition root)
├── GamePhaseController          ← authoritative GamePhase + transitions
├── HubPhaseController           ← IPhaseController
├── ExplorationPhaseController ← IPhaseController
├── CombatPhaseController        ← IPhaseController
├── PartyRuntime, SaveSystem, ContentDatabase, …
└── (shared subsystems referenced by phase controllers)

InputRouter                      ← enables action maps from PhaseChanged
```

### Responsibilities

| Type | Role |
|------|------|
| **`GamePhase`** (`Core` enum) | `Hub`, `Exploration`, `Combat` |
| **`GamePhaseController`** | `TryTransitionTo`, `PhaseChanged`, transition validation |
| **`GameState`** | Scene lifetime, serialized refs, public API for UI/systems to request transitions |
| **`HubPhaseController`** | Enter hub UI/services; exit clears exploration-only listeners |
| **`ExplorationPhaseController`** | Wire `DungeonExplorer` events → `MapSystem`, `FoeSystem`, `EncounterTrigger`; show FPV |
| **`CombatPhaseController`** | Start/end battle presentation; disable exploration input; call `CombatController` |
| **`CombatController`** | Union bar round flow, AGI queue, flee, victory — **unchanged by this doc** |

## Phase diagram

```mermaid
stateDiagram-v2
  [*] --> Hub
  Hub --> Exploration: LeaveHub
  Exploration --> Combat: Encounter
  Combat --> Exploration: Win / Flee
  Exploration --> Hub: ReturnToHub
  Combat --> Hub: WipeLoadSave
```

## Transition flow (sequence)

```mermaid
sequenceDiagram
  participant Caller as System / UI
  participant GS as GameState
  participant GPC as GamePhaseController
  participant Old as Current IPhaseController
  participant New as Next IPhaseController
  participant IR as InputRouter

  Caller->>GS: RequestTransition(Combat)
  GS->>GPC: TryTransitionTo(Combat)
  GPC->>GPC: Validate(from, to)
  GPC->>Old: OnExit()
  GPC->>GPC: Current = Combat
  GPC->>New: OnEnter()
  GPC->>IR: PhaseChanged
  GPC-->>Caller: true
```

## Who requests transitions

| Trigger | Requested phase | Caller |
|---------|-----------------|--------|
| Player leaves inn / enters stratum | Exploration | `HubController.LeaveHub` |
| FOE same cell as party | Combat | `FoeSystem` → `GameState` |
| Random encounter on step | Combat | `EncounterTrigger` → `GameState` |
| Battle won or flee success | Exploration | `CombatController` |
| Return to surface / hub menu | Hub | Hub UI / stairs up |
| Party wipe | Hub | Wipe flow → load save → Hub |

Combat **never** transitions directly to Hub on flee — only Exploration (FOE remains on map).

## Exploration step flow

While `Current == Exploration`, `ExplorationPhaseController` owns event subscriptions. A single step can end in map reveal, FOE patrol, contact combat, or a random encounter.

```mermaid
sequenceDiagram
  participant Input as ExplorationInputHandler
  participant DE as DungeonExplorer
  participant Map as MapSystem
  participant Foe as FoeSystem
  participant Enc as EncounterTrigger
  participant GS as GameState

  Input->>DE: TryStep()
  DE->>DE: Lerp cell / bump or move
  alt entered new cell
    DE->>Map: OnPartyEnteredCell
  else blocked
    DE->>Map: OnBumpWall
  end
  DE->>Foe: OnPartyStep
  Foe->>Foe: Advance patrol
  alt FOE same cell
    Foe->>GS: RequestTransition(Combat)
  else random encounter roll
    Enc->>GS: RequestTransition(Combat)
  end
```

## Combat round flow (within Combat phase)

When `Current == Combat`, **game phase does not change** until the battle ends. Round logic is entirely inside `CombatController`.

```mermaid
sequenceDiagram
  participant GS as GameState
  participant CP as CombatPhaseController
  participant CC as CombatController
  participant Union as UnionSystem
  participant TQ as TurnQueueBuilder
  participant EOR as EndOfRoundPipeline

  CP->>CC: StartBattle(context)
  loop each combat round
    alt Union bar == 100%
      CC->>Union: TryBeginUnionPhase
    end
    CC->>TQ: Build AGI queue
    loop each AGI turn
      alt player core
        CC->>CC: Wait SubmitPlayerAction
      else MVP1 summon
        CC->>CC: ResolveSummonTurn
      else enemy
        CC->>CC: Run AI
      end
      CC->>Union: OnCoreActed
    end
    CC->>EOR: Execute end-of-round
    CC->>CC: Victory / wipe / continue
  end
  CC->>CP: OnBattleEnded
  CP->>GS: RequestTransition(Exploration)
```

See [combat](combat.md) for command tables and damage pipeline.

## Phase Enter / Exit checklist

### Hub `OnEnter`

- Show hub UI (menu tree MVP1)
- `InputRouter` → UI / hub map only
- `SaveSystem` ready for inn save
- `FoeSystem.ResetFloor` for floors when returning from a dive (ADR 008)
- `SaveSystem.ClearExplorationState`

### Hub `OnExit`

- Hide hub UI

### Exploration `OnEnter`

- Load floor from `ContentDatabase` + save snapshot
- `DungeonView.SetVisible(true)`
- `MapSystem.LoadFloor`
- `FoeSystem.LoadFloor`
- Subscribe: `DungeonExplorer.OnPartyStep`, `OnPartyEnteredCell`, `OnBumpWall`
- Subscribe: `FoeSystem.OnFoeContact` → request Combat
- `InputRouter` → Exploration + Map maps

### Exploration `OnExit`

- Unsubscribe all exploration listeners (avoid leaks)
- Optional: pause `DungeonExplorer` input

### Combat `OnEnter`

- `DungeonView.SetVisible(false)` (or dimmed)
- `CombatPhaseController` builds `CombatEntryContext`, calls `CombatController.StartBattle`
- `CombatScenePresenter` spawn backdrop + enemy slots
- `AuraSystem.ApplyPassives` for active Navigator
- `InputRouter` → Combat map

### Combat `OnExit`

- `CombatController` cleanup, dismiss aux summons
- `CombatScenePresenter` teardown
- `AuraSystem.RemovePassives`

## API sketch (Runtime)

```csharp
// Core/Enums/GamePhase.cs
enum GamePhase { Hub, Exploration, Combat }

// Runtime/Game/GamePhaseController.cs — plain C#, not MonoBehaviour
sealed class GamePhaseController
{
    public GamePhase Current { get; private set; }
    public event Action<GamePhase, GamePhase> PhaseChanged;

    public bool TryTransitionTo(GamePhase next, IReadOnlyDictionary<GamePhase, IPhaseController> controllers);
}

// Runtime/Game/IPhaseController.cs
interface IPhaseController
{
    void OnEnter(GamePhase from);
    void OnExit(GamePhase to);
}

// Runtime/Game/GameState.cs
sealed class GameState : MonoBehaviour
{
    public GamePhase Current => _phaseController.Current;
    public bool RequestTransition(GamePhase phase) => …;
}
```

`TryTransitionTo` calls `OnExit` on the old controller, updates `Current`, calls `OnEnter` on the new controller, then raises `PhaseChanged`.

## Input maps per phase

| Game phase | Input System maps (enabled) |
|------------|---------------------------|
| Hub | `UI` (+ hub-specific if split later) |
| Exploration | `Exploration`, `Map` (map overlay pass-through per ADR 014) |
| Combat | `Combat`, `UI` |

Implemented in `InputRouter` (UI assembly or Runtime — see [class design MVP1](../05-class-design-mvp1.md)).

## Visual Scripting (post-MVP1 optional)

If a UVS state graph is added later:

- Graph **listens** to `PhaseChanged` only
- Graph runs presentation (fade, audio sting)
- Graph **must not** call `TryTransitionTo` except via debug menu
- C# remains authoritative

## Related docs

- [ADR 017 — Game phase controller](../../decisions/017-game-phase-controller.md)
- [05 — Class design MVP1](../05-class-design-mvp1.md)
- [04 — Tech notes](../04-tech-notes.md)
- [MVP1 spec](../mvp1-spec.md)
- [Combat](combat.md)
- [Hub & services](hub-and-services.md)
- [Input bindings](input-bindings.md)
