# TWC default notes ([#345](https://github.com/miramocha/griddungeon-game/issues/345))

Phase 0 default path: `ExplorationFloor` walkables → TWC `AddCellsToLayer` → `GenerateCompleteMap`.

**Authority:** [floor art FPV — TileWorldCreator runtime path](../02-systems/floor-art-fpv.md#tileworldcreator-runtime-path-planned--epic-344) · **Issue:** [griddungeon-game #345](https://github.com/miramocha/griddungeon-game/issues/345)

## Setup (once after clone)

1. Import **TileWorldCreator 4** to `Assets/TileWorldCreator/` (local Asset Store install — see [game third-party-assets.md](https://github.com/miramocha/griddungeon-game/blob/main/docs/third-party-assets.md)).
2. Unity menu: **GridDungeon → Floor Art → TWC Default → Setup B1F (Configuration + Template)**.
3. Play Mode **F2** (Exploration) on Dev Bootstrap — loads **s1_B1F** with TWC meshes.

## Locked default parameters

| Parameter                 | Value                                                                         | Grid Dungeon source                                                                                                     |
| ------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Grid size                 | **21×21**                                                                     | `ExplorationGridMetrics.FloorGridCells` / `s1_B1F` asset (design docs say 20×20 playable; launch floors are 21 indices) |
| Cell size                 | **10** world units (logic)                                                    | `ExplorationGridMetrics.WorldUnitsPerCell`                                                                              |
| TWC sub-grid              | **2×2** default — **5** u TWC `cellSize`, **42×42** blueprint on 21×21 floors | `FloorArtTwcSubGrid.DefaultCellsPerLogicCell` / **TwcFloorArt → TWC Cells Per Logic Cell**                              |
| Axis map                  | `cell.X` → world **X**, `cell.Y` → world **Z** (north **+Z**)                 | `ExplorationWorldSpace`, `FloorArtGrid.GridToWorld`                                                                     |
| Blueprint `WalkableFloor` | walkable logic cells                                                          | **Floor** build layer — dual grid + `GrassTilesPreset` (fill tiles in corridors)                                        |
| Blueprint `SolidMass`     | impassable cells (wall-block populate rules)                                  | **Walls** build layer — dual grid + `BaseBlockPresetGreen` (edge/corner at mass boundary)                               |
| Default floor             | `s1_B1F` only                                                                 | `FloorArtTwcFloorHost` on template skips built-in walls/floor/blocky; chests/doors still populate                       |

## Dual grid floor + walls (default)

| Layer     | Blueprint input           | Build output                                                                         |
| --------- | ------------------------- | ------------------------------------------------------------------------------------ |
| **Floor** | `BuildWalkableFloorCells` | Grass dual-grid **fill** — builds **first**, mesh colliders for wall stacking        |
| **Walls** | `BuildSolidMassCells`     | BaseBlock dual-grid **edges** — `layerYOffset = -twcCellSize/2` for center-pivot tiles (no `placeOnTop`) |

Center-pivot TWC tiles: floor and walls both `layerYOffset = -twcCellSize/2` (2.5 u when sub-grid cellSize is 5). Fixed offsets avoid door/chest raycast misalignment from `placeOnTop`.

**Runtime:** `FloorArtTwcTileLayerYOffset` sets floor `layerYOffset = -maxY × twcCellSize`. Walls use the same `-twcCellSize/2` when the edge mesh is center-pivot (`minY ≤ 0`); asymmetric edges (`minY > 0`) use `-minY × twcCellSize`.

## Sub-grid resolution (default 2×2)

Logic grid stays **10 u** per cell. Default: **TWC Cells Per Logic Cell = 2** (`FloorArtTwcSubGrid.DefaultCellsPerLogicCell`).

|                              | 1:1 (opt-out)               | 2×2 sub-grid (default)        |
| ---------------------------- | --------------------------- | ----------------------------- |
| TWC `cellSize`               | 10                          | **5**                         |
| Blueprint size (21×21 floor) | 21×21                       | **42×42**                     |
| Paint                        | one TWC cell per logic cell | four TWC cells per logic cell |
| Cliff footprint              | full 10 u tiles             | finer ~5 u tiles              |

Build log includes `subGrid=2`, `config cellSize=5`, `grid 42x42`. Set **TWC Cells Per Logic Cell** to **1** only to compare legacy 1:1. ~4× blueprint cells vs 1:1 → longer `GenerateCompleteMap` time.

Floor blueprint includes **chest pads** (`HasChest`, non-walkable) — same cells wall-block populate skips for props.

Legacy single-layer setup (`Walkable` blueprint → `FloorTiles` build) is disabled when you re-run **Setup B1F**.

## Tileset swaps (Play Mode)

Use **Tileset Profile** assets to try different TWC floor + wall presets without editing code.

1. **GridDungeon → Floor Art → TWC Default → Create Default Tileset Profiles** (or re-run **Setup B1F** — creates profiles and wires the default).
2. Profiles live under `Assets/Content/FloorArt/TWC/TilesetProfiles/`:
    - `GrassFloor_BaseBlockGreenWalls` — default grass + green walls
    - `SandFloor_BaseBlockBlueWalls` — sand corridors + blue block walls (when TWC sand/blue presets are installed)
    - `GrassFloor_BaseBlockBlueWalls` — grass floor + blue walls
    - `CliffA_Floor_CliffA_Walls` — cliff dual-grid floor + walls (TWC `CliffTilesPreset_A`)
    - `CliffA_Floor_CliffB_Walls` — cliff A floor + cliff B walls (mixed rock tone)
3. Open `Assets/Content/FloorArt/Templates/s1_FloorArtTemplate.prefab` → **TwcFloorArt** → assign **Tileset Profile** or **Floor Tile Preset** + **Wall Tile Preset** (direct refs are more reliable at runtime).
4. Play **F2** — `FloorArtTwcFloorHost` applies the profile at build time; console log includes `tileset=…`.

**Quick cliff preview:** **GridDungeon → Floor Art → TWC Default → Apply Cliff Tileset to B1F Default** (creates profiles if needed and wires the template host).

Create custom pairs via **Assets → Create → Grid Dungeon → Floor Art → TWC Tileset Profile** (both presets should be **dual grid**).

**Manual alternative:** edit **Floor** / **Walls** build layers on `GridDungeonTwcConfiguration.asset` directly, or leave **Tileset Profile** empty to use whatever is saved on the configuration.

## Tile scale offset (default)

TWC dual-grid meshes (especially Cliff) can read larger than built-in **10 u** logic cells even when TWC `cellSize` is correct (default **5 u** with 2×2 sub-grid). Tune without editing the TWC configuration asset:

1. Open `s1_FloorArtTemplate` → **TwcFloorArt** → **Tile Scale Offset** (default `(1, 1, 1)`).
2. Try **X/Z ≈ 0.92–0.98**, keep **Y = 1** unless height also needs trimming.
3. Play **F2** — build log includes `tileScale=(x, y, z)` next to `tileset=…`.

Applied at runtime to both **Floor** and **Walls** build layers (`scaleTileToCellSize` stays on). Does **not** change logic grid or `cellSize`.

## Dual grid vs standard grid

|                      | Dual grid (default)                                                                                             | Standard grid                                           |
| -------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Tile count           | 5 prefab roles (edge, corner, inverted corner, fill, double interior)                                           | Up to 14 autotile variants                              |
| Input mask           | **Impassable mass** on blueprint layer (BaseBlock preset)                                                       | Same                                                    |
| Corridors            | Unpainted void — edge tiles form walls at mass boundary                                                         | Same                                                    |
| Fit for Grid Dungeon | **Yes** — matches legacy wall-block populate cells; do **not** paint walkable (fills corridor with solid cubes) | Heavier art set; defer unless art needs NRMGRD variants |

## Elevation bridge (#347)

- **Authority:** `ExplorationFloor.cellElevationSteps` + `elevationStepUnits` → party/camera Y via `FloorArtGrid.TryGetElevationY` (unchanged).
- **FPV mesh:** `FloorArtTwcElevationTranslator` buckets walkable/solid blueprint cells by **elevation step layer**. Walkable terraces paint **solid foundation** on layers `0 .. surfaceStep-1` then walkable on `surfaceStep`. Layout `#` walls paint **solid on every layer** `baseStep .. baseStep + terrainWallHeight` (one TWC block per layer — no single boosted cliff bucket). **TWC blueprint Y:** `layerStep × TwcElevationBlockStepUnits` (0.5 u). Party/camera Y still uses floor `elevationStepUnits`. `FloorArtTwcElevationLayerProvisioner` orders **floor build layers before walls** per step (sibling index — draw order only).
- **Flat floors** (single step `0`): canonical `WalkableFloor` / `SolidMass` layers — same as Phase 0.
- **No per-floor TWC config authoring** — elevation is not stored on `GridDungeonTwcConfiguration.asset`.
- **Floor key gate:** empty `m_enabledFloorKeys` or legacy single `s1_B1F` entry → TWC build runs for all floors on the stratum template.

## Build time

`FloorArtTwcFloorHost` logs wall-clock ms after `GenerateCompleteMap` on each load, e.g.:

```text
[FloorArtTwc] Built 's1_B1F' — N walkable cells, XX.X ms ...
```

Record Play Mode numbers here after verification:

| Floor  | Walkable cells | Blueprint + build (ms) | Notes            |
| ------ | -------------- | ---------------------- | ---------------- |
| s1_B1F | (from log)     | (from log)             | F2 Dev Bootstrap |

## Alignment check

On build, console logs one sample walkable cell comparing:

- `ExplorationWorldSpace.CellCornerToWorld`
- `FloorArtGrid.GridToWorld`
- TWC `configuration.cellSize` (expect **5** with default sub-grid, **10** if **TWC Cells Per Logic Cell** is 1)

Walk party along B1F corridor — FPV mesh corners should match logic grid / minimap.

## Troubleshooting

| Symptom                                        | Likely cause                                                                 | Fix                                                                                                   |
| ---------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Only chests/doors, no corridor meshes          | TWC `cellSize` wrong (tiny map at origin)                                    | Re-run Setup B1F or play once — `ApplyConfigurationDefaults` sets sub-grid `cellSize` at build        |
| Hallways shifted / walls overlap wrong cells   | Dual-grid spans `[x±0.5]` in TWC coords — needs **+halfCell** manager offset | `AlignManagerWithGrid` adds `(cellSize/2, 0, cellSize/2)` to `FloorArtGrid.Origin`                    |
| Walls fill corridor / on walkable cells        | Solid-mass mask on walkable blueprint                                        | Floor uses `WalkableFloor` + `BuildWalkableFloorCells`; walls use `SolidMass` + `BuildSolidMassCells` |
| Only floating walls, no ground                 | Single build layer on solid mass only                                        | Re-run **Setup B1F** for `WalkableFloor` + `Floor` build layer                                        |
| Floor renders above walls                      | Build layer order / hierarchy                                                | Floor build runs first; host moves floor layer below walls                                            |
| Floor top at mid-wall height                   | Center-pivot cube tiles at y=0                                               | Floor and walls `layerYOffset = -twcCellSize/2`                                                        |
| Hole in floor at chest                         | Chest cells are not walkable                                                 | `BuildWalkableFloorCells` includes `HasChest` pads                                                    |
| Door-adjacent walls raised                     | `placeOnTop` raycast hits door/floor colliders                               | Fixed wall `layerYOffset` — `placeOnTop` off                                                          |
| `FloorArtGrid or ExplorationFloor not bound`   | TWC build before floor bind                                                  | Fixed: `FloorArtRuntimeBuilder` calls `TryBuildFromBoundFloor` after populate                         |
| `Layer not found: WalkableFloor` / `SolidMass` | Legacy single-layer config                                                   | Re-run **Setup B1F** menu                                                                             |

## Code map

| Type                             | Role                                                                                            |
| -------------------------------- | ----------------------------------------------------------------------------------------------- |
| `FloorArtTwcSubGrid`             | Cells-per-logic-cell math + clamp (1 or 2)                                                      |
| `FloorArtTwcWalkableMaskBuilder` | `ExplorationFloor` → `HashSet<Vector2>` (+ `ExpandToTwcBlueprint`)                              |
| `FloorArtTwcElevationTranslator` | Per-step walkable/solid buckets from `cellElevationSteps` (#347)                               |
| `FloorArtTwcElevationLayerProvisioner` | Runtime clone: per-step blueprint/build layers + Y offsets (#347)                            |
| `FloorArtTwcFloorHost`           | Runtime build + timing log (clones Configuration at play — does not mutate the committed asset)   |
| `FloorArtTwcTilesetProfile`      | Floor + wall preset pair for tileset swaps                                                      |
| `FloorArtTwcDefaultBootstrap`    | Editor: config asset + template **TwcFloorArt** host                                            |

**Committed `GridDungeonTwcConfiguration.asset`:** default bootstrap output (~large YAML). Regenerate via **Setup B1F** after TWC import; Play Mode uses a runtime clone so the asset stays clean.

**Assembly:** `GridDungeon.FloorArt.TileWorldCreator` uses `autoReferenced: false` — TWC is optional; only explicit asmdef refs (tests, prefab host) pull it in.

Follow-up: [#346](https://github.com/miramocha/griddungeon-game/issues/346) `IFloorArtMeshBackend`, [#347](https://github.com/miramocha/griddungeon-game/issues/347) elevation bridge.
