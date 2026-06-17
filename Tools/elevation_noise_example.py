"""Mirror GridDungeon CellElevationGenerator noise modes for doc examples."""
from __future__ import annotations

from math import floor, pow


def u32(n: int) -> int:
    return n & 0xFFFFFFFF


def hash_lattice(seed: int, x: int, y: int) -> float:
    h = u32(seed)
    h = u32(h ^ u32(x * 374761393))
    h = u32(h ^ u32(y * 668265263))
    h = u32((h ^ (h >> 13)) * 1274126177)
    h = u32(h ^ (h >> 16))
    return h / 4294967295.0


def smooth(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def seeded_noise_2d(seed: int, nx: float, ny: float) -> float:
    x0 = int(floor(nx))
    y0 = int(floor(ny))
    x1 = x0 + 1
    y1 = y0 + 1
    tx = smooth(nx - x0)
    ty = smooth(ny - y0)
    n00 = hash_lattice(seed, x0, y0)
    n10 = hash_lattice(seed, x1, y0)
    n01 = hash_lattice(seed, x0, y1)
    n11 = hash_lattice(seed, x1, y1)
    nx0 = lerp(n00, n10, tx)
    nx1 = lerp(n01, n11, tx)
    return lerp(nx0, nx1, ty)


def hash_octave(seed: int, octave: int, channel: int) -> int:
    return u32((seed * 397) ^ (octave * 1013) ^ (channel * 9176))


def octave_offset(seed: int, octave: int) -> tuple[float, float]:
    ox = (hash_octave(seed, octave, 0) % 1000) / 1000.0
    oy = (hash_octave(seed, octave, 1) % 1000) / 1000.0
    return ox, oy


def redistribute(value: float, fudge: float = 1.1, exponent: float = 2.5) -> float:
    clamped = max(0.0, min(1.0, value))
    fudge = max(0.01, fudge)
    exponent = max(0.01, exponent)
    return min(1.0, pow(min(1.0, clamped * fudge), exponent))


def quantize(elevation01: float, min_step: int, max_step: int) -> int:
    if min_step >= max_step:
        return min_step
    scaled = min_step + elevation01 * (max_step - min_step)
    rounded = int(scaled + 0.5) if scaled >= 0 else int(scaled - 0.5)
    return max(min_step, min(max_step, rounded))


def sample_fractal(
    seed: int,
    nx: float,
    ny: float,
    octave_count: int = 4,
    frequency: float = 4.0,
    persistence: float = 0.5,
) -> float:
    frequency = max(0.01, frequency)
    persistence = max(0.01, min(1.0, persistence))
    total = 0.0
    amp_sum = 0.0
    for octave in range(octave_count):
        amplitude = pow(persistence, octave)
        octave_freq = frequency * pow(2, octave)
        ox, oy = octave_offset(seed, octave)
        sample = seeded_noise_2d(
            seed + octave * 7919,
            octave_freq * nx + ox,
            octave_freq * ny + oy,
        )
        total += amplitude * sample
        amp_sum += amplitude
    normalized = total / amp_sum if amp_sum > 0 else 0.0
    return redistribute(normalized)


def sample_ridged(
    seed: int,
    nx: float,
    ny: float,
    octave_count: int = 4,
    frequency: float = 4.0,
    persistence: float = 0.5,
) -> float:
    frequency = max(0.01, frequency)
    persistence = max(0.01, min(1.0, persistence))
    total = 0.0
    amp_sum = 0.0
    weight = 1.0
    for octave in range(octave_count):
        amplitude = pow(persistence, octave)
        octave_freq = frequency * pow(2, octave)
        ox, oy = octave_offset(seed, octave)
        noise = seeded_noise_2d(
            seed + octave * 9176,
            octave_freq * nx + ox,
            octave_freq * ny + oy,
        )
        ridged = 2.0 * (0.5 - abs(0.5 - noise))
        total += amplitude * ridged * weight
        amp_sum += amplitude
        weight = max(0.0, min(1.0, ridged))
    normalized = total / amp_sum if amp_sum > 0 else 0.0
    return redistribute(normalized)


def generate_grid(
    width: int,
    height: int,
    seed: int,
    min_step: int,
    max_step: int,
    mode: str,
) -> list[list[int]]:
    sampler = sample_fractal if mode == "fractal" else sample_ridged
    grid = [[0] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            nx = (x + 0.5) / width - 0.5
            ny = (y + 0.5) / height - 0.5
            e = sampler(seed, nx, ny)
            grid[y][x] = quantize(e, min_step, max_step)
    return grid


def format_grid(grid: list[list[int]]) -> str:
    return "\n".join("  ".join(str(c) for c in row) for row in reversed(grid))


def main() -> None:
    w, h = 8, 8
    seed = 4242
    min_step, max_step = 0, 4
    fractal = generate_grid(w, h, seed, min_step, max_step, "fractal")
    ridged = generate_grid(w, h, seed, min_step, max_step, "ridged")
    print("FRACTAL")
    print(format_grid(fractal))
    print("RIDGED")
    print(format_grid(ridged))


if __name__ == "__main__":
    main()
