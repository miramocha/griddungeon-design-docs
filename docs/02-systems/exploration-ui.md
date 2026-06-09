# Exploration UI (UI Toolkit)

How the **exploration HUD** is composed, bound, and wired to runtime systems in **griddungeon-game**. Use this when replacing or extending exploration chrome (map panel, pause overlay, future party strip) without re-tracing the scene graph.

**Related:** [mapping — Map UI](mapping.md#map-ui) (player-facing behavior), [game phase](game-phase.md) (macro phases + input maps), [input bindings](input-bindings.md), [map cell art](map-cell-art.md), [ADR 014 — MVP1 exploration map](../../decisions/014-mvp1-exploration-map.md). **Integrator:** [UI event contract](../04-dev/ui-event-contract.md), [custom party UI](../04-dev/custom-party-ui.md).

**Game repo entry points:**

| Piece | Path |
|-------|------|
| Shell UXML | `Assets/UI/Screens/Exploration/ExplorationHud.uxml` |
| Styles | `ExplorationHud.uss`, `MapView.uss`, `Shared/HudOverlay.uss` |
| Orchestrator | `Assets/Scripts/UI/Views/ExplorationHudView.cs` |
| Map panel | `Assets/Scripts/UI/Views/MapView.cs` |
| Map marker overlays | `MapPartyMarkerPresenter`, `MapFoeMarkersPresenter`, `MapGatherMarkersPresenter`, `MapHubEntranceMarkersPresenter`, `MapHubEntranceMarkerRules`, `MapGatherMarkerRules`, `MapGridMarkerAnimator` |
| Party / pause menu | `Assets/Scripts/UI/Views/PartyMenuOverlayView.cs` (shared `PartyMenu.uxml`; Quit on hub + exploration) |
| Grid paint helpers | `Assets/Scripts/UI/MapGridPainter.cs`, `MapGridStyleClasses.cs` |
| Map overlay art catalog | `Assets/Scripts/UI/MapCellArtCatalog.cs`, `Assets/UI/Map/MapCellArtCatalog.asset`, `MapCellArtPsdSpriteSync` (Editor) |
| Input | `Assets/Scripts/UI/Input/InputRouter.cs`, `ExplorationInputHandler.cs`, `MapInputHandler.cs` |
| Scene wiring (Editor) | `DevBootstrapSceneCreator.cs`, `DevSceneComposition.WireExplorationHud` / `WireMapView` |

---

## Design note: partial map presenters (shipped)

Combat HUD uses **reactive presenters** + `CombatPresentationGate` ([#35](https://github.com/miramocha/griddungeon-game/pull/35)). Exploration is **split**: cell grid is imperative (`MapView` + `MapGridPainter`); **party / FOE / gather / hub-gate** use overlay presenters + `MapGridMarkerAnimator` ([#90](https://github.com/miramocha/griddungeon-game/pull/90), [#94](https://github.com/miramocha/griddungeon-game/pull/94)); **party strip** + `ExplorationPresentationGate` + `ExplorationHudReactivePresenter` ([#36](https://github.com/miramocha/griddungeon-game/issues/36)); **pause** shares the hub **party menu** shell (`PartyMenuOverlayView` — Inventory / Equipment / Quit on exploration). **Runtime event index:** [UI event contract](../04-dev/ui-event-contract.md). A custom HUD can reuse the same hooks without changing phase authority.

**Future map refactor (optional):** [Appendix — future map read-model refactor](#appendix--future-map-read-model-refactor) — same runtime hooks, shared `MapGridPainter`; not required for a custom skin.

---

## Scene composition

Dev bootstrap creates one GameObject **`ExplorationHud`** under the game root:

```mermaid
flowchart TB
    subgraph GameRoot["Game (GameState, systems…)"]
        GS[GameState]
        EX[DungeonExplorer]
        MS[MapSystem]
        GB[GameBootstrap]
    end

    subgraph ExplorationHudGO["GameObject: ExplorationHud"]
        DOC[UIDocument + PanelSettings]
        EHV[ExplorationHudView]
        MV[MapView]
    end

    subgraph PartyMenuGO["GameObject: PartyMenuOverlay"]
        PMO[PartyMenuOverlayView]
    end

    subgraph World["GameObject: DungeonView"]
        DV[DungeonView — visibility only]
    end

    IR[InputRouter]

    GB -->|Start: Bind| IR
    IR --> GS
    EHV --> DOC
    EHV --> MV
    MV --> GS
    MV --> EX
    MV --> MS
    PMO --> GS
    IR --> EHV
    IR --> PMO
```

| Component | Serialized / wired to |
|-----------|------------------------|
| `ExplorationHudView` | `VisualTreeAsset` → `ExplorationHud.uxml`, `GameState`, `MapView` |
| `MapView` | `GameState`, `DungeonExplorer`, `MapSystem`, `PartyMenuOverlayView`, `MapView.uss` |
| `PartyMenuOverlayView` | `PartyMenu.uxml`, bag/equipment panes, `GameState`, exploration/hub HUD refs |
| `InputRouter` | `GridDungeon.inputactions`, `DungeonExplorer`, `CombatController`, `ExplorationHudView`, `PartyMenuOverlayView` |

Regenerate scene refs: **GridDungeon → Scenes → Create Dev Bootstrap** (game repo).

---

## UXML load and mount lifecycle

`ExplorationHudView` is the **only** type that clones exploration HUD UXML. On `OnEnable` it clears `UIDocument.rootVisualElement`, clones the tree, queries named roots, and delegates:

```mermaid
sequenceDiagram
    participant EHV as ExplorationHudView
    participant DOC as UIDocument.rootVisualElement
    participant UXML as ExplorationHud.uxml
    participant MV as MapView
    EHV->>DOC: Clear()
    EHV->>UXML: CloneTree(host)
    EHV->>DOC: Q("exploration-hud")
    EHV->>DOC: Q("map-view-mount")
    EHV->>MV: BindToHud(mapMount, document, sortOrder)
```

On `OnDisable`, `MapView.ReleaseFromHud()` runs before the document is torn down. Pause / party menu lives on sibling **`PartyMenuOverlay`** (`UIDocument` sort **250**).

### UXML element map

| `name` (UXML) | Bound by | Notes |
|---------------|----------|--------|
| `exploration-hud` | `ExplorationHudView` | Root container |
| `map-view-mount` | `MapView.BindToHud` | **Empty mount** — map UI built in C# |
| `party-formation-floater-host` | `ExplorationPartyStripView` | Bottom party floater (2×4); slides off-screen when hidden; `ExplorationHudReactivePresenter` syncs on step/cell/phase |
**Hybrid layout:** the **map grid** is **programmatic** (`MapView.BuildMapTree` adds `map-view`, title, hint, `map-view-grid` under the mount). Pause / quit UI is in shared **`PartyMenu.uxml`** (`party-menu-section-quit`, `party-menu-pane-quit`).

---

## View responsibilities and data sources

```mermaid
flowchart LR
    subgraph UXML_Dynamic["Built under map-view-mount"]
        MAP[map-view tree]
    end

    subgraph Runtime["Runtime"]
        GS[GameState.PhaseChanged]
        EX[DungeonExplorer events]
        MS[MapSystem.RevealChanged]
    end

    PMO[PartyMenuOverlayView]
    MV[MapView]

    PMO --> GS

    MV --> MAP
    MV --> GS
    MV --> EX
    MV --> MS
    MV -->|MapGridPainter| MAP
```

### MapView (push updates)

| Subscription | UI effect |
|--------------|-----------|
| `GameState.PhaseChanged` | Show map only in `GamePhase.Exploration`; hide on Hub/Combat; reset fullscreen |
| `MapSystem.RevealChanged` | Repaint fog / walls / stairs on dirty cells; marker presenters sync visibility |
| `DungeonExplorer.OnPartyEnteredCell` / `OnPartyFacingChanged` | `MapPartyMarkerPresenter` slide / snap (not a cell glyph) |
| `FoeSystem.OnFoePatrolMoved` | `MapFoeMarkersPresenter` slide; `MapView` repaints patrol endpoint **cells** after overlay motion |
| `GameState.ExplorationBindingsWired` | Re-subscribe party/FOE markers **after** `MapSystem` visit handler so reveal runs before marker handlers ([#90](https://github.com/miramocha/griddungeon-game/pull/90)) |
| `GameState.PhaseChanged` → Exploration | Restore party marker after combat ([#94](https://github.com/miramocha/griddungeon-game/pull/94)) |
| Floor layout | `GameState.Content.GetFloor` + `MapSystem` visit/wall/feature state |

Cell paint priority: [map-cell-art](map-cell-art.md), [mapping § Map cell art](mapping.md#map-cell-art-2d-schematic). Overlay layers: [§ Map marker overlays](#map-marker-overlays).

### Map marker overlays

Built under `map-view-grid-host` (siblings above `map-view-grid`):

| Layer (bottom → top) | Presenter | Visibility / rules |
|----------------------|-----------|-------------------|
| `map-view-gather-markers` | `MapGatherMarkersPresenter` | `HasGatherNode` + visited (or dev reveal-all); `map-view__marker--gather` |
| `map-view-hub-entrance-markers` | `MapHubEntranceMarkersPresenter` | B1F `stairsUp` gate when visited — `MapHubEntranceMarkerRules` |
| `map-view-foe-markers` | `MapFoeMarkersPresenter` | FOE in LOS / last known; patrol slide via `MapGridMarkerAnimator` |
| `map-view-party-markers` | `MapPartyMarkerPresenter` | Party cell + facing; lerp with step; resync on return from combat |

`MapGridMarkerAnimator` — shared fade/slide tweens; FOE patrol is **ambient** (does not block exploration input). Dev **Tools → Dev Tools Map** can pass `revealAllMarkers` for preview.

Fullscreen map raises `UIDocument.sortingOrder` so the panel draws above the side layout; `M` / `Esc` behavior is in [input bindings](input-bindings.md) and `MapInputHandler`.

### Party / pause menu (`PartyMenuOverlayView`)

**`Tab`** or **`Esc`** (when map not fullscreen) opens the same overlay when safe ([ADR 034](../../decisions/034-skill-point-allocation-outside-combat.md)) — vertical section rail (**W/S**; **Z** reveals pane):

| Section | Hub | Exploration |
|---------|-----|-------------|
| **Inventory** | Category-tabbed bag | Same |
| **Equipment** | Member tabs + worn slots + picker | Same |
| **Formation** | Bottom floater 2×4 swap (`PartyFormationFloaterView`) | Same |
| **Quit to title** | Confirm pane → `GameState.RequestQuitToTitle()` (no inn save) | Same |

Closing the menu after equipment changes refreshes the exploration **party strip** (HP/MP) without requiring a dungeon step.

**Formation:** core slot swap via shared `PartyFormationFloaterView` — bottom 2×4 grid floater (exploration strip + formation menu; slides off-screen when irrelevant). Bind copy on global `InputHints`. **Deferred:** **Skills** (ADR 034), **Tutorial codex** ([ADR 029](../../decisions/029-guided-tutorial.md)).

Spec: [items & inventory](items-and-inventory.md) · [ADR 036](../../decisions/036-party-inventory-model.md) · [shared menu & picker UI](../04-dev/shared-menu-picker-ui.md) · [input bindings](input-bindings.md).

When the menu is open, `InputRouter` unbinds exploration movement. Quit confirm copy stays on the pane body (not the global hint strip).

---

## Input routing

`GameBootstrap` calls `InputRouter.Bind(GameState)` at play start. The router listens to `GameState.PhaseChanged` and enables action maps per phase ([game phase — Input maps](game-phase.md#input-maps-per-phase)).

```mermaid
flowchart TB
    IA[GridDungeon.inputactions]
    IR[InputRouter]
    GS[GameState.PhaseChanged]

    IR --> GS
    GS -->|Exploration| EIH[ExplorationInputHandler]
    GS -->|Exploration| MIH[MapInputHandler]

    EIH --> EX[DungeonExplorer]
    MIH --> MV[MapView]
    MIH --> PMO[PartyMenuOverlayView]

    PMO -->|OpenStateChanged| IR
    IR -->|menu open| EIH
```

| Input (Exploration) | Handler | Target |
|---------------------|---------|--------|
| W/S/A/D, Q/E, Interact | `ExplorationInputHandler` | `DungeonExplorer` step / turn / interact |
| `M` | `MapInputHandler` | `MapView.ToggleFullscreenFromInput()` |
| `Esc` | `MapInputHandler` | Exit map fullscreen, or toggle party/pause menu |
| `Tab` | `PartyMenuInputHandler` | Toggle same menu |
| `Esc` (map focused, backup) | `MapView` key callback | Exit fullscreen if UI Toolkit has focus |

When the menu is open, exploration movement actions are **unbound** so the party cannot walk under the overlay.

---

## Phase system vs UI visibility

**Two parallel “exploration” layers:**

| Layer | Type | Phase behavior |
|-------|------|----------------|
| `DungeonView` / `FloorArtPresenter` | World / FPV (`SetVisible`; authored art load [#102](https://github.com/miramocha/griddungeon-game/issues/102)) | `ExplorationPhaseController` shows; `CombatPhaseController` hides |
| `ExplorationHud` + `MapView` | UI Toolkit | Map gated on `GamePhase.Exploration`; party/pause menu on overlay `UIDocument` |
| `DungeonExplorer` + `MapSystem` | Simulation | `ExplorationPhaseController` wires on enter, unwires on exit |

The **`ExplorationHud` GameObject is not disabled** on Hub or Combat. Visibility is **per-widget** (`MapView` display / pause overlay classes), not by destroying `ExplorationHudView`.

```mermaid
stateDiagram-v2
    [*] --> Hub
    Hub --> Exploration: GameState transition
    Exploration --> Combat: RequestCombat
    Combat --> Exploration: BattleEnded

    state Exploration {
        [*] --> EPC
        EPC: ExplorationPhaseController\nDungeonView visible\nexplorer ↔ map/foes
        UI: MapView visible\npause available
    }

    state Combat {
        [*] --> CPC
        CPC: CombatPhaseController\nDungeonView hidden\nCombatScenePresenter
        UI: MapView hidden\npause closed
    }
```

Phase **logic** stays in `ExplorationPhaseController` ([game phase](game-phase.md)); it does **not** reference UI Toolkit types.

---

## Replacing exploration UI (checklist)

1. **Shell:** Replace or extend `ExplorationHud.uxml` / `ExplorationHudView` (keep `UIDocument` + mount pattern, or split documents if needed).
2. **Map:** Either reuse `MapView` + `MapGridPainter`, or subscribe per [UI event contract § Exploration](../04-dev/ui-event-contract.md#exploration-phase) (see also [§ MapView](#mapview-push-updates) for per-presenter effects).
3. **Pause:** Extend `PartyMenu.uxml` sections or `PartyMenuOverlayView`; keep `MapInputHandler` + `InputRouter` party-menu wiring.
4. **Input:** Keep `ExplorationInputHandler` / `MapInputHandler` contracts, or extend `InputRouter.EnableMapsForPhase` for new maps.
5. **Do not** move floor load, reveal rules, or combat entry into UI — keep `ExplorationPhaseController` + `GameState` as authority ([architecture principles](../../.cursor/rules/architecture-design-principles.mdc)).

**Party strip:** `party-formation-floater-host` in UXML — wired via `ExplorationPartyStripView` ([#36](https://github.com/miramocha/griddungeon-game/issues/36)); event sources in [UI event contract](../04-dev/ui-event-contract.md#exploration-phase). Integrator guide: [custom party UI](../04-dev/custom-party-ui.md#exploration-party-strip).

For a **clean replacement** (not a fork of `MapView`), see [Appendix — future map read-model refactor](#appendix--future-map-read-model-refactor) below.

**Not wired (MVP1):** exploration **combat log** panel — `ExplorationHud.uxml` has no log mount; only combat uses `CombatHudLogView` ([#34](https://github.com/miramocha/griddungeon-game/issues/34)). Class-design `ExplorationHUD.Log` is target-only.

---

## Appendix — future map read-model refactor

**Status:** Design sketch (not locked ADR). **Not a blocker** for custom HUD skins — subscribe per [UI event contract](../04-dev/ui-event-contract.md) and reuse shipped `MapView` today.

| Shipped (use as-is) | Future extract ([#26](https://github.com/miramocha/griddungeon-game/issues/26)) |
|---------------------|----------------------------------------------------------------------------------|
| `MapView`, `MapGridPainter`, marker presenters ([#90](https://github.com/miramocha/griddungeon-game/pull/90)) | `ExplorationMapReadModel` — cell glyph + USS from floor + `MapSystem` |
| `ExplorationHudView`, pause, party strip, reactive presenter + gate ([#36](https://github.com/miramocha/griddungeon-game/issues/36)) | `ExplorationMapPresenter` — event wiring only; `MapGridRenderer` — paint read model |
| [Mapping § Map UI motion](mapping.md#map-ui-motion) + [UI event contract](../04-dev/ui-event-contract.md) | Same events; optional stricter gate on `RevealChanged` beats |

**Why:** `MapView` today mixes subscribe + floor resolve + paint priority + Toolkit build. Refactor splits **read model** (testable) from **renderer** (`MapGridPainter`) without moving reveal rules out of Runtime.

**Migration (ordered):**

1. Extract `ExplorationMapReadModel` from `MapView.PaintCellAt` (golden cell tests).
2. Add `MapGridRenderer` + thin `MapPanelView` shell; Dev Tools Map shares renderer.
3. `ExplorationMapPresenter` — same subscriptions as [§ MapView](#mapview-push-updates).
4. Deprecate monolithic `MapView`; keep `MapGridPainter` and marker presenters.

**Rules unchanged:** `ExplorationPhaseController`, `MapSystem`, `InputRouter` handlers; presenters never call `TryStepForward` or reveal calculators. Input still goes through `ExplorationHudView` facades (`ToggleMapFullscreen`, `OpenPause`), not presenter types.

**Gate policy:** MVP1 — movement lerp blocks steps; map tweens often parallel. Stricter EO lock (gate blocks next step after reveal stamp) is incremental — see [tech notes § UI reactivity](../04-tech-notes.md#ui-reactivity).

Type names and combat mirror table: [05 — Class design § UI layer](../05-class-design-mvp1.md#ui-layer).

---

## Related docs

- [UI event contract](../04-dev/ui-event-contract.md) — integrator / external HUD (runtime events + examples)
- [Game phase](game-phase.md) — `GamePhaseController`, dev bootstrap, input maps
- [Mapping](mapping.md) — map UX, motion table, combat map toggle
- [Input bindings](input-bindings.md) — `M` / `Esc` / exploration moves
- [Map cell art](map-cell-art.md) — glyphs, USS, sprite target
- [04 — Tech notes § Exploration HUD](../04-tech-notes.md#exploration-hud-ui-toolkit) — short index
- [05 — Class design MVP1 § UI layer](../05-class-design-mvp1.md#ui-layer) — target types vs shipped names
- [ADR 014 — MVP1 exploration map](../../decisions/014-mvp1-exploration-map.md)
