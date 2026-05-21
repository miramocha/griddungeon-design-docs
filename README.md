# Grid Dungeon — Design Docs

First-person, grid-based, turn-based labyrinth RPG aligned with **Etrian Odyssey** — mapping as gameplay, FOE threats, guild hub loop, and AGI-driven combat turns.

**Target platform:** PC (keyboard + mouse primary).  
**Engine:** Unity 6 + URP; **Shader Graph–first** shaders ([ADR 012](decisions/012-unity-6-stack.md)).

## How to use these docs

- **Cursor rules** — [`.cursor/rules/`](.cursor/rules/) — Unity clean-code rules (hard-linked from `griddungeon-game`) plus [architecture-design-principles](.cursor/rules/architecture-design-principles.mdc) for class/phase design in this repo
- **Vision & loop** — why the game exists and what one session feels like
- **Systems** — rules engines (movement, mapping, combat, party, hub)
- **Content** — strata, floors, monsters, FOE placement
- **Tech** — Unity 6 / URP implementation constraints
- **Decisions** — ADRs when we lock a design choice
- **Release scope** — [MVP1 & MVP2](docs/00-release-scope.md) · **[MVP1 spec](docs/mvp1-spec.md)** (implementation checklist)

## Release milestones

| Milestone | Focus |
|-----------|--------|
| **MVP1** | Hub loop, explore, FOE, AGI combat, Synchro Protocol, auto-map |
| **MVP2** | Gather/fish minigames, synthesis, FOE combat patrol + mid-battle join, autopilot |

## Document index

| Doc | Status | Summary |
|-----|--------|---------|
| [MVP1 spec](docs/mvp1-spec.md) | Active | MVP1 checklist + locked rules |
| [00 — Release scope](docs/00-release-scope.md) | Draft | MVP1, MVP2, later |
| [00 — Vision](docs/00-vision.md) | Draft | EO-first pillars, inspirations |
| [00 — Game references](docs/00-game-references.md) | Draft | EO + Mary Skelter, etc. — future design reference |
| [01 — Core loop](docs/01-core-loop.md) | Draft | Guild hub ↔ stratum loop |
| [02 — Dungeon navigation](docs/02-dungeon-navigation.md) | Draft | Grid FPV, FOEs on map |
| [02 — Mapping](docs/02-systems/mapping.md) | Draft | Auto-reveal only; no drawing tools |
| [02 — Hub & services](docs/02-systems/hub-and-services.md) | Draft | Explorers Guild, Navigator Office, shop, hospital, save |
| [02 — Combat](docs/02-systems/combat.md) | Draft | AGI turn order, rows |
| [02 — Combat status & buffs](docs/02-systems/combat-status-and-buffs.md) | Draft | Ailments, binds, Boost/Down, ticks |
| [02 — Combat scene](docs/02-systems/combat-scene.md) | Accepted | Battle arena + slots; not in-world FPV |
| [02 — Combat presentation](docs/02-systems/combat-presentation.md) | Draft | Fixed camera; selective cinematics |
| [02 — Party & classes](docs/02-systems/party-and-classes.md) | Draft | 6 core (3+3) + aux slots |
| [02 — Summons & guests](docs/02-systems/summons-and-guests.md) | Draft | +1 front / +1 back aux |
| [02 — Progression](docs/02-systems/character-progression.md) | Draft | Skill points, synthesis |
| [02 — Navigator](docs/02-systems/navigator.md) | Draft | Off-formation lead; Protocol + auras |
| [02 — Synchro Protocol](docs/02-systems/synchro-protocol.md) | Draft | Synchro bar; Navigator Protocols |
| [02 — Input bindings](docs/02-systems/input-bindings.md) | Draft | PC keyboard + mouse defaults |
| [02 — FOE encounters](docs/02-systems/foe-encounters.md) | Accepted | Contact, flee, retreat cell |
| [02 — Game phase](docs/02-systems/game-phase.md) | Accepted | `GamePhaseController`, phase diagrams, Enter/Exit ([ADR 017](decisions/017-game-phase-controller.md)) |
| [05 — Class design MVP1](docs/05-class-design-mvp1.md) | Draft | Assemblies, Core DTOs, class sketches, content IDs |
| [02 — FOE mid-battle join](docs/02-systems/chain-foe-battle.md) | Accepted | 1 FOE joins current fight / round |
| [02 — Gathering & fishing](docs/02-systems/gathering-and-fishing.md) | MVP2 | Dungeon minigames; materials |
| [02 — Autopilot](docs/02-systems/autopilot.md) | MVP2 | Pathfind to discovered tile on map |
| [03 — Dungeons & encounters](docs/03-content/dungeons-and-encounters.md) | Draft | Strata, FOE tables; B1F–B3F MVP1 layouts |
| [03 — Campaign / S1 intro](docs/03-content/campaign/s1-intro.md) | Draft | Three-act intro, flags, entry rules |
| [04 — Tech notes](docs/04-tech-notes.md) | Draft | Map layer, FOE tick |
| [ADR 001 — Grid movement](decisions/001-grid-movement.md) | Accepted | Step lerp, hold-to-repeat, strafe, turn rules |
| [ADR 002 — Mapping model](decisions/002-mapping-model.md) | Accepted | Auto-reveal; drawing tools out of scope |
| [ADR 003 — FOE step patrol](decisions/003-foe-step-patrol.md) | Accepted | FOEs advance on party steps |
| [ADR 004 — Auxiliary slots](decisions/004-auxiliary-slots.md) | Accepted | +1 summon/guest per row |
| [ADR 005 — FOE combat patrol](decisions/005-foe-combat-patrol.md) | Deferred | 1 FOE cell / combat round (**MVP2**) |
| [ADR 006 — Team burst bar](decisions/006-union-team-bar.md) | Accepted | Synchro bar mechanics |
| [ADR 020 — Team burst naming](decisions/020-team-burst-naming.md) | Accepted | Retire “Union”; use Synchro Protocol |
| [ADR 007 — Navigator role](decisions/007-navigator-role.md) | Accepted | Off-formation; runs Protocol |
| [ADR 008 — Campaign defaults](decisions/008-campaign-defaults.md) | Accepted | FOE respawn, unlimited explore, PC |
| [ADR 009 — Input bindings](decisions/009-input-bindings-pc.md) | Accepted | WASD + QE, combat 1–5, mouse targets |
| [ADR 010 — FOE mid-battle join](decisions/010-chain-foe-battle.md) | Accepted | 1 FOE joins current fight per round (with ADR 005) |
| [ADR 011 — FOE flee retreat](decisions/011-foe-flee-retreat.md) | Accepted | Flee pushes back 1 cell; disabled at wall |
| [ADR 012 — Unity 6 stack](decisions/012-unity-6-stack.md) | Accepted | Unity 6, URP, Shader Graph–first |
| [ADR 013 — Combat scene rendering](decisions/013-combat-scene-rendering.md) | Accepted | Battle arena backdrop; enemies on slots |
| [ADR 014 — MVP1 exploration & map](decisions/014-mvp1-exploration-map.md) | Accepted | Wall reveal, map input, persist, gather stub |
| [ADR 015 — MVP1 combat](decisions/015-mvp1-combat.md) | Accepted | Damage, single enemy row, status subset |
| [ADR 016 — Summon control MVP1](decisions/016-summon-control-mvp1.md) | Accepted | MVP1 scripted actions; player control TBD |
| [ADR 017 — Game phase controller](decisions/017-game-phase-controller.md) | Accepted | C# `GamePhaseController` + three `IPhaseController`s; no UVS MVP1 |
| [ADR 018 — Exploration animation speed](decisions/018-exploration-animation-speed.md) | Accepted | Slow / Normal / Fast / Very Fast lerp presets |
| [ADR 021 — Autopilot MVP2](decisions/021-autopilot-mvp2.md) | Accepted | Pathfind on revealed tiles; no path drawing |

