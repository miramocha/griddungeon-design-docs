# Grid Dungeon — Design Docs

First-person, grid-based, turn-based labyrinth RPG aligned with **Etrian Odyssey** — mapping as gameplay, FOE threats, guild hub loop, and AGI-driven combat turns.

## How to use these docs

- **Vision & loop** — why the game exists and what one session feels like
- **Systems** — rules engines (movement, mapping, combat, party, hub)
- **Content** — strata, floors, monsters, FOE placement
- **Tech** — Unity/URP implementation constraints
- **Decisions** — ADRs when we lock a design choice

## Document index

| Doc | Status | Summary |
|-----|--------|---------|
| [00 — Vision](docs/00-vision.md) | Draft | EO-first pillars, inspirations |
| [01 — Core loop](docs/01-core-loop.md) | Draft | Guild hub ↔ stratum loop |
| [02 — Dungeon navigation](docs/02-dungeon-navigation.md) | Draft | Grid FPV, FOEs on map |
| [02 — Mapping](docs/02-systems/mapping.md) | Draft | Auto-reveal only; no drawing tools |
| [02 — Hub & services](docs/02-systems/hub-and-services.md) | Draft | Guild, shop, hospital, save |
| [02 — Combat](docs/02-systems/combat.md) | Draft | AGI turn order, rows |
| [02 — Combat presentation](docs/02-systems/combat-presentation.md) | Draft | Fixed camera; selective cinematics |
| [02 — Party & classes](docs/02-systems/party-and-classes.md) | Draft | 6 core (3+3) + aux slots |
| [02 — Summons & guests](docs/02-systems/summons-and-guests.md) | Draft | +1 front / +1 back aux |
| [02 — Progression](docs/02-systems/character-progression.md) | Draft | Skill points, synthesis |
| [03 — Dungeons & encounters](docs/03-content/dungeons-and-encounters.md) | Draft | Strata, FOE tables |
| [04 — Tech notes](docs/04-tech-notes.md) | Draft | Map layer, FOE tick |
| [ADR 001 — Grid movement](decisions/001-grid-movement.md) | Proposed | Discrete step lerp |
| [ADR 002 — Mapping model](decisions/002-mapping-model.md) | Accepted | Auto-reveal; drawing tools out of scope |
| [ADR 003 — FOE step patrol](decisions/003-foe-step-patrol.md) | Accepted | FOEs advance on party steps |
| [ADR 004 — Auxiliary slots](decisions/004-auxiliary-slots.md) | Accepted | +1 summon/guest per row |
| [ADR 005 — FOE combat patrol](decisions/005-foe-combat-patrol.md) | Deferred | 1 FOE cell / combat round (optional) |

## Resolved (EO defaults)

- **Party size:** 6 core (3+3) + **1 aux front / 1 aux back** (summon or guest)
- **Mapping:** Fully auto-reveal on explore; **no drawing tools** ([ADR 002](decisions/002-mapping-model.md))
- **Death:** GAME OVER → load last **hub save**; **map kept**
- **FOEs:** Core content; patrol on **party steps** ([ADR 003](decisions/003-foe-step-patrol.md)); stationary FOEs = path length 1
- **Multiplayer:** Out of scope — single-player only ([00 — Vision](docs/00-vision.md))
- **Spell presentation:** Most skills = fixed battle camera; some = cinematic ([combat presentation](docs/02-systems/combat-presentation.md))

## Optional later

- [FOE combat patrol](decisions/005-foe-combat-patrol.md) — FOEs move 1 grid per combat round while party fights; no mid-battle join by default

## Open questions

- [ ] Input: keyboard + gamepad; map pan/zoom bindings?
- [ ] Chain FOE battle if FOE reaches party cell when combat patrol ends?
- [ ] Include **Boost/Break**-style systems (EO2+)? → defer, not MVP
- [ ] **TP/limits** on exploration (EO2+) or unlimited steps?
- [ ] Target platform(s)?

## Naming

Working title: **Grid Dungeon**. Strata/floors use `B1F` style labels like EO.
