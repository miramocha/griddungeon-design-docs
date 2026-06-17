# Elevation generation — algorithm

**Implementation:** `GridDungeon.Core.FloorArt.CellElevationGenerator`  
**Related:** [Floor Editor](floor-editor.md) (authoring UI)

## Problem

Given a 2D grid with a walkable mask, produce an `int[]` of **elevation steps** — one integer per cell. Walkable cells receive steps in `[MinStep, MaxStep]`. Non-walkable cells get a separate wall pass. Output must be **deterministic** from `Seed` for a fixed grid and parameters.

Index layout: `index = x + y × width` (row-major, `x` east, `y` north in game coords).

## Entry point

```csharp
int[] Generate(int width, int height, bool[] walkable, CellElevationGenerationParams parameters)
```

**Validation:** `width, height > 0`; `walkable.Length == width × height`; `MinStep ≤ MaxStep`.

**Pipeline:**

1. Walkable pass — mode dispatch; only indices where `walkable[i]` stay non-zero from this pass (others remain `0`).
2. Wall pass — `ApplyWallSteps` fills non-walkable indices.
3. Return `steps`.

---

## Walkable modes

### PerCell

For each walkable `(x, y)`:

```text
steps[index] ← UniformRandom(MinStep, MaxStep)   // inclusive, System.Random(Seed)
```

No spatial correlation.

### PlateauStamp

Repeat `PlateauCount` times:

1. Draw `rectWidth ∈ [PlateauMinWidth, PlateauMaxWidth]`, `rectHeight ∈ [PlateauMinHeight, PlateauMaxHeight]`.
2. Draw origin `(x0, y0)` uniformly in grid (may clip at edges).
3. Draw `step ∈ [MinStep, MaxStep]`.
4. For each walkable cell in `[x0, x0+rectWidth) × [y0, y0+rectHeight)`, set `steps[index] = step`.

Later stamps overwrite overlaps.

### FixedChunk

For each walkable `(x, y)`:

```text
chunkX = x / ChunkSize
chunkY = y / ChunkSize
chunkSeed = HashChunk(Seed, chunkX, chunkY)    // xor mix, unchecked int
steps[index] ← UniformRandom(MinStep, MaxStep)  // new Random(chunkSeed) per chunk
```

All walkable cells in the same chunk share one step.

### FractalNoise and RidgedNoise

Shared setup per walkable cell:

```text
nx = (x + 0.5) / width  - 0.5
ny = (y + 0.5) / height - 0.5
elevation01 ← sample fractal or ridged field at (nx, ny)
steps[index] ← QuantizeElevationStep(elevation01, MinStep, MaxStep)
```

Only walkable cells are sampled; walls stay `0` until the wall pass.

---

## Noise sampling (FractalNoise / RidgedNoise)

### SeededNoise2D

Value noise on ℤ², output ∈ `[0, 1]`.

For continuous `(nx, ny)`:

1. `x0 = floor(nx)`, `y0 = floor(ny)`; corners `(x0,y0)…(x1,y1)`.
2. Each corner: `Lattice(seed, ix, iy) = Hash(seed, ix, iy) / uint.MaxValue`.
3. Bilinear blend with smoothstep weights: `t' = t²(3 - 2t)`.

Hash mixes `seed`, lattice `x`, `y` with fixed 32-bit constants (see `SeededNoise2D.cs`).

### Fractal (fBm)

```text
frequency ← max(0.01, NoiseFrequency)
persistence ← clamp(Persistence, 0.01, 1)
sum ← 0; ampSum ← 0

for octave in 0 .. OctaveCount-1:
    amplitude ← persistence^octave
    octaveFreq ← frequency × 2^octave
    (offsetX, offsetY) ← OctaveOffset(Seed, octave)   // hash → [0,1) per channel
    noise ← SeededNoise2D(Seed + octave×7919, octaveFreq×nx + offsetX, octaveFreq×ny + offsetY)
    sum += amplitude × noise
    ampSum += amplitude

normalized ← sum / ampSum   // 0 if ampSum == 0
return RedistributeElevation(normalized)
```

### Ridged multifractal

Same octave loop structure; per octave:

```text
noise ← SeededNoise2D(Seed + octave×9176, ...)
ridged ← 2 × (0.5 - |0.5 - noise|)          // ∈ [0, 1], peaks at noise = 0 or 1
contribution ← amplitude × ridged × weight
sum += contribution
ampSum += amplitude
weight ← clamp(ridged, 0, 1)                  // valleys suppress higher octaves
```

Then `normalized ← sum / ampSum` and `RedistributeElevation`.

### Fractal vs Ridged — same seed, different shape

Both modes share `nx`/`ny`, redistribution, and quantization. Only the octave accumulator differs (plain noise vs ridged × weight). Same seed does **not** mean same steps — octave salts differ (**7919** vs **9176**).

**Example** — 8×8 open floor, all walkable, wall pass skipped for display:

