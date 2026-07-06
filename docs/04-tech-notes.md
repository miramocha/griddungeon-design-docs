---
tags:
  - path/docs
  - type/dev
  - scope/required
  - status/draft
  - domain/exploration
  - domain/map
---
# Tech Notes (Unity 6 / URP)

**Engine:** **Unity 6** (6000.x) + **URP** ([ADR 012](../decisions/012-unity-6-stack.md)).  
**Platform:** PC Standalone ([ADR 008](../decisions/008-campaign-defaults.md), [input bindings](02-systems/input-bindings.md)).

**Cursor / clean code:** Unity rules in `griddungeon-game/.cursor/rules/` are **hard-linked** into this repo at [`.cursor/rules/`](../.cursor/rules/) (see README there). Architecture work also applies [`architecture-design-principles.mdc`](../.cursor/rules/architecture-design-principles.mdc).

## Engine stack (locked)

| Layer | Choice |
|-------|--------|
| Editor / runtime | Unity 6 — pin minor in `ProjectVersion.txt` when repo exists |
| Rendering | URP (no Built-in RP) |
| Shaders | **Shader Graph** for most materials/VFX; **HLSL** only when Graph can't express it or perf demands a custom pass ([ADR 012](../decisions/012-unity-6-stack.md)) |
| Input | Input System — `Exploration`, `Combat`, `Map`, `UI` action maps; rebindable player prefs when settings ship |
| Runtime animation | **DOTween** (Demigiant) — exploration step lerp, UI, camera punch, Fixed-skill VFX timing |
| Combat cinematics | **Timeline** / Animation clips per skill asset (`Cinematic`, `CinematicQTE`) |
| Save | `JsonUtility` or custom serializer at launch; ScriptableObjects for content DB |

