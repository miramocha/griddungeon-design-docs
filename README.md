---
tags:
  - path/root
  - type/vision
  - scope/required
  - status/active
---
# Grid Dungeon — Design Docs

First-person, grid-based, turn-based labyrinth RPG aligned with **Etrian Odyssey** — mapping as gameplay, FOE threats, guild hub loop, and AGI-driven combat turns.

**Target platform:** PC (keyboard + mouse primary).  
**Engine:** Unity 6 + URP; **Shader Graph–first** shaders ([ADR 012](decisions/012-unity-6-stack.md)).

## How to use these docs

- **Obsidian** — tag taxonomy: [obsidian-tags](docs/04-dev/obsidian-tags.md)
- **Cursor rules** — [`.cursor/rules/`](.cursor/rules/) — Unity clean-code rules (hard-linked from `griddungeon-game`) plus [architecture-design-principles](.cursor/rules/architecture-design-principles.mdc) for class/phase design in this repo
- **Vision & loop** — why the game exists and what one session feels like
- **Systems** — rules engines (movement, mapping, combat, party, hub)
- **Content** — strata, floors, monsters, FOE placement
- **Tech** — Unity 6 / URP implementation constraints
- **Dev / integrator** — [04-dev/](docs/04-dev/README.md) (e.g. [UI event contract](docs/04-dev/ui-event-contract.md), [shared menu & picker UI](docs/04-dev/shared-menu-picker-ui.md), [custom skill picker UI](docs/04-dev/custom-skill-picker-ui.md), [custom party UI](docs/04-dev/custom-party-ui.md))
- **Decisions** — ADRs when we lock a design choice
- **Refs** — visual / UX scratchpads (screenshots, links; not spec authority)
- **Release scope** — [Required, optional & later](docs/00-release-scope.md) · [project board](https://github.com/users/miramocha/projects/3) (`required` / `optional` labels)

## Release scope

| Tier | Focus |
|------|--------|
| **Required** | Hub loop, explore, FOE, AGI combat, Synchro Protocol, auto-map |
| **Optional** | Gather/fish minigames, synthesis, FOE combat patrol + mid-battle join, autopilot, side dungeons |
| **Later** | Guided coach codex, gamepad, full ailment roster, 3D hub |

See [00 — Release scope](docs/00-release-scope.md) and the [project board](https://github.com/users/miramocha/projects/3).

## Document index

Tag filters: [obsidian-tags](docs/04-dev/obsidian-tags.md). More integrator docs: [04-dev README](docs/04-dev/README.md).

### Vision & loop

| Doc | Status | Summary |
|-----|--------|---------|
| [00 — Release scope](docs/00-release-scope.md) | Active | Required, optional, later |
| [00 — Vision](docs/00-vision.md) | Draft | EO-first pillars, inspirations |
| [00 — Game references](docs/00-game-references.md) | Draft | EO + Mary Skelter, etc. — future design reference |
| [01 — Core loop](docs/01-core-loop.md) | Draft | Guild hub ↔ stratum loop |

### Systems

| Doc | Status | Summary |
|-----|--------|---------|
| [02 — Dungeon navigation](docs/02-dungeon-navigation.md) | Draft | Grid FPV, FOEs on map |
| [02 — Floor art (FPV)](docs/02-systems/floor-art-fpv.md) | Shipped | TWC runtime path, `FloorArtGrid`, wall blocks ([#344](https://github.com/miramocha/griddungeon-game/issues/344)) |
| [02 — Floor editor](docs/02-systems/floor-editor.md) | Active | `ExplorationFloor` authoring, exit links, gather pins |
| [02 — Floor transition](docs/02-systems/floor-transition.md) | Accepted | Stairs / hub vignette beats, black threshold |
| [02 — Mapping](docs/02-systems/mapping.md) | Draft | Auto-reveal only; no drawing tools |
| [02 — Map cell art](docs/02-systems/map-cell-art.md) | Active | UITK cell paint catalog, wall/floor overlays |
| [02 — Map reveal save format](docs/02-systems/map-reveal-save-format.md) | Active | Persisted reveal bitmask codec |
| [02 — Exploration UI](docs/02-systems/exploration-ui.md) | Accepted | UI Toolkit HUD: map coordinator, pause, input |
| [02 — Hub & services](docs/02-systems/hub-and-services.md) | Draft | Explorers Guild, Navigator Office, shop, hospital, save |
| [02 — Game phase](docs/02-systems/game-phase.md) | Accepted | `GamePhaseController`, phase diagrams, Enter/Exit ([ADR 017](decisions/017-game-phase-controller.md)) |
| [02 — Input bindings](docs/02-systems/input-bindings.md) | Draft | PC keyboard + mouse defaults |
| [02 — FOE encounters](docs/02-systems/foe-encounters.md) | Accepted | Contact, flee, retreat cell |
| [02 — FOE mid-battle join](docs/02-systems/chain-foe-battle.md) | Accepted | 1 FOE joins current fight / round (optional) |
| [02 — Combat](docs/02-systems/combat.md) | Draft | AGI turn order, rows |
| [02 — Combat status & buffs](docs/02-systems/combat-status-and-buffs.md) | Draft | Ailments, binds, Boost/Down, ticks |
| [02 — Combat scene](docs/02-systems/combat-scene.md) | Accepted | Battle arena + slots; not in-world FPV |
| [02 — Combat presentation](docs/02-systems/combat-presentation.md) | Draft | Fixed camera; selective cinematics |
| [02 — Party & classes](docs/02-systems/party-and-classes.md) | Draft | 6 core (3+3) + aux slots |
| [02 — Summons & guests](docs/02-systems/summons-and-guests.md) | Draft | +1 front / +1 back aux |
| [02 — Items & inventory](docs/02-systems/items-and-inventory.md) | Draft | Bags, equipment, shop stock |
| [02 — Progression](docs/02-systems/character-progression.md) | Draft | Skill points, synthesis |
| [02 — Navigator](docs/02-systems/navigator.md) | Draft | Off-formation lead; Protocol + auras |
| [02 — Synchro Protocol](docs/02-systems/synchro-protocol.md) | Draft | Synchro Charge; Navigator Protocols |
| [02 — Story events](docs/02-systems/story-events.md) | Draft | VN presentation layer, triggers, playback |
| [02 — Narrative POV](docs/02-systems/narrative-pov.md) | Accepted | Navigator blank-state, speaker rules |
| [02 — Guided tutorial](docs/02-systems/guided-tutorial.md) | Accepted | Coach layer vs VN; [ADR 029](decisions/029-guided-tutorial.md) |
| [02 — Gathering & fishing](docs/02-systems/gathering-and-fishing.md) | Optional | Dungeon minigames; materials |
| [02 — Autopilot](docs/02-systems/autopilot.md) | Optional | Pathfind to discovered tile on map |
| [02 — Side dungeons](docs/02-systems/side-dungeons.md) | Optional | Hub menu → non-strata grid maps |
| [02 — Terrain biomes](docs/02-systems/terrain-biomes.md) | Draft | Biome assignment for FPV art |
| [02 — Elevation generation](docs/02-systems/elevation-generation.md) | Draft | Procedural height fields (later verticality) |
| [02 — UVS phase & presentation](docs/02-systems/uvs-phase-presentation.md) | Draft | Optional Visual Scripting hooks |

### Content

| Doc | Status | Summary |
|-----|--------|---------|
| [03 — Campaign index](docs/03-content/campaign/README.md) | Active | S1 campaign doc map |
| [03 — Campaign / S1 intro](docs/03-content/campaign/s1-intro.md) | Draft | Three-act intro, flags, entry rules |
| [03 — S1 guided tutorials](docs/03-content/campaign/s1-guided-tutorials.md) | Active | Coach beat table (`tutorialEntryId` rows) |
| [03 — Dungeons & encounters](docs/03-content/dungeons-and-encounters.md) | Draft | Strata, FOE tables; S1 B1F–B3F |
| [03 — Stratum 1 enemy roster](docs/03-content/enemy-roster.md) | Draft | S1 enemy stats/skills, encounter groups ([#2](https://github.com/miramocha/griddungeon-design-docs/issues/2)) |
| [03 — Launch class skills](docs/03-content/class-skills.md) | Locked | 3 skills × 6 classes; deploy + summon script IDs ([#3](https://github.com/miramocha/griddungeon-design-docs/issues/3)) |
| [03 — Story events index](docs/03-content/story-events/README.md) | Active | VN draft folders; game asset sync |
| [03 — S1 story drafts](docs/03-content/story-events/s1/) | Synced | Gate briefing, stalker, Protocol unlock, hub return |

### Dev, tech & plans

| Doc | Status | Summary |
|-----|--------|---------|
| [04 — Tech notes](docs/04-tech-notes.md) | Draft | Module tree, map layer, FOE tick |
| [05 — Class design](docs/05-class-design.md) | Locked | Assemblies, type catalog, folder layout, content IDs |
| [04 — Dev: UI event contract](docs/04-dev/ui-event-contract.md) | Active | Runtime events + command APIs for custom HUD |
| [04 — Dev: Centralized UI services](docs/04-dev/centralized-ui-services.md) | Active | Cross-phase overlays, `ICentralizedUiSurface` |
| [04 — Dev: Shared menu & picker UI](docs/04-dev/shared-menu-picker-ui.md) | Active | Rail menu, item list picker, skill picker |
| [04 — Dev: Custom skill picker UI](docs/04-dev/custom-skill-picker-ui.md) | Active | Replace combat skill modal |
| [04 — Dev: Custom party UI](docs/04-dev/custom-party-ui.md) | Active | Exploration strip / combat roster |
| [04 — Dev: Presentation shell](docs/04-dev/presentation-shell-implementation.md) | Active | `ICommandRailShell` prefab + catalog checklist |
| [04 — Dev: UITK BEM transitions](docs/04-dev/uitk-bem-transition-guide.md) | Active | `UiToolkitTweens`, steady-class registry |
| [04 — Dev: Floor transition authoring](docs/04-dev/authoring-floor-transition-beats.md) | Active | Vignette prefab + Cinemachine workflow |
| [04 — Dev: TWC default notes](docs/04-dev/twc-default-notes.md) | Active | TileWorldCreator adapter notes |
| [04 — Dev: Autopilot pathfinding](docs/04-dev/autopilot-pathfinding.md) | Active | Integrator pathfind rules |
| [04 — Dev: Class naming patterns](docs/04-dev/class-naming-patterns.md) | Active | C# suffix conventions |
| [04 — Dev: Obsidian tags](docs/04-dev/obsidian-tags.md) | Active | Vault tag taxonomy + registry |
| [04 — Dev: Doc format](docs/04-dev/doc-format.md) | Active | Markdown profiles; format audit script |
| [Plan — Core assembly](docs/plans/core-assembly-improvement-plan.md) | Active | Core vs Campaign boundary improvements |

### Reference & archive

| Doc | Status | Summary |
|-----|--------|---------|
| [Refs — README](docs/refs/README.md) | Active | Scratchpad policy (not spec authority) |
| [Refs — Map UI](docs/refs/map-ui.md) | Scratchpad | Other games’ map UI screenshots |
| [Archive — release scope snapshot](docs/archive/mvp1-spec.md) | Archived | Historical; use [release scope](docs/00-release-scope.md) |
| [Archive — S1 floor layouts (draft)](docs/archive/mvp1-s1-floor-layouts-draft.md) | Archived | ASCII layouts until floor lock |

### ADRs (001–043)

| ADR | Status | Summary |
|-----|--------|---------|
| [001 — Grid movement](decisions/001-grid-movement.md) | Accepted | Step lerp, hold-to-repeat, strafe, turn rules |
| [002 — Mapping model](decisions/002-mapping-model.md) | Accepted | Auto-reveal; drawing tools out of scope |
| [003 — FOE step patrol](decisions/003-foe-step-patrol.md) | Accepted | FOEs advance on party steps |
| [004 — Auxiliary slots](decisions/004-auxiliary-slots.md) | Accepted | +1 summon/guest per row |
| [005 — FOE combat patrol](decisions/005-foe-combat-patrol.md) | Deferred | 1 FOE cell / combat round (**optional**) |
| [006 — Team burst bar](decisions/006-union-team-bar.md) | Accepted | Synchro Charge mechanics |
| [007 — Navigator role](decisions/007-navigator-role.md) | Accepted | Off-formation; runs Protocol |
| [008 — Campaign defaults](decisions/008-campaign-defaults.md) | Accepted | FOE respawn, unlimited explore, PC |
| [009 — Input bindings](decisions/009-input-bindings-pc.md) | Accepted | EO-style WS/QE/AD; combat ZXCVB; mouse targets |
| [010 — FOE mid-battle join](decisions/010-chain-foe-battle.md) | Accepted | 1 FOE joins current fight per round |
| [011 — FOE flee retreat](decisions/011-foe-flee-retreat.md) | Accepted | Flee pushes back 1 cell; disabled at wall |
| [012 — Unity 6 stack](decisions/012-unity-6-stack.md) | Accepted | Unity 6, URP, Shader Graph–first |
| [013 — Combat scene rendering](decisions/013-combat-scene-rendering.md) | Accepted | Battle arena backdrop; enemies on slots |
| [014 — Default exploration & map](decisions/014-mvp1-exploration-map.md) | Accepted | Wall reveal, map input, persist, gather stub |
| [015 — Default combat](decisions/015-mvp1-combat.md) | Accepted | Damage, enemy front+back rows (6 max), status subset |
| [016 — Summon control](decisions/016-summon-control-mvp1.md) | Accepted | Player-controlled summons; minimal per-summon kit |
| [017 — Game phase controller](decisions/017-game-phase-controller.md) | Accepted | C# `GamePhaseController`; no UVS at launch |
| [018 — Exploration animation speed](decisions/018-exploration-animation-speed.md) | Accepted | Slow / Normal / Fast / Very Fast lerp presets |
| [019 — Floor verticality](decisions/019-floor-verticality.md) | Accepted | `GridPosition.Level`; jump pads deferred |
| [020 — Team burst naming](decisions/020-team-burst-naming.md) | Accepted | Retire “Union”; use Synchro Protocol |
| [021 — Autopilot (optional)](decisions/021-autopilot-mvp2.md) | Accepted | Pathfind on revealed tiles; no path drawing |
| [022 — Side dungeons (optional)](decisions/022-side-dungeons-mvp3.md) | Accepted | Hub Side expedition; `sd##_F#` save keys |
| [023 — Protocol Deploy](decisions/023-protocol-deploy-sortie-summon.md) | Accepted | `protocol_deploy` spawns aux summon |
| [024 — Protocol Transform](decisions/024-protocol-transform.md) | Accepted | Slot-replaces one core with Navigator transform |
| [025 — Campaign exploration target](decisions/025-campaign-exploration-target.md) | Proposed | Neutral `ExplorationTarget` DTO; S2+ policy |
| [026 — Combat menu focus](decisions/026-combat-menu-focus-navigation.md) | Accepted | Rail focus + Z/X confirm; amends ADR 009 |
| [027 — Combat cinematic Timeline](decisions/027-combat-cinematic-timeline-events.md) | Accepted | `PlayableDirector.stopped` + QTE markers |
| [028 — Story VN events](decisions/028-story-visual-novel-events.md) | Proposed | Modal story playback; [#87](https://github.com/miramocha/griddungeon-game/issues/87) |
| [029 — Guided tutorial](decisions/029-guided-tutorial.md) | Accepted | Coach layer distinct from VN |
| [030 — Story event graph authoring](decisions/030-story-event-graph-authoring.md) | Proposed | Graph Toolkit → story steps (follow-up) |
| [031 — Floor event pin graph](decisions/031-floor-event-pin-condition-graph.md) | Proposed | Flag-gated pins; does not block launch |
| [032 — Floor transition vignette](decisions/032-floor-transition-vignette-mvp1.md) | Accepted | Black + 3D threshold between floors |
| [033 — Hub environment Cinemachine](decisions/033-hub-environment-cinemachine.md) | Accepted | Menu-driven hub camera pans (**later** polish) |
| [034 — Skill points outside combat](decisions/034-skill-point-allocation-outside-combat.md) | Accepted | Class trees in hub / labyrinth when safe |
| [035 — Skill use picker](decisions/035-skill-use-picker.md) | Accepted | Modal picker; default tab **All** |
| [036 — Party inventory model](decisions/036-party-inventory-model.md) | Proposed | Shared bag + per-member equip slots |
| [037 — Layered UITK panels](decisions/037-layered-uitk-panels.md) | Proposed | Split HUD into panel `UIDocument` stack |
| [038 — Centralized UI lifecycle](decisions/038-centralized-ui-presentation-lifecycle.md) | Accepted | `ICentralizedUiSurface`, `IsSettling` |
| [039 — UITK DOTween show/hide](decisions/039-uitk-dotween-show-hide.md) | Accepted | `UiToolkitTweens` + `UiTransitionSession` |
| [040 — Floor exit topology graph](decisions/040-floor-exit-topology-graph.md) | Proposed | `FloorExitLink[]`; GTK compile |
| [041 — Floor Connector wiring](decisions/041-floor-connector-toolkit-wiring.md) | Proposed | `FloorNode` / `ExitEdge` / `HubNode` ([#253](https://github.com/miramocha/griddungeon-game/issues/253)) |
| [042 — Presentation bus](decisions/042-presentation-bus.md) | Accepted | Phase shell DTO bus + rail chrome |
| [043 — TWC FPV presentation](decisions/043-twc-fpv-presentation-layer.md) | Accepted | TileWorldCreator runtime mesh backend |

## Resolved

- **Party:** 6 core (3+3) + aux; Navigator off-formation ([ADR 004](decisions/004-auxiliary-slots.md), [007](decisions/007-navigator-role.md))
- **Mapping:** Auto-reveal; no drawing tools ([ADR 002](decisions/002-mapping-model.md))
- **Movement:** Discrete steps, strafe, ~0.32s lerp (Normal), hold-to-repeat, speed presets ([ADR 001](decisions/001-grid-movement.md), [018](decisions/018-exploration-animation-speed.md))
- **FOE patrol:** Party step-based ([ADR 003](decisions/003-foe-step-patrol.md)); **respawn on hub return** ([ADR 008](decisions/008-campaign-defaults.md))
- **Exploration:** **Unlimited steps** — no TP limit ([ADR 008](decisions/008-campaign-defaults.md))
- **Platform:** **PC** ([ADR 008](decisions/008-campaign-defaults.md))
- **Engine:** **Unity 6 + URP**; shaders **Shader Graph** default, HLSL when needed ([ADR 012](decisions/012-unity-6-stack.md))
- **Death:** GAME OVER → hub save; map kept
- **Synchro Protocol + Navigator:** Team bar; Navigator executes; unlock-only ([006](decisions/006-union-team-bar.md), [007](decisions/007-navigator-role.md), [020](decisions/020-team-burst-naming.md))
- **Multiplayer:** Out of scope
- **Boost/Break:** Out of scope — Synchro Protocol covers team burst ([ADR 008](decisions/008-campaign-defaults.md))
- **Input:** PC defaults ([input bindings](docs/02-systems/input-bindings.md), [ADR 009](decisions/009-input-bindings-pc.md))
- **FOE mid-battle join:** Optional with combat patrol ([ADR 005](decisions/005-foe-combat-patrol.md), [010](decisions/010-chain-foe-battle.md)); **off in required slice**
- **FOE flee:** Escapable; success → **1 cell back**; **disabled** if wall behind ([ADR 011](decisions/011-foe-flee-retreat.md))
- **Skill points:** Spend on class trees in hub or labyrinth when safe — not combat / VN / cutscene ([ADR 034](decisions/034-skill-point-allocation-outside-combat.md))

## Optional (scoped)

- [Gathering & fishing minigames](docs/02-systems/gathering-and-fishing.md) — chop/mine/forage + fish nodes in labyrinth; feeds synthesis
- Hub **synthesis** + gather quests ([release scope](docs/00-release-scope.md))
- [FOE combat patrol](decisions/005-foe-combat-patrol.md) + [mid-battle join](decisions/010-chain-foe-battle.md)
- [Autopilot](docs/02-systems/autopilot.md) — pathfind to discovered tiles; no map drawing ([ADR 021](decisions/021-autopilot-mvp2.md))
- [Side dungeons](docs/02-systems/side-dungeons.md) — hub **Side expedition** → full grid explore + combat outside strata ([ADR 022](decisions/022-side-dungeons-mvp3.md))
- Optional: [cinematic QTE skills](docs/02-systems/combat-presentation.md)

## Open questions

- Required **structure** locked — [release scope](docs/00-release-scope.md), [ADR 014](decisions/014-mvp1-exploration-map.md), [ADR 015](decisions/015-mvp1-combat.md)
- **Map during combat** — show persistent schematic for incoming FOE threat vs `M` toggle only? [mapping § Consider / explore](docs/02-systems/mapping.md#consider--explore--map-during-combat) (ties to [ADR 005](decisions/005-foe-combat-patrol.md))
- **Navigator 3D presence** — bottom-right model in exploration + combat; Protocol Deploy → aux slot, Transform → core slot transition — [navigator § Consider / explore](docs/02-systems/navigator.md#consider--explore--navigator-3d-presence)
- Remaining work: **content** (floors, enemies, skills), **tuning numbers**, optional features

## Naming

Working title: **Grid Dungeon**. Strata/floors use `B1F` style labels like EO.
