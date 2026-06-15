# Campaign flow (content)

Narrative progression, tutorials, and one-time gates � **not** floor grids or encounter tables.

| Doc | Scope |
|-----|--------|
| [s1-intro.md](s1-intro.md) | Stratum 1 at launch � three-act intro, save flags, entry rules |
| [s1-guided-tutorials.md](s1-guided-tutorials.md) | S1 guided hints � Act 1 movement, hub, B2F Protocol coach |
| [../dungeons-and-encounters.md](../dungeons-and-encounters.md) | Floor layouts, FOE placement, random tables (authority for grids) |
| [../enemy-roster.md](../enemy-roster.md) | Enemy stats, skills, encounter group compositions |

**Story scenes (VN):** [story-events.md](../../02-systems/story-events.md) � [ADR 028](../../decisions/028-story-visual-novel-events.md) � [#87](https://github.com/miramocha/griddungeon-game/issues/87)

**Guided coaching (HUD):** [guided-tutorial.md](../../02-systems/guided-tutorial.md) � [ADR 029](../../decisions/029-guided-tutorial.md) � [#88](https://github.com/miramocha/griddungeon-game/issues/88) � distinct from VN; S1 beat table in [s1-guided-tutorials.md](s1-guided-tutorials.md).

**Launch S1:** four story events � B1F **Event cell** before first hub; B2F Event before tutorial fight; mid-combat unlock; hub outro ([story-events index](../story-events/README.md)).

**Later:** more hub / exploration tile scripts and one-off fights. Game assets stay on existing types (`ExplorationFloor`, `EncounterGroup`, save flags) � see [05 � Class design](../../05-class-design.md#content-definitions-runtime-scriptableobjects).