Third-party plugins and asset store packs must declare **Unity 6 + URP** compatibility before use. **DOTween** is a required dependency (Asset Store import under `Assets/Plugins/Demigiant/DOTween/`). **Plugin asmdefs:** optional `GridDungeon.FloorArt.TileWorldCreator` (+ Editor sibling) references vendor TWC; `GridDungeon.Runtime` uses `IFloorArtMeshBackend` registry only — see [floor-art-fpv.md — TileWorldCreator runtime path](02-systems/floor-art-fpv.md#tileworldcreator-runtime-path) and [ADR 043](../decisions/043-twc-fpv-presentation-layer.md).

## Shaders (Shader Graph—first)

| Use Shader Graph | Use HLSL (exception) |
|------------------|----------------------|
| FPV dungeon walls/floor/doors | Custom fullscreen blit with no graph equivalent |
| Battle arena backdrop & slot lighting | Compute-style pass (if used) |
| Character/enemy sprites — lit/unlit | Extremely hot path after profiling |
| Hit flash, poison tint, Synchro burst VFX | Porting legacy `.shader` until rebuilt in Graph |
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
| Grid step lerp, bump nudge, FOE slide-in | Boss / Protocol `Cinematic` beats |
| UI fades, map pan, combat log pop | `CinematicQTE` authored camera + timing |
| Fixed-skill target zoom punch, hit flash, light screen shake | Anything needing keyed tracks / multiple actors |

**Conventions**

- Import **DOTween** from the Asset Store into `Assets/Plugins/Demigiant/DOTween/`; enable modules needed at setup (UI, 2D, etc.).
- Game runtime assemblies reference `DOTween` / `DOTween.Modules` as needed; no tween logic in `CombatSimulator` (pure C# tests).
- Prefer `Sequence` / `Tween` over hand-rolled lerps; kill or complete tweens on scene unload, combat end, and explorer disable (`DOTween.Kill` on owning transforms).
- Exploration input: poll movement/turn `IsPressed` when explorer lerp completes for hold-to-repeat; displacement priority over turn; no buffered input during lerp ([ADR 001](../decisions/001-grid-movement.md)).
- Exploration lerp durations: four presets (Slow / Normal / Fast / Very Fast); default Normal **0.32s** step, `OutQuad` ([ADR 018](../decisions/018-exploration-animation-speed.md)).
- **Timeline** stays the source of truth for sparse cinematic skills; do not duplicate the same beat in both Timeline and DOTween unless one drives the other.

### UI reactivity

**Hub, exploration, and combat** HUDs share the same launch bar: on state change, the UI **animates or pulses** so cause → effect reads clearly.

| Principle | Rule |
|-----------|------|
| **Event-driven** | Presenters (`*View` in `GridDungeon.UI`) subscribe to controller events (`CombatController`, `HubController` services, `MapSystem`, `DungeonExplorer`, `GamePhaseController`) and play feedback; views do not poll every frame for diffs. **Full event list:** [04 — Dev: UI event contract](04-dev/ui-event-contract.md). |
| **DOTween on Toolkit** | Short tweens on `VisualElement` style/transform (fade, scale punch, slide, fill lerp). Enable DOTween **UI** module. No tween logic in `GridDungeon.Core`. |
| **State first, motion second** | Apply authoritative values immediately (HP, map cells, queue order); animate **from** the previous visual state. |
| **Blocking (EO-style)** | Hold a **presentation lock** until mandatory UI tweens for the current beat finish. The **next** player action (combat command, hub confirm, etc.) is ignored until unlock. **Summon/auto turns** use the same lock — play the full highlight → VFX → log chain before the queue advances ([summons](02-systems/summons-and-guests.md)). Exploration grid step already blocks movement during lerp ([ADR 001](../decisions/001-grid-movement.md)); map/HUD feedback for that step may run in parallel or complete before the next step is accepted — pick one per beat in the phase doc tables. |
| **Duration** | Typical UI feedback **0.1—0.4s**; Synchro meter fill and HP drops may use **0.2—0.6s**. Longer motion belongs in [combat presentation](02-systems/combat-presentation.md) (camera/VFX), not HUD chrome. |
| **Cleanup** | `Kill` / complete tweens on `OnDisable`, phase exit, and combat end (see [Animation](#animation-dotween--timeline) above). |

**launch checklists by phase:**

| Phase | Doc |
|-------|-----|
| Combat | [combat — UI motion & feedback](02-systems/combat.md#ui-motion--feedback) |
| Exploration | [mapping — Map UI motion](02-systems/mapping.md#map-ui-motion) |
| Hub | [hub — Service UI motion](02-systems/hub-and-services.md#service-ui-motion); [hub — environment camera pan](02-systems/hub-and-services.md#hub-environment-presentation) (**later**, non-blocking) |

**Deferred (later):** global **reduce UI motion** accessibility toggle; keep tween durations in data/prefs so scale-to-zero is trivial later.

## High-level modules

```
GameState (composition root)
+-- GamePhaseController  — Hub | Exploration | Combat ([ADR 017](../decisions/017-game-phase-controller.md), [game phase](02-systems/game-phase.md))
—   +-- HubPhaseController
—   +-- ExplorationPhaseController
—   +-- CombatPhaseController
+-- HubServices          — explorers guild, navigator office, shop, hospital, inn save
+-- DungeonExplorer      — grid step, facing, interact; `m_poseRoot` (e.g. **PartyPose**) for world lerp — see [party pose vs grid](02-dungeon-navigation.md#party-pose-vs-grid-coordinates)
+-- ExplorationGridMetrics (Core) — `WorldUnitsPerCell` (10), corner→world math shared with floor art
+-- FloorArtPresenter    load FPV prefabs by `floorKey` via `FloorArtCatalog` ([#102](https://github.com/miramocha/griddungeon-game/issues/102)); MeshBackend registry Default or TWC plugin ([#344](https://github.com/miramocha/griddungeon-game/issues/344))
+-- DungeonView          FPV mount / visibility (hidden during combat); per-cell blobber deferred
+-- CombatScenePresenter — battle backdrop + enemy slot rig ([combat scene](02-systems/combat-scene.md))
+-- MapSystem            — auto-reveal layer, fog, read-only UI
+-- FoeSystem            — spawn, visibility, step patrol, contact
+-- PartyRuntime         — 6 core + 0—2 aux combatants, skills; mirrors SaveGame.PartyInventory
+-- InventoryRules (Core) — bag add/stack/equip; InventoryBagCatalog (tab filter); EquipmentStatAggregator
+-- NavigatorRuntime     — active navigator, aura application, roster
+-- ProtocolSystem       — Synchro Charge gain/spend (`SynchroBar`); Navigator invokes Protocol on core turn at 100%
+-- CombatController     — AGI queue + command planning + Protocol → EndRound; `ActionStepDelaySeconds` default **0.55s** between resolved actions (0 in tests)
+-- CodexSystem          — enemy knowledge / weaknesses
+-- StoryEventRunner     — VN scenes; overlay lock ([#87](https://github.com/miramocha/griddungeon-game/issues/87), [ADR 028](../decisions/028-story-visual-novel-events.md), [story events](02-systems/story-events.md))
+-- ContentDatabase      — strata, floors, side dungeons (optional), FOE, encounters
+-- SaveSystem           — hub save + per-floor revealed map + FOE state
```

**Dev bootstrap:** `DevBootstrap.unity` (not in git; regenerate locally) + UI Toolkit `GamePhaseDevHud` drives Hub → Exploration → Combat → Hub for macro-phase smoke tests ([game phase](02-systems/game-phase.md#dev-bootstrap-hud-ui-toolkit)). **F3** uses two dev cores + slime when the party roster is empty (AGI order 14 → 9 → 5). Editor: **GridDungeon → Tools → Dev Tools** (phase shortcuts), **Save Editor** (inn save F5, campaign flags, Edit Mode write — [PR #84](https://github.com/miramocha/griddungeon-game/pull/84)), **Dev Tools Map**. Game repo: **GridDungeon → Scenes → Create Dev Bootstrap**.

## Map system

- **Revealed layer** (saved per floor):
  - `visited` floor tiles
  - `wallMask` per cell edge (set on bump + perimeter reveal)
  - `features`: door state, stairs, chest opened, trap triggered
  - `foeIcons`: last known FOE cell when in LOS
- **Truth layer** — designer collision (editor only); never sent to client as full download
- **UI:** read-only grid; pan/zoom; no edit raycasts
- `MapReveal.OnPartyEnteredCell`, `OnBumpWall(side)`, `OnInteract(type)`
- **Save packing:** [map-reveal-save-format.md](02-systems/map-reveal-save-format.md) — `FloorMapStateCodec` (`Visited` / `Walls` packed ints, features/FOE structs)

### Map authoring & HUD ([ADR 002](../decisions/002-mapping-model.md#technical-notes-unity--authoring--runtime-map))

| Concern | Approach |
|---------|----------|
| **Authoring (primary)** | **Floor Editor** (Unity Editor) → exports **`ExplorationFloor`** SO: tiles, **edge walls**, features, FOE spawns/patrol — epic [#75](https://github.com/miramocha/griddungeon-game/issues/75), spec [floor-editor.md](02-systems/floor-editor.md) |
| **Authoring (FPV)** | Stratum template or custom floor art prefab per `floorKey`; same grid alignment; does not drive HUD map — [floor-art-fpv.md](02-systems/floor-art-fpv.md) ([#102](https://github.com/miramocha/griddungeon-game/issues/102)) |
| **Runtime HUD (primary)** | **`ExplorationMapCoordinator`** + `MapGridPaintController` — 2D UI Toolkit grid from `ExplorationFloor` + `FloorMapState` reveal; refresh on dirty |
| **Fog** | Unrevealed cells/edges hidden in 2D view from `Visited` / `WallMask` |
| **Party / FOE** | Icons on 2D map at `(x, y, level)`; patrol updates view without RT |
| **Verticality** | Cell `(x,y,level)`; jump pads / stairs in painter data ([ADR 019](../decisions/019-floor-verticality.md)) |
| **Collision** | Same `ExplorationFloor` truth as painter output — `MapSystem` / `FloorCollisionQuery`, not HUD drawables |
| **Deferred** | MapProxy + minimap camera → RT (optional 3D debug preview only) |

**Game repo folders:** `Assets/Content/Floors/{stratum}_{floorId}.asset`; custom FPV prefabs under `Assets/Content/FloorArt/Prefabs/Floors/`. Editor: `GridDungeon.Editor` floor painter when implemented.

### Map cell art assets

Sprite checklist, composite wall rules (edge segments — no 16 autotiles), door overlay tints, and USS class list: **[map-cell-art.md](02-systems/map-cell-art.md)**. Implementation: [game #38](https://github.com/miramocha/griddungeon-game/issues/38); shared painter: [#26](https://github.com/miramocha/griddungeon-game/issues/26). Campaign gates → map icons: [#33](https://github.com/miramocha/griddungeon-game/issues/33).

## Side dungeons (sketch) (optional)

- **Save/map keys:** `{locationId}_{floorId}` — e.g. `sd01_F1` (not `s1_B1F`). Same `FloorMapStateSave` / `FoeStateSave[]` dictionaries as strata ([side dungeons](02-systems/side-dungeons.md), [ADR 022](../decisions/022-side-dungeons-mvp3.md)).
- **`ExplorationStateSave`:** add `ExplorationMapKind` (`Stratum` | `SideDungeon`) + `locationId` + `floorId` on active dive.
- **Hub entry:** `HubController.EnterSideDungeon(locationId, floorId)` — parallel to `LeaveHub`; loads floor SO from `ContentDatabase` by side key.
- **Content path (draft):** `Assets/Content/SideDungeons/sd01_F1.asset`
- **Stratum-only save:** `HubSaveData.UnlockedWarpGateStrata` (hub **Depart** after in-world gate unlock); does not track side locations — use `UnlockedSideDungeonIds` or quest flags.

## Autopilot

- **`MapPathfinder`** (`GridDungeon.Core`) — generic **A\*** with Manhattan heuristic + binary heap; injectable node/edge predicates ([autopilot pathfinding](04-dev/autopilot-pathfinding.md))
- **`ExplorationPathGraph`** (`GridDungeon.Runtime`) — revealed walkable graph (visited cells, layout walkability, walls, closed doors) → calls `MapPathfinder`
- **`AutopilotPathWalker`** (`GridDungeon.Core`) — path index → next turn or step
- **`AutopilotController`** — destination pick, walk state, combat **suspend/resume**, overlay events; `DungeonExplorer` commits lerps + step events ([autopilot](02-systems/autopilot.md), [ADR 021](../decisions/021-autopilot-mvp2.md))
- **UI:** `ExplorationMapCoordinator` + expanded map — **Z** arm path, arrows/click cursor, path overlay via `MapGridPaintController` (not side minimap pick yet)
- **Layout validation** uses **`FloorLayoutConnectivity`** on raw `ExplorationFloor` (delegates to `MapPathfinder`; not autopilot fog/walls) ([autopilot pathfinding — vs FloorLayoutConnectivity](04-dev/autopilot-pathfinding.md#vs-floorlayoutconnectivity-layout-connectivity))
- Cancel on manual input, blocked step, or unreachable resume; combat suspends with optional resume after fight

## Gathering & fishing

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

At launch: step patrol system in core; early floors mostly `stepsPerMove: 0` or 1-cell paths. No combat-round FOE movement.

## Combat

- `TurnQueueBuilder.Build(combatants)` sorted by AGI (+ Speed Up/Down from [status system](02-systems/combat-status-and-buffs.md))
- `StatusSystem` (Core) — apply/refresh/tick/cleanse using `StatusData` DTOs; SO `StatusDefinition` in Runtime via `ContentDatabase.ToStatusData`
- `EndOfRoundPipeline` — regen → DoT → decrement durations → FOE patrol (optional)
- UI binds to queue head; advance on action complete
- `CombatSimulator` pure C# for tests (status inflict + tick unit tests)

## Navigator

- `NavigatorDefinition` — aura modifiers, protocol skill ids, `unlockCondition`
- `PartyRuntime.ActiveNavigatorId`; `UnlockedNavigatorIds` (flags from strata/quests/events)
- `AuraSystem.ApplyPassives(coreSix)` on combat start / navigator swap
- Not in `Combatant` AGI list; **excluded from targeting** (including boss AOEs); separate UI strip, no HP
- **Explore:** bottom-right **3D presence** in exploration + combat; Protocol Deploy/Transform transition model into aux / core slot rigs — [navigator — Consider / explore](02-systems/navigator.md#consider--explore--navigator-3d-presence) at launch still portrait strip)

## Synchro Protocol (team bar)

- `SynchroBar` float 0—1 on `PartyRuntime` (Synchro Charge)
- `ProtocolSystem` — bar fill from core actions; spend on `CombatCommand.Protocol`
- Core turn at Synchro == 1: player picks `protocol_strike` / `protocol_mend` from Navigator kit
- S1: tutorial FOE — crisis AOE, VN unlock, guided `protocol_strike`, hub warp ([story-events](02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)); guided HUD — [guided-tutorial](02-systems/guided-tutorial.md), [s1 beats](03-content/campaign/s1-guided-tutorials.md)
- `ProtocolSkillDefinition` — participant count, effect, presentation id
- Save: `synchroBar` + `activeNavigatorId` per dive
- FOE state: persist on floor during dive; **reset FOE spawns** on hub return + re-enter

## Exploration HUD (UI Toolkit)

Shipped on **`ExplorationHud`** (`ExplorationHudView` — **no** `UIDocument`) + sibling **`ExplorationMap`** (`ExplorationMapCoordinator`, `MinimapPanelView`, `ExpandedMapOverlayView`). Pause / party menu: sibling **`PartyMenuOverlay`**. Party strip: **`PartyFormationFloater`** ([centralized UI services](04-dev/centralized-ui-services.md)). Full bind diagrams, document map, input routing, and replacement checklist: **[exploration UI](02-systems/exploration-ui.md)**.

- Map surfaces — C# `MapGridHostBuilder` per `UIDocument` under `ExplorationMap` ([#244](https://github.com/miramocha/griddungeon-game/pull/244)); integrator: [ui-event-contract](04-dev/ui-event-contract.md), [custom party UI](04-dev/custom-party-ui.md).
- `MapGridPaintController` — cell grid via `MapGridPainter`; marker overlays via `MapPartyMarkerPresenter`, `MapFoeMarkersPresenter`, `MapGatherMarkersPresenter`, `MapHubEntranceMarkersPresenter`, `MapGridMarkerAnimator` ([#90](https://github.com/miramocha/griddungeon-game/pull/90), [#244](https://github.com/miramocha/griddungeon-game/pull/244)).
- Pause — `Esc` when map not fullscreen; quit confirm → `RequestQuitToTitle` ([ADR 014](../decisions/014-mvp1-exploration-map.md)).
- **Exploration log** — not wired (combat log only). **Map refactor** (read model): [exploration UI appendix](02-systems/exploration-ui.md#appendix--future-map-read-model-refactor).
- **Layered panels (draft):** exploration Tier 1 **shipped** (map + floater + pause as sibling docs); combat still monolithic — [ADR 037](../decisions/037-layered-uitk-panels.md), [dev note](04-dev/layered-uitk-panels.md).

## Combat HUD (UI Toolkit)

**Shipped** — epic [#179](https://github.com/miramocha/griddungeon-game/issues/179) via [PR #182](https://github.com/miramocha/griddungeon-game/pull/182) ([#180](https://github.com/miramocha/griddungeon-game/issues/180) frame — [#181](https://github.com/miramocha/griddungeon-game/issues/181) log modal). Spec: [combat — Combat HUD frame layout](02-systems/combat.md#combat-hud-frame-layout). Full-screen `combat-hud` (`position: absolute; inset: 0`, `flex-direction: row`):

```
command-rail | center column (log-preview → arena-spacer → synchro) + PartyFormationFloater + CombatArenaPlate overlays | turn-order-strip
```

- **Left rail** — `combat-hud__command-rail` → `command-panel` (vertical column, centered in rail). Button order: Attack → — → Flee → **Back** (DOM matches focus navigator).
- **Top center** — `combat-log-preview-row` only (round + one line). **Enemy HP plates** — transient `CombatArenaPlatePresenter` @ sort **15** above arena slot anchors ([ADR 046](../decisions/046-combat-arena-plates-camera.md)); not embedded in `CombatHud`.
- **Bottom center** — `synchro-bar` in center column (**Protocol** when Synchro 100% — `C` / LMB); party plates on shared **`PartyFormationFloater`** (combat-center inset; HP + MP on cores).
- **Log** — `combat-log-preview-row` (round + one line; no Log button); modal via **`V`** or preview click; title + scroll only; close via **`V`**, **`X`** / Back (`TryBack` — log before pickers), or backdrop click (not scroll).
- **Centralized UI services** — cross-phase `UIDocument` overlays (`InputHintPresenter`, `CombatArenaPlatePresenter`, `CommandRailPresenter` + `CommandPanelModalSupport`, `PartyFormationFloater`, `ScreenFadePresenter`), `sortingOrder` stack, bootstrap: [centralized UI services](04-dev/centralized-ui-services.md). **Input hints** — bind copy only on global strip (`sortingOrder` 300); `InputHints.Publish` / `Clear`; constants in `TabbedPickerRailHints` ([shared menu & picker UI](04-dev/shared-menu-picker-ui.md#global-input-hints); agent rule `unity-global-input-hints.mdc`).
- **Right rail** — `turn-order-strip` vertical flat AGI queue (top → bottom = soonest → latest).

`CombatArenaPlate.EnemyRoster.BindEnemyFormation` — `EnemySlots[0..2]` → front, `[3..5]` → back. Party: `PartyFormationFloater.Grid` (`PartyFormationGridView`). Replace/reskin: [custom party UI](04-dev/custom-party-ui.md).

- **Skill use picker** — modal cloned from `SkillUsePicker.uxml`; `CombatSkillPickerHost` + `ISkillUsePickerView` ([#138](https://github.com/miramocha/griddungeon-game/issues/138)). Integrator: [custom skill picker UI](04-dev/custom-skill-picker-ui.md).
- **Shared UITK menus** — `RailMenuPresenter`, `ItemListPickerView`, `SkillUsePickerToolkitView`, `WindowedListPaneView`, `PickerTabStripView` — composition diagram and consumers: [shared menu & picker UI](04-dev/shared-menu-picker-ui.md).
- AGI strip — flat list only (no enemy row grouping); USS ellipsis for names ([#66](https://github.com/miramocha/griddungeon-game/pull/66)).
- Stale queued target: USS `combat-arena-plate__slot--stale-target` on enemy/party roster during planning ([#65](https://github.com/miramocha/griddungeon-game/issues/65)).
- **Reactive HUD ([#35](https://github.com/miramocha/griddungeon-game/pull/35), [#395](https://github.com/miramocha/griddungeon-game/pull/395)):** `CombatHudReactivePresenter` + `CombatPresentationGate` — wind-up, sequential multi-target HP beats ([#397](https://github.com/miramocha/griddungeon-game/pull/397)), death beat + staggered `EnemyRowCollapse`; DOTween beats block AGI until complete; `CombatHudLogView` owns log format + preview/modal. Mid-fight story: `EncounterEventScheduler` on `CombatController`.
- **Roster vitals bars:** UITK `ProgressBar` via `RosterStatMeter` on party/enemy roster slots; synchro meter uses the same control — `CombatHudReactivePresenter` still lerps displayed values on damage/heal beats.
- **Shared panel scale:** `GamePanelSettings.asset` — Scale With Screen Size, reference **1920—1080**, **Match Height** (exploration + combat `UIDocument` panels).

## Combat scene

- `CombatEntryContext` → `BattleBackground` + `EncounterGroup` → spawn on `EnemySlot_0..5` ([ADR 013](../decisions/013-combat-scene-rendering.md))
- `CombatScenePresenter.SpawnEnemyVisuals` / `ClearAndDestroyEnemyVisuals` — `EnemyDefinition.battlePrefab` on slot rig ([ADR 046](../decisions/046-combat-arena-plates-camera.md))
- `CombatScenePresenter.GetEnemySlotAnchor(int slotIndex)` — `slotIndex` `0..5` matches UI + `Combatant.SlotIndex`
- Exploration `DungeonView` paused/hidden; grid anchor unchanged until fight ends
- Enemy **grid sprite** (exploration) vs **battle prefab/sprite** (arena) — separate assets per id

## Combat presentation

- `BattleCameraRig` — fixed angle on arena rig; `NudgeZoomToTarget` on action commit + enemy target pick; `BattleCameraFocusPolicy` ([ADR 046](../decisions/046-combat-arena-plates-camera.md) · [combat presentation](02-systems/combat-presentation.md))
- `SkillDefinition.presentation`: `Fixed` | `Cinematic` | `CinematicQTE`
- `Fixed` — VFX at slots; optional subtle zoom to primary target, then reset
- `Cinematic` / `CinematicQTE` — `PlayableDirector` + Timeline; end on `stopped`; QTE beats via Timeline **markers** ([ADR 027](../decisions/027-combat-cinematic-timeline-events.md))
- `CinematicQTE` — `QTEController` tiers → damage bonus; skill always resolves base on miss/skip
- At launch: all skills `Fixed`; cinematic + QTE stubbed
- MVP2: 1— `CinematicQTE` party skill + 1— boss `Cinematic` sample

## Grid / content

- `ExplorationFloor` ScriptableObject: grid, spawns, FOE list, encounter rate
- Labels: `B1F` within `Stratum01`

## Save format (EO-oriented)

```json
{
  "hub": { "credits": 0, "unlockedWarpGateStrata": ["s1", "s2"] },
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
+------------------------------------+
—   FPV dungeon view  —  Map (view)  —
—                     —  read-only   —
+------------------------------------—
—  Log / party strip (HP, status)    —
+------------------------------------+
```

Combat replaces layout with turn order + **4+4 rows** (core + aux).

## Combatant types

```csharp
enum CombatantKind { Core, Summon, Guest, Enemy }
```

- `PartyRuntime` — 6 core, always
- `CombatController` — spawns aux from skills/scripts; clears on battle end
- Summon AGI turn — `IsWaitingForPlayer` + filtered command panel ([ADR 016](../decisions/016-summon-control-mvp1.md)); **no** auto `SummonScriptRunner` for player summons

## Performance

- 60 FPS exploration with map visible
- FOE patrol: =10 active FOEs per floor
- Floor size: 40—40 soft max (EO floors vary)

## Open technical decisions

- [x] Map fullscreen: movement **pass-through** ([ADR 014](../decisions/014-mvp1-exploration-map.md))
- [x] Wall reveal: **bump + cell perimeter** ([ADR 014](../decisions/014-mvp1-exploration-map.md))
- [ ] **Map during combat:** persistent panel vs `M` toggle vs threat ping — [mapping — Consider / explore](02-systems/mapping.md#consider--explore--map-during-combat) (revisit with [ADR 005](../decisions/005-foe-combat-patrol.md))
- [ ] **Navigator 3D presence:** corner model (explore + combat) + Deploy/Transform slot transitions — [navigator — Consider / explore](02-systems/navigator.md#consider--explore--navigator-3d-presence); optional Tier 2 under [ADR 037](../decisions/037-layered-uitk-panels.md)
- [ ] **Layered UITK panels:** exploration + combat HUD split into panel components — [ADR 037](../decisions/037-layered-uitk-panels.md) (draft epic)
- [ ] Default `stepsPerMove` per stratum (tune 2—5 in data)
- [ ] **Floor Editor** → `ExplorationFloor` export — [#75](https://github.com/miramocha/griddungeon-game/issues/75) epic; launch floors hand-filled via builders until [#77](https://github.com/miramocha/griddungeon-game/issues/77)
- [ ] Custom Unity editor for FOE patrol paths + `stepsPerMove` (can merge into floor painter)

## Related docs

- [05 — class design](05-class-design.md) — assembly map, C# type catalog
- [Game phase](02-systems/game-phase.md) — design goals, diagrams, `GamePhaseController` + phase controllers ([ADR 017](../decisions/017-game-phase-controller.md))
- [Mapping](02-systems/mapping.md)
- [ADR 002](../decisions/002-mapping-model.md)
- [ADR 003](../decisions/003-foe-step-patrol.md)
- [ADR 012 — Unity 6 stack](../decisions/012-unity-6-stack.md)
