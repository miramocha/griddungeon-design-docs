# Tech Notes (Unity 6 / URP)

**Engine:** **Unity 6** (6000.x) + **URP** ([ADR 012](../decisions/012-unity-6-stack.md)).  
**Platform:** PC Standalone ([ADR 008](../decisions/008-campaign-defaults.md), [input bindings](02-systems/input-bindings.md)).

**Cursor / clean code:** Unity rules in `griddungeon-game/.cursor/rules/` are **hard-linked** into this repo at [`.cursor/rules/`](../.cursor/rules/) (see README there). Architecture work also applies [`architecture-design-principles.mdc`](../.cursor/rules/architecture-design-principles.mdc).

## Engine stack (locked)

| Layer | Choice |
|-------|--------|
| Editor / runtime | Unity 6 — pin minor in `ProjectVersion.txt` when repo exists |
| Rendering | URP (no Built-in RP) |
| Shaders | **Shader Graph** for most materials/VFX; **HLSL** only when Graph can’t express it or perf demands a custom pass ([ADR 012](../decisions/012-unity-6-stack.md)) |
| Input | Input System — `Exploration`, `Combat`, `Map`, `UI` action maps; rebindable player prefs when settings ship |
| Runtime animation | **DOTween** (Demigiant) — exploration step lerp, UI, camera punch, Fixed-skill VFX timing |
| Combat cinematics | **Timeline** / Animation clips per skill asset (`Cinematic`, `CinematicQTE`) |
| Save | `JsonUtility` or custom serializer MVP1; ScriptableObjects for content DB |

Third-party plugins and asset store packs must declare **Unity 6 + URP** compatibility before use. **DOTween** is a required dependency (Asset Store import under `Assets/Plugins/Demigiant/DOTween/`).

## Shaders (Shader Graph–first)

| Use Shader Graph | Use HLSL (exception) |
|------------------|----------------------|
| FPV dungeon walls/floor/doors | Custom fullscreen blit with no graph equivalent |
| Battle arena backdrop & slot lighting | Compute-style pass (if used) |
| Character/enemy sprites — lit/unlit | Extremely hot path after profiling |
| Hit flash, poison tint, Union burst VFX | Porting legacy `.shader` until rebuilt in Graph |
| UI-adjacent fullscreen tints | |

**Conventions**

- URP **Shader Graph** assets under `Assets/Shaders/Graph/` (or project convention).
- Handwritten shaders under `Assets/Shaders/HLSL/` — **one-line rationale** at top of file.
- Prefer **subgraphs** for reusable noise, dissolve, hit-flash rather than copy-paste HLSL.
- No Built-in RP shaders; no Shader Forge legacy imports.

EO alignment drives **auto-reveal map**, **FOE entities**, and **AGI combat queue** as first-class systems. **No map drawing tools.**

## Animation (DOTween + Timeline)

| Use DOTween | Use Timeline |
|-------------|--------------|
| Grid step lerp, bump nudge, FOE slide-in | Boss / Union `Cinematic` beats |
| UI fades, map pan, combat log pop | `CinematicQTE` authored camera + timing |
| Fixed-skill target zoom punch, hit flash, light screen shake | Anything needing keyed tracks / multiple actors |

**Conventions**

