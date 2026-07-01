# ADR 043 — TileWorldCreator as FPV presentation layer

**Status:** Accepted  
**Date:** 2026-07-01  
**Epic:** [griddungeon-game #344](https://github.com/miramocha/griddungeon-game/issues/344)  
**Docs:** [floor-art-fpv — TileWorldCreator runtime path](../docs/02-systems/floor-art-fpv.md#tileworldcreator-runtime-path), [twc-default-notes](../docs/04-dev/twc-default-notes.md)

## Context

Grid Dungeon renders exploration corridors in **3D FPV** (walls, walkable ground, elevation terraces) while gameplay authority lives in `ExplorationFloor` + Core ([ADR 002](002-mapping-model.md)). The built-in path uses prefab populate and blocky terrain meshes. [TileWorldCreator v4](https://giantgrey.gitbook.io/tileworldcreator-v4-documentation/api) can generate equivalent meshes at runtime from blueprint cell masks.

TWC also ships procedural blueprint generators (cellular automata, BSP, maze). Using those as layout source would duplicate Core maze tools and drop doors, FOE, chests, and elevation data.

## Decision

1. **`ExplorationFloor` is the only gameplay map authority** — walkability, doors, elevation steps, encounters, exits. TWC receives a **one-way feed** from floor data via adapters (`FloorArtTwcWalkableMaskBuilder`, `FloorArtTwcElevationTranslator`).
2. **TWC is presentation only** — no movement, collision, or encounter logic on TWC tile colliders. Party Y remains `FloorArtGrid.TryGetElevationY` / `DungeonExplorer`.
3. **Optional plugin assembly** — `GridDungeon.FloorArt.TileWorldCreator` references vendor TWC; `GridDungeon.Runtime` uses `IFloorArtMeshBackend` only so clones without the asset compile with `MeshBackend = Default`.
4. **Per-stratum backend** — `FloorArtMeshBackendKind { Default, TileWorldCreator }` on `FloorArtStratumDefaults`. `Default` stays supported for installs without TWC; not deprecated.
5. **UITK minimap unchanged** — TWC has no HUD map; [map cell art](../docs/02-systems/map-cell-art.md) stays USS + reveal state.

## Rejected / out of scope (epic #344)

| Option | Why |
|--------|-----|
| TWC generators → write `ExplorationFloor` | Loses markers, elevation, FOE; duplicates Core maze gen |
| TWC colliders for grid movement | Drift from logic grid; breaks elevation / doors |
| Replacing UITK minimap with TWC | No minimap feature in TWC; custom work not in epic |
| Removing `MeshBackend = Default` in epic | Non-TWC installs must keep working; retirement is optional ([#370](https://github.com/miramocha/griddungeon-game/issues/370)) |

## Consequences

- Floor Editor layout tabs unchanged for TWC rollout; designers still paint `ExplorationFloor` assets.
- Runtime builds TWC configuration clone per floor load; committed TWC assets are templates, not layout authority.
- Elevation uses runtime-provisioned `Level_sN` layers ([#347](https://github.com/miramocha/griddungeon-game/issues/347)); `cellElevationSteps` schema unchanged.
- Built-in populate/terrain path remains until optional [#370](https://github.com/miramocha/griddungeon-game/issues/370) after full strata rollout.

## Implementation references

| Phase | Issue | Delivered |
|-------|-------|-----------|
| Spike | [#345](https://github.com/miramocha/griddungeon-game/issues/345) | B1F default path, [twc-default-notes](../docs/04-dev/twc-default-notes.md) |
| Adapter | [#346](https://github.com/miramocha/griddungeon-game/issues/346) | `IFloorArtMeshBackend`, plugin asmdef |
| Elevation | [#347](https://github.com/miramocha/griddungeon-game/issues/347) | `Level_sN` stack, terrace boost |
