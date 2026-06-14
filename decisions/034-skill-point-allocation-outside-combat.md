# ADR 034 — Skill point allocation outside combat

**Status:** Accepted (required slice)  
**Date:** 2026-05-30  
**Supersedes:** “Hub only” skill spending called out in early launch docs and `GuildService`-only wiring.

## Context

Etrian-style progression grants **skill points on level-up** for **core** party members. Early Grid Dungeon docs said points are spent **at hub only** (Explorers Guild), which forces a surface trip after every level-up found in the labyrinth.

Players should be able to **react to a level-up** (or spend banked points) **without returning to hub**, as long as they are not in a mode that already blocks menu control.

**Not in scope**

- **Navigator** kits — unlock + assign at Navigator Office; no skill points ([ADR 007](007-navigator-role.md)).
- **Summon combat kits** — fixed `skillIds` on `SummonDefinition`, not guild trees ([ADR 016](016-summon-control-mvp1.md)).
- **Respec** — still expensive NPC or none at launch.
- **Mid-combat level-up UI** — XP applies after battle; spending waits until a **safe** screen.

## Decision

1. **Class skill trees** are editable whenever the player is **not** in:
   - **`GamePhase.Combat`** (command planning, AGI playback, battle-end flow until macro phase returns to Exploration or Hub)
   - **Active story / VN** — `StoryEventRunner` ([ADR 028](028-story-visual-novel-events.md))
   - **Cutscene / presentation lock** — floor-transition vignette ([ADR 032](032-floor-transition-vignette-mvp1.md)), blocking guided-tutorial coach ([ADR 029](029-guided-tutorial.md)), or any full-screen sequence that disables hub/exploration menus

2. **Allowed macro phases:** **Hub** and **Exploration** (when no blocker in §1).

3. **Same rules and data** in every entry point — one implementation path for `AllocateSkillPoint(characterId, skillId)`:
   - Hub — Explorers Guild
   - Labyrinth — `Tab` party menu and exploration pause **Skills** ([input bindings](../docs/02-systems/input-bindings.md))

4. **Gate in one place** — UI and services consult `GamePhase` + story runner + presentation gates; **not** “caller must be `HubController`.”

5. **Level-up during combat** — grant `+1` skill point in post-battle rewards; player may spend on the **next** safe Hub or Exploration screen without a hub return.

## Rejected at launch

| Option | Why |
|--------|-----|
| Hub-only spending | Extra friction; EO players expect to manage builds between fights on the floor |
| Fourth macro `GamePhase` (e.g. `SkillTree`) | Trees are a **modal overlay** on Hub/Exploration; same pattern as map/pause ([ADR 017](017-game-phase-controller.md)) |
| Spend points during combat | Breaks turn flow; conflicts with command planning and presentation locks |
| Spend during VN / cutscene | Competes with narrative and coach UX ([ADR 028](028-story-visual-novel-events.md), [ADR 029](029-guided-tutorial.md)) |
| Separate labyrinth skill tree data | One `SkillDefinition` table; UI location only differs |

## Consequences

- **Docs:** [character progression § Skill points](../docs/02-systems/character-progression.md#skill-points), [game phase § Skill point allocation](../docs/02-systems/game-phase.md#skill-point-allocation-ui-gate)
- **`GuildService.AllocateSkillPoint`** — rename or wrap is optional; behavior must be callable from exploration party UI with shared validation
- **`HubServices.TryAllocateSkillPoint`** (game repo) — extend or extract to `PartyProgressionService` (or equivalent) used by Guild **and** exploration menus
- **Exploration UI** — party menu / pause **Skills** screen (may not exist yet); gate on ADR §1 blockers
- **Save:** `AllocatedSkillPoints` / `AllocatedSkillIds` unchanged — allocation timing only
- **launch trees:** still flat 3 nodes per class ([class-skills](../docs/03-content/class-skills.md))

## Implementation (game repo)

Track when building labyrinth skill UI:

- Shared `CanAllocateSkillPoints()` (phase + story + presentation)
- Exploration pause / party menu routes to same tree presenter as Guild
- Disable **Skills** entry when `CanAllocateSkillPoints()` is false

No mandatory issue number at accept time — file against hub/exploration UI or progression epic when scheduled.

## Related

- [Party & classes](../docs/02-systems/party-and-classes.md)
- [Hub & services](../docs/02-systems/hub-and-services.md)
- [release scope](../docs/00-release-scope.md)
- [ADR 007 — Navigator role](007-navigator-role.md)
- [ADR 017 — Game phase controller](017-game-phase-controller.md)
- [ADR 028 — Story visual novel events](028-story-visual-novel-events.md)
- [ADR 029 — Guided tutorial](029-guided-tutorial.md)