- Import **DOTween** from the Asset Store into `Assets/Plugins/Demigiant/DOTween/`; enable modules needed at setup (UI, 2D, etc.).
- Game runtime assemblies reference `DOTween` / `DOTween.Modules` as needed; no tween logic in `CombatSimulator` (pure C# tests).
- Prefer `Sequence` / `Tween` over hand-rolled lerps; kill or complete tweens on scene unload, combat end, and explorer disable (`DOTween.Kill` on owning transforms).
- Exploration input: poll movement/turn `IsPressed` when explorer lerp completes for hold-to-repeat; displacement priority over turn; no buffered input during lerp ([ADR 001](../decisions/001-grid-movement.md)).
- Exploration lerp durations: four presets (Slow / Normal / Fast / Very Fast); default Normal 0.28s step ([ADR 018](../decisions/018-exploration-animation-speed.md)).
- **Timeline** stays the source of truth for sparse cinematic skills; do not duplicate the same beat in both Timeline and DOTween unless one drives the other.

### UI reactivity

**Hub, exploration, and combat** HUDs share the same MVP1 bar: when game state changes, the UI **animates or pulses** so cause → effect is obvious. Static swaps alone are not enough.

| Principle | Rule |
|-----------|------|
| **Event-driven** | Presenters (`*View` in `GridDungeon.UI`) subscribe to controller events (`CombatController`, `HubController` services, `MapSystem`, `DungeonExplorer`, `GamePhaseController`) and play feedback; views do not poll every frame for diffs. |
| **DOTween on Toolkit** | Short tweens on `VisualElement` style/transform (fade, scale punch, slide, fill lerp). Enable DOTween **UI** module. No tween logic in `GridDungeon.Core`. |
| **State first, motion second** | Apply authoritative values immediately (HP, map cells, queue order); animate **from** the previous visual state. |
| **Blocking (EO-style)** | Hold a **presentation lock** until mandatory UI tweens for the current beat finish. The **next** player action (combat command, hub confirm, etc.) is ignored until unlock. **Summon/auto turns** use the same lock — play the full highlight → VFX → log chain before the queue advances ([summons](02-systems/summons-and-guests.md)). Exploration grid step already blocks movement during lerp ([ADR 001](../decisions/001-grid-movement.md)); map/HUD feedback for that step may run in parallel or complete before the next step is accepted — pick one per beat in the phase doc tables. |
| **Duration** | Typical UI feedback **0.1–0.4s**; Union bar fill and HP drops may use **0.2–0.6s**. Longer motion belongs in [combat presentation](02-systems/combat-presentation.md) (camera/VFX), not HUD chrome. |
| **Cleanup** | `Kill` / complete tweens on `OnDisable`, phase exit, and combat end (see [Animation](#animation-dotween--timeline) above). |

**MVP1 checklists by phase:**

| Phase | Doc |
|-------|-----|
| Combat | [combat — UI motion & feedback](02-systems/combat.md#ui-motion--feedback) |
| Exploration | [mapping — Map UI motion](02-systems/mapping.md#map-ui-motion) |
| Hub | [hub — Service UI motion](02-systems/hub-and-services.md#service-ui-motion) |

**Deferred (post-MVP1):** global **reduce UI motion** accessibility toggle; keep tween durations in data/prefs so scale-to-zero is trivial later.

## High-level modules

```
GameState (composition root)
├── GamePhaseController  — Hub | Exploration | Combat ([ADR 017](../decisions/017-game-phase-controller.md), [game phase](02-systems/game-phase.md))
│   ├── HubPhaseController
│   ├── ExplorationPhaseController
│   └── CombatPhaseController
├── HubServices          — explorers guild, navigator office, shop, hospital, inn save
├── DungeonExplorer      — grid step, facing, interact
├── DungeonView          — FPV cell rendering (hidden during combat)
├── CombatScenePresenter — battle backdrop + enemy slot rig ([combat scene](02-systems/combat-scene.md))
├── MapSystem            — auto-reveal layer, fog, read-only UI
├── FoeSystem            — spawn, visibility, step patrol, contact
├── PartyRuntime         — 6 core + 0–2 aux combatants, skills
├── NavigatorRuntime     — active navigator, aura application, roster
├── UnionSystem          — team bar charge/spend; Navigator invokes in Union phase
├── CombatController     — UnionPhase → AGI queue → EndRound
├── CodexSystem          — enemy knowledge / weaknesses
├── ContentDatabase      — strata, floors, FOE, encounters
└── SaveSystem           — hub save + per-floor revealed map + FOE state
```

**Dev bootstrap:** `DevBootstrap.unity` + UI Toolkit `GamePhaseDevHud` drives Hub → Exploration → Combat → Hub for macro-phase smoke tests ([game phase](02-systems/game-phase.md#dev-bootstrap-hud-ui-toolkit)). Game repo: **GridDungeon → Scenes → Create Dev Bootstrap**.

## Map system

- **Revealed layer** (saved per floor):
  - `visited` floor tiles
  - `wallMask` per cell edge (set on bump + perimeter reveal)
  - `features`: door state, stairs, chest opened, trap triggered
  - `foeIcons`: last known FOE cell when in LOS
- **Truth layer** — designer collision (editor only); never sent to client as full download
- **UI:** read-only grid; pan/zoom; no edit raycasts
- `MapReveal.OnPartyEnteredCell`, `OnBumpWall(side)`, `OnInteract(type)`

### Map proxy + minimap camera ([ADR 002](../decisions/002-mapping-model.md#technical-notes-unity--map-proxy--minimap-camera))

| Concern | Approach |
|---------|----------|
| **Authoring** | Per-floor **map proxy rig**: flat-color **cubes** on layer **`MapProxy`**, grid-aligned with FPV layout so designers preview overlap in the Editor |
| **FPV vs map** | Exploration / dungeon meshes on non-`MapProxy` layers; **minimap ortho culling mask = `MapProxy` only** |
| **Main camera** | FPV camera **excludes** `MapProxy` (or proxies hidden from player view) — player never sees schematic cubes in corridor view |
| **Output** | Minimap camera → `RenderTexture` → UI Toolkit map panel; refresh on `MapSystem` reveal dirty, not per frame |
| **Fog** | Hide/disable proxies or shader clip from `FloorMapState.Visited` / `WallMask` |
| **Party / FOE** | `MapProxy` quads on `PartyPose` / `FOEPose`; live RT while minimap cam on |
| **Verticality** | Cell `(x,y,level)`; jump pads / stairs in content; no walk-under ([ADR 019](../decisions/019-floor-verticality.md)) |
| **Runtime type** | `MapView` binds `IReadOnlyFloorMapState`, triggers proxy/RT refresh; `MapSystem` applies `MapRevealCalculator` |

**Folder convention (game repo):** e.g. `Assets/.../Floors/{floorId}/MapProxy.prefab` or proxy children under floor root; document in floor authoring checklist when content pipeline exists.

## Gathering & fishing (MVP2)

- `MinigameController` — `Gather` | `Fish`; pauses exploration + FOE step tick
- `GatherNodeInstance` / `FishNodeInstance` on floor; depleted flags in dive save; reset on hub respawn ([gathering & fishing](02-systems/gathering-and-fishing.md))

## FOE system

- `FoeInstance` — id, grid pos, patrol path index, tier, encounter group
- `OnPartyStep()` → increment floor step count; FOEs with `stepsPerMove` advance patrol index
- Line-of-sight check for map icon reveal
- Collision → `CombatController.StartBattle(foeId)`
- `CanFoeFlee()` → backward retreat cell walkable ([ADR 011](../decisions/011-foe-flee-retreat.md))
- `OnFoeFleeSuccess()` → set party exploration pos to retreat cell
- **Optional later:** `TickCombatRound()` + `TryJoinOneFoe()` ([ADR 005](../decisions/005-foe-combat-patrol.md), [ADR 010](../decisions/010-chain-foe-battle.md)); flag-gated

MVP1: step patrol system in core; early floors mostly `stepsPerMove: 0` or 1-cell paths. No combat-round FOE movement.

## Combat

- `TurnQueueBuilder.Build(combatants)` sorted by AGI (+ Speed Up/Down from [status system](02-systems/combat-status-and-buffs.md))
- `StatusSystem` (Core) — apply/refresh/tick/cleanse using `StatusData` DTOs; SO `StatusDefinition` in Runtime via `ContentDatabase.ToStatusData`
- `EndOfRoundPipeline` — regen → DoT → decrement durations → FOE patrol (optional)
- UI binds to queue head; advance on action complete
- `CombatSimulator` pure C# for tests (status inflict + tick unit tests)

## Navigator

- `NavigatorDefinition` — aura modifiers, union skill ids, `unlockCondition`
- `PartyRuntime.ActiveNavigatorId`; `UnlockedNavigatorIds` (flags from strata/quests/events)
- `AuraSystem.ApplyPassives(coreSix)` on combat start / navigator swap
- Not in `Combatant` AGI list; **excluded from targeting** (including boss AOEs); separate UI strip, no HP

## Union (team bar)

- `UnionBar` float 0–1 on `PartyRuntime`
- `UnionSystem.OnCombatEvent` — core six only
- `CombatController.BeginRound` → `UnionPhase` if bar == 1 && Navigator skill chosen
- `UnionSkillDefinition` — participant count, effect, presentation id
- Save: `unionBar` + `activeNavigatorId` per dive
- FOE state: persist on floor during dive; **reset FOE spawns** on hub return + re-enter

## Combat scene

- `CombatEntryContext` → `BattleBackground` + `EncounterGroup` → spawn on `EnemySlot_0..4` ([ADR 013](../decisions/013-combat-scene-rendering.md))
- Exploration `DungeonView` paused/hidden; grid anchor unchanged until fight ends
- Enemy **grid sprite** (exploration) vs **battle prefab/sprite** (arena) — separate assets per id

## Combat presentation

- `BattleCameraRig` — fixed angle on arena rig ([combat presentation](02-systems/combat-presentation.md))
- `SkillDefinition.presentation`: `Fixed` | `Cinematic` | `CinematicQTE`
- `Fixed` — VFX at slots; optional subtle zoom to primary target, then reset
- `Cinematic` — Timeline; skippable; enemy boss telegraphs (no player QTE)
- `CinematicQTE` — Timeline + `QTEController` (press / chain / hold); tier → damage bonus; skill always resolves base on miss
- MVP1: all skills `Fixed`; cinematic + QTE stubbed
- MVP2: 1× `CinematicQTE` party skill + 1× boss `Cinematic` sample

## Grid / content

- `StratumFloor` ScriptableObject: grid, spawns, FOE list, encounter rate
- Labels: `B1F` within `Stratum01`

## Save format (EO-oriented)

```json
{
  "hub": { "gold": 0, "unlockedFloors": { "s1": "B3F" } },
  "party": [ /* 6 characters + skill allocations */ ],
  "maps": {
    "s1_B2F": { "visited": [], "walls": [], "features": [], "foeIcons": [] }
  },
  "foeState": {
    "s1_B2F": [{ "id": "stalker", "cell": [12,9], "alive": true }]
  },
  "exploration": null
}
```

When in labyrinth, `exploration` holds position, facing, floor id.

## UI layout (PC prototype)

```
┌─────────────────────┬──────────────┐
│   FPV dungeon view  │  Map (view)  │
│                     │  read-only   │
├─────────────────────┴──────────────┤
│  Log / party strip (HP, status)    │
└────────────────────────────────────┘
```

Combat replaces layout with turn order + **4+4 rows** (core + aux).

## Combatant types

```csharp
enum CombatantKind { Core, Summon, Guest, Enemy }
```

- `PartyRuntime` — 6 core, always
- `CombatController` — spawns aux from skills/scripts; clears on battle end
- `ResolveSummonTurn()` — run `SummonDefinition.actionScript`; no input ([ADR 016](../decisions/016-summon-control-mvp1.md))

## Performance

- 60 FPS exploration with map visible
- FOE patrol: ≤10 active FOEs per floor
- Floor size: 40×40 soft max (EO floors vary)

## Open technical decisions

- [x] Map fullscreen: movement **pass-through** ([ADR 014](../decisions/014-mvp1-exploration-map.md))
- [x] Wall reveal: **bump + cell perimeter** ([ADR 014](../decisions/014-mvp1-exploration-map.md))
- [ ] Default `stepsPerMove` per stratum (tune 2–5 in data)
- [ ] Custom Unity editor for FOE patrol paths + `stepsPerMove` (post-MVP1 tooling)

## Related docs

- [05 — Class design MVP1](05-class-design-mvp1.md) — full class hierarchy, assembly layout, folder structure
- [Game phase](02-systems/game-phase.md) — design goals, diagrams, `GamePhaseController` + phase controllers ([ADR 017](../decisions/017-game-phase-controller.md))
- [Mapping](02-systems/mapping.md)
- [ADR 002](../decisions/002-mapping-model.md)
- [ADR 003](../decisions/003-foe-step-patrol.md)
- [ADR 012 — Unity 6 stack](../decisions/012-unity-6-stack.md)
