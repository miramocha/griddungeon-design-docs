# ADR 019 — Floor Verticality (Doom-style)

**Status:** Accepted  
**Date:** 2026-05-21

## Context

Some floors need **height bands** (upper walkways, pits, jump pads) while keeping **discrete grid** exploration ([ADR 001](001-grid-movement.md)). Player fantasy: *Doom*-like maps — multiple walkable **levels** at the same `(x, y)` are allowed, but the party **never walks under** an upper floor (no crawl space, no “under the bridge” routing).

## Decision

1. **Grid cell identity** is **`(x, y, level)`** — integer `level` ≥ 0 is the walkable **floor band** the party stands on. Same `(x, y)` at different `level` values are **different cells**.
2. **Party state** tracks `GridPosition` with `Level` plus `FacingDirection` (four cardinals unchanged).
3. **Normal displacement** (forward / back / strafe) moves on the **same `level`** only, subject to walls and **no-under** rules (below).
4. **Vertical change** happens only through authored connectors:
   - **Stairs / ramps** — `level ± 1` at that cell when stepping or interacting.
   - **Jump pad** — scripted offset in facing space, e.g. **+2 cells forward, +1 level up** (data-driven per pad).
   - **Drop / pit** (optional) — explicit one-way down or hazard tile; never implicit “fall” from walking.
5. **No under floors:** horizontal moves that would put the party **under** blocking upper geometry are **illegal**, even if a lower `level` exists at the same `(x, y)`. Designers block with **overhang / low-ceiling** flags or absent lower walkability — not player skill.
6. **FOEs, encounters, map reveal** use full `(x, y, level)` — patrol and icons are on one level; step events fire on entering a new cell including level changes via connectors.
7. **Map HUD ([ADR 002](002-mapping-model.md)):** MVP1 2D map shows the **party’s current `level`** slice; other levels when visited (optional layer toggle post-MVP1).

## Movement validation (Core)

`DungeonExplorer` / `FloorCollisionQuery` checks target `(x, y, level)`:

| Check | Rule |
|-------|------|
| Walkable surface | Target cell has walkable floor at `level` |
| Same-level step | `level` unchanged; walls on horizontal edges at that level |
| Vertical connector | Stairs / jump pad / ramp authorizes `level` delta |
| **No-under** | Horizontal step rejected if an **overhang** blocks passage at the party’s `level` (upper band floor exists above the path and lower band is not a valid same-plane route) |

**Jump pad example** (`jump_pad_launch_2f1u`):

- From `(x, y, L)` facing north → land target `(x, y+2, L+1)` if walkable and not blocked by no-under rules.
- One **displacement** event (FOE tick, encounter roll) on **landing** cell; presentation may use arced lerp in FPV + proxy.

## Rejected

| Option | Why |
|--------|-----|
| Free 3D movement / jumping without grid | Breaks EO step, FOE, map ([ADR 001](001-grid-movement.md)) |
| Walking “under” bridges or ledges | Violates Doom-style readability and map clarity |
| Implicit fall between levels | Only explicit pits / stairs / pads |
| Full 3D minimap camera | Deferred; 2D chart per **level** band |

## Consequences

- `GridPosition` gains `Level` in Core; saves and `FloorMapState` key reveal by `(x, y, level)` (or per-level 2D layers).
- Floor content adds `level` to spawn paths, FOE placement, jump-pad / stair `FeatureType` data.
- Floor painter: per-`level` layer in the grid canvas; FPV scene may use stacked roots per band for art preview.
- MVP1 **content** may ship flat floors first; verticality is **structure-ready** when a floor uses it.

## Related

- [02 — Dungeon navigation](../docs/02-dungeon-navigation.md#grid-model)
- [ADR 002 — Mapping model](002-mapping-model.md)
- [ADR 001 — Grid movement](001-grid-movement.md)
- [ADR 003 — FOE step patrol](003-foe-step-patrol.md)
- [MVP1 spec](../docs/archive/mvp1-spec.md)