| Parameter | Value |
|-----------|-------|
| `Seed` | 4242 |
| `MinStep` / `MaxStep` | 0 / 4 |
| `NoiseFrequency` | 4 |
| `OctaveCount` | 4 |
| `Persistence` | 0.5 |
| Redistribution | defaults (fudge 1.1, exponent 2.5) |

Rows print **north-up** (`y = 7` top row, `y = 0` bottom). Only walkable steps shown.

**FractalNoise**

```text
2  1  0  0  0  1  0  0
1  0  0  1  0  0  0  0
1  0  0  1  0  0  0  0
1  0  0  0  0  1  0  1
1  1  1  0  0  0  1  1
1  1  1  0  1  1  1  1
1  1  1  1  1  1  1  1
2  1  1  2  1  0  0  0
```

**RidgedNoise** (same params)

```text
1  4  2  1  1  1  0  0
2  0  0  2  1  0  0  0
3  0  0  0  0  1  0  1
2  0  0  0  0  1  2  2
2  1  2  1  1  2  2  3
2  2  2  2  1  2  3  2
1  2  3  1  1  1  1  1
1  2  3  1  1  0  0  0
```

| Observation | Fractal | Ridged |
|-------------|---------|--------|
| Step range used | Mostly 0–2; soft blobs | Full 0–4; sharper peaks |
| Low areas | Broad 0–1 plains | Pinned 0 valleys (weight kills detail) |
| High areas | Gradual 1–2 ridges | Isolated 3–4 crests (NW corner **4**) |
| Adjacent delta | Often ≤ 1 | More ±2 jumps — more cliff-seal candidates |

Reproduce: `python Tools/elevation_noise_example.py` in **griddungeon-design-docs** (mirrors Core math for doc fixtures).

### Redistribution

Pushes mass toward extremes before quantization:

```text
clamped ← clamp(value, 0, 1)
fudge ← max(0.01, RedistributionFudge)
exponent ← max(0.01, RedistributionExponent)
return (clamped × fudge)^exponent   capped at 1
```

Defaults: fudge **1.1**, exponent **2.5** — slightly lifts values then compresses mid-range.

### Quantization

```text
if MinStep >= MaxStep: return MinStep

scaled ← MinStep + elevation01 × (MaxStep - MinStep)
return clamp(round(scaled, AwayFromZero), MinStep, MaxStep)
```

---

## Wall pass

For each non-walkable `(x, y)`:

**If `RandomizeWallElevation`:**

```text
extra ← UniformRandom(0, WallExtraMaxStep)   // inclusive upper; 0 if WallExtraMaxStep ≤ 0
steps[index] ← WallStartingStep + extra
```

**Else (default):**

```text
steps[index] ← min(steps[neighbor]) over cardinal walkable neighbors
             // if none: 0
```

Cardinal neighbors: `(x±1, y)`, `(x, y±1)`; skip out of bounds and non-walkable.

---

## Cliff seal (post-generation)

Separate utility: `CellElevationCliffSealer.FindCellsToSeal` — not part of `Generate`, but uses the same step grid.

For each walkable `(x, y)`, check edges to `(x+1, y)` and `(x, y+1)` only (each undirected edge once):

```text
if both walkable and |steps[A] - steps[B]| > maxWalkableStepDelta:
    mark one index for seal:
        HigherStep → index with larger step (A on tie)
        LowerStep  → index with smaller step (A on tie)
```

Returns `bool[] seal` — editor converts sealed walkable cells to layout walls.

Example (`maxWalkableStepDelta = 2`): steps **0** adjacent to **2** → OK; **0** adjacent to **4** → seal.

---

## Determinism

| Source | Rule |
|--------|------|
| PerCell, PlateauStamp | `System.Random(Seed)` sequence |
| FixedChunk | `Random(HashChunk(Seed, chunkX, chunkY))` per chunk |
| Fractal / Ridged | Pure functions of `Seed`, cell coords, parameters; octave salts **7919** / **9176** |
| SeededNoise2D | Integer hash — no floating platform variance |
| Cliff seal | Pure function of grid + steps + threshold — no RNG |

Same `(width, height, walkable, parameters)` → identical `steps[]`.

---

## Parameter summary

| Field | Role |
|-------|------|
| `Seed` | RNG / noise identity |
| `MinStep`, `MaxStep` | Quantization range |
| `Mode` | Walkable dispatch |
| `PlateauCount`, `PlateauMin/MaxWidth`, `PlateauMin/MaxHeight` | PlateauStamp |
| `ChunkSize` | FixedChunk block size |
| `NoiseFrequency`, `OctaveCount`, `Persistence` | Noise scale / detail |
| `RedistributionExponent`, `RedistributionFudge` | Post-noise curve |
| `RandomizeWallElevation`, `WallStartingStep`, `WallExtraMaxStep` | Wall pass |

---

## Tests

Edit Mode — `Assets/Tests/Map/CellElevationGeneratorTests.cs`, `CellElevationCliffSealerTests.cs`: determinism, chunk/plateau invariants, min/max bounds, wall-follow-floor, cliff delta threshold.
