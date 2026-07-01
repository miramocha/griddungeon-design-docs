---
tags:
  - path/docs/02-systems
  - type/system
  - scope/later
  - status/draft
  - domain/exploration
---
# Terrain biomes (procedural splat painting)

**Scope:** [Later](../00-release-scope.md#later)

**Implementation:** `GridDungeon.Core.FloorArt.TerrainBiomePaintCalculator`, `GridDungeon.Runtime.Exploration.FloorArt.FloorArtBlockyTerrainBuilder`  
**Related:** [Elevation generation](elevation-generation.md), [Floor Editor](floor-editor.md), [Red Blob — biomes from noise](https://www.redblobgames.com/maps/terrain-from-noise/#biomes)

## Overview

When **blocky terrain** is baked (runtime or FPV editor), alphamap splat weights can be painted procedurally from:

| Input | Source |
|-------|--------|
| **Elevation** | Floor `cellElevationSteps`, normalized by min/max on that floor |
| **Moisture** | Seeded 2D value noise (per-floor seed XOR stratum biome salt) |
| **Diagram** | `FloorArtStratumDefaults.m_biomeDiagram` — 2D lookup of terrain layer indices |
| **Layers** | `FloorArtStratumDefaults.m_terrainLayers` — Unity `TerrainLayer` assets |

Uses **default Unity terrain** splatting (URP Terrain Lit or built-in). Assign that material on stratum **Terrain material**.

## Diagram axes

Match Red Blob convention on `TerrainBiomeDiagramData`:

- **X (width)** — elevation low → high (`0` = min step, `1` = max step on floor)
- **Y (height)** — moisture dry → wet (`0` = dry, `1` = wet from noise)

Each diagram cell stores an **index** into `m_terrainLayers` (not a texture name).

**Soft blend:** bilinear interpolation across four diagram corners merges layer weights per alphamap texel.

## Stratum fields (`FloorArtStratumDefaults`)

| Field | Role |
|-------|------|
| `m_enableProceduralTerrainBiomes` | Master toggle (off until layers + diagram are authored) |
| `m_biomeDiagram` | Width, height, `LayerIndices[]` (row-major) |
| `m_moistureNoiseFrequency` | Moisture noise scale (default `4`) |
| `m_biomeSeedSalt` | Mixed with floor seed: `moistureSeed = floorSeed ^ biomeSeedSalt` |
| `m_wallTerrainLayerIndex` | Splat layer for non-walkable (`#`) cells |
| `m_terrainLayers` | Layer assets referenced by diagram indices |
| `m_terrainMaterial` | Unity terrain material (must sample splat maps) |

Edit via **Floor Editor → Open Template** (opens stratum defaults for the floor’s location id).

## Seeds

- **Runtime:** `FloorArtBuildContext.FloorSeed` (from `FloorArtCatalog` resolve per floor key).
- **Editor bake:** `FloorArtTerrainSeedEditor.ResolveFloorSeed` (catalog → stratum default → stable hash).
- **Moisture channel** is always derived from floor seed + biome salt so it stays stable per floor but independent of wall/floor populate seeds.

## Walls

Non-walkable cells (`ExplorationFloorLayout.IsWalkable` false) receive **100%** weight on `m_wallTerrainLayerIndex`; diagram is not sampled.

## Pipeline

1. `ConfigureTerrainData` — heightmap size
2. `EnsureTerrainSplatLayers` — assign layers + `PaintAlphamaps` (or flat layer 0 when biomes disabled)
3. `BuildHeights` / `ApplyHeights`
4. `ApplyTerrainMaterial` from stratum

Alphamap resolution: `max(16, max(gridWidth, gridHeight))` when biomes enabled; `16` for flat fallback.

## Authoring checklist

1. Open stratum defaults (**Open Template** in Floor Editor).
2. Assign **URP Terrain Lit** (or built-in terrain) to **Terrain material**.
3. Add 2–8 **Terrain layer** assets to `m_terrainLayers`.
4. Fill **biome diagram** (`8×8` default): layer indices per elevation/moisture cell.
5. Enable **Procedural terrain biomes**.
6. Floor with **Use blocky terrain** + varied elevation → FPV Preview or Play Mode F2.

## Tests

- `Tests → Map → TerrainBiomePaintCalculatorTests`
- `Tests → Exploration → FloorArtBlockyTerrainBuilderTests` (`PaintAlphamaps_WhenBiomesEnabled_ProducesNonUniformWeights`)

## Out of scope (v1)

- Per-floor stored biome overrides
- Floor Editor biome heatmap
- Procedural `TerrainLayer` asset creation at runtime
- Custom `TerrainGround.shadergraph` splat path

---

## Related docs

- [Elevation generation](elevation-generation.md)
- [Floor Editor](floor-editor.md)
- [Floor art FPV](floor-art-fpv.md)
- [ADR 019 — Floor verticality](../../decisions/019-floor-verticality.md)