## Resolved

- **Party:** 6 core (3+3) + aux; Navigator off-formation ([ADR 004](decisions/004-auxiliary-slots.md), [007](decisions/007-navigator-role.md))
- **Mapping:** Auto-reveal; no drawing tools ([ADR 002](decisions/002-mapping-model.md))
- **Movement:** Discrete steps, strafe, ~0.28s lerp (Normal), hold-to-repeat, speed presets ([ADR 001](decisions/001-grid-movement.md), [018](decisions/018-exploration-animation-speed.md))
- **FOE patrol:** Party step-based ([ADR 003](decisions/003-foe-step-patrol.md)); **respawn on hub return** ([ADR 008](decisions/008-campaign-defaults.md))
- **Exploration:** **Unlimited steps** — no TP limit ([ADR 008](decisions/008-campaign-defaults.md))
- **Platform:** **PC** ([ADR 008](decisions/008-campaign-defaults.md))
- **Engine:** **Unity 6 + URP**; shaders **Shader Graph** default, HLSL when needed ([ADR 012](decisions/012-unity-6-stack.md))
- **Death:** GAME OVER → hub save; map kept
- **Synchro Protocol + Navigator:** Team bar; Navigator executes; unlock-only ([006](decisions/006-union-team-bar.md), [007](decisions/007-navigator-role.md), [020](decisions/020-team-burst-naming.md))
- **Multiplayer:** Out of scope
- **Boost/Break:** Out of scope — Synchro Protocol covers team burst ([ADR 008](decisions/008-campaign-defaults.md))
- **Input:** PC defaults ([input bindings](docs/02-systems/input-bindings.md), [ADR 009](decisions/009-input-bindings-pc.md))
- **FOE mid-battle join:** MVP2 with combat patrol ([ADR 005](decisions/005-foe-combat-patrol.md), [010](decisions/010-chain-foe-battle.md)); **off in MVP1**
- **FOE flee:** Escapable; success → **1 cell back**; **disabled** if wall behind ([ADR 011](decisions/011-foe-flee-retreat.md))

## MVP2 (scoped)

- [Gathering & fishing minigames](docs/02-systems/gathering-and-fishing.md) — chop/mine/forage + fish nodes in labyrinth; feeds synthesis
- Hub **synthesis** + gather quests ([release scope](docs/00-release-scope.md))
- [FOE combat patrol](decisions/005-foe-combat-patrol.md) + [mid-battle join](decisions/010-chain-foe-battle.md)
- [Autopilot](docs/02-systems/autopilot.md) — pathfind to discovered tiles; no map drawing ([ADR 021](decisions/021-autopilot-mvp2.md))
- Optional: [cinematic QTE skills](docs/02-systems/combat-presentation.md)

## Open questions

- MVP1 **structure** locked — [mvp1-spec](docs/mvp1-spec.md), [ADR 014](decisions/014-mvp1-exploration-map.md), [ADR 015](decisions/015-mvp1-combat.md)
- **Map during combat** — show persistent schematic for incoming FOE threat vs `M` toggle only? [mapping § Consider / explore](docs/02-systems/mapping.md#consider--explore--map-during-combat) (ties to [ADR 005](decisions/005-foe-combat-patrol.md))
- Remaining work: **content** (floors, enemies, skills), **tuning numbers**, MVP2 features

## Naming

Working title: **Grid Dungeon**. Strata/floors use `B1F` style labels like EO.
