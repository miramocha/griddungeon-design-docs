---
tags:
  - path/decisions
  - type/adr
  - scope/optional
  - status/accepted
  - domain/combat
---
# ADR 027 — Combat Cinematic Timeline Events

> **Scope: Optional feature** — not required for initial release.

**Status:** Accepted  
**Date:** 2026-05-23  
**Aligns with:** [ADR 012](012-unity-6-stack.md) (Timeline for combat cinematics), [ADR 015](015-mvp1-combat.md) launch `Fixed` only), [combat presentation](../docs/02-systems/combat-presentation.md)

## Context

Combat skills use three presentation profiles: `Fixed`, `Cinematic`, and `CinematicQTE` ([combat presentation](../docs/02-systems/combat-presentation.md)). Launch ships **`Fixed` only**; cinematics are stubbed ([ADR 015](015-mvp1-combat.md)).

Early doc sketches used **`at_sec`** fields for QTE prompt timing and implied hand-authored **durations** in skill data. That duplicates timing already authored on Timeline clips, drifts when clips are re-timed, and splits the source of truth between content DB and presentation assets.

Exploration animation speed is preset-driven in [ADR 018](018-exploration-animation-speed.md). Combat cinematics need a different model: **per-skill authored length** on sparse Timeline assets, with **runtime callbacks** at beats and at end — not a second clock in `SkillDefinition` or Core.

**Goals**

- End-of-cinematic and mid-cinematic beats fire from **Unity Timeline**, not polled timers or duplicate config seconds.
- `CombatController` / Core stay unaware of clip length; presentation owns wait/skip/lock.
- QTE windows align to authored frames; damage resolves once after tier is known ([combat presentation § Damage application](../docs/02-systems/combat-presentation.md#combat-flow-integration)).

## Decision

### 1. Source of truth

| Concern | Owner | Mechanism |
|---------|--------|-----------|
| Clip length | Timeline asset on prefab | `PlayableDirector.duration` (read-only at runtime) |
| Cinematic end | `CinematicSkillPlayer` | `PlayableDirector.stopped` |
| QTE prompt open/close | Custom Timeline **markers** (`INotification`) | `CinematicSkillPlayer` as `INotificationReceiver` |
| Rare boss multi-hit beat | Optional **Signal** `Cinematic_MultiHit` | Boss skills tagged `multi_hit_cinematic` only |
| Skip | `CombatPresentationController` | Cancel QTE → `Stop()` → `stopped` → **base** tier |
| AGI / turn rules | `CombatController` (Core) | Unchanged; presentation **pauses** queue advance until cinematic completes or skips |

**Do not** add `cinematicDurationSec`, `hitFrameSec`, or `qte_prompts[].at_sec` to locked `SkillDefinition` for shipping cinematics.

### 2. Runtime components (Runtime / UI assemblies)

| Type | Responsibility |
|------|----------------|
| `SkillCinematicPrefab` (prefab) | `PlayableDirector` + `CinematicSkillPlayer` + bindings to `BattleCameraRig` / slot anchors |
| `CinematicSkillPlayer` | `Play()` with combat wrap settings; `stopped`; `INotificationReceiver` for QTE markers |
| `CombatPresentationController` | Exclusive cinematic lock; ordered skip; unlock queue on `stopped` |
| `QTEController` | `OpenPrompt` / `ClosePrompt` / `CancelActivePrompts`; tier → `QTEResult` before damage apply |

`SkillDefinition` retains **`presentation`** + **`cinematicAssetId`** (prefab / Timeline reference) only. **QTE damage bonuses** (`perfect` / `good` / `base` multipliers) stay on skill or linked `CinematicSkillDefinition` SO — **timing** lives on Timeline, **numbers** on skill data.

### 3. End-of-cinematic callback

- Subscribe to **`PlayableDirector.stopped`** when playback ends naturally or after **`Stop()`** (skip).
- On `stopped`: apply skill rules (base + QTE bonus if applicable) → release presentation lock → resume AGI playback.
- **`wasSkipped`:** set only from skip input before `Stop()` — for combat log / analytics; **does not** change damage tier (skip always **base** per [combat presentation § Skip](../docs/02-systems/combat-presentation.md#skip--accessibility)).

### 4. Mid-cinematic beats — markers vs signals

**QTE prompts (locked):** Custom Timeline markers on a dedicated marker track:

| Marker type | Payload (on marker) | Handler |
|-------------|---------------------|---------|
| `CinematicQteOpenMarker` | `promptIndex`, `QtePromptType`, `inputBindingId`, `windowSec` | `QTEController.OpenPrompt(...)` |
| `CinematicQteCloseMarker` | `promptIndex` | `QTEController.ClosePrompt(promptIndex)` |

`CinematicSkillPlayer` implements `INotificationReceiver` and forwards to `QTEController`. One marker **type** per open/close; many marker **instances** per skill Timeline.

**Why not one Signal asset per key:** Unity Signal emitters do not carry per-instance structured payload without proliferating Signal assets (`Cinematic_QTE_Open_Space`, `Cinematic_QTE_Open_1`, …). Markers keep one type and per-beat data on the Timeline.

**Optional coarse Signal (boss only):**

| Signal | When | Handler |
|--------|------|---------|
| `Cinematic_MultiHit` | Tagged boss skills only | Optional mid-cinematic VFX; **not** default damage apply |

Default damage: **single resolve** at `stopped`. Do not fire damage on every marker.

**Rejected for production:** `Invoke(delay)`, per-frame `director.time` polling, or primary `at_sec` in skill content.

### 5. Skip mid-QTE (locked order)

When the player skips (or **Skip all cinematics**):

1. **`QTEController.CancelActivePrompts()`** — hide prompt HUD; stop listening for input.
2. **`PlayableDirector.Stop()`** — halt Timeline.
3. **`stopped` handler** — apply skill at **base** tier; release lock; resume queue.

Do not leave an open prompt visible while `stopped` runs. Accessibility **Auto QTE** never opens prompts; still uses the same `stopped` path.

### 6. `PlayableDirector` wrap mode (locked)

| Context | `extrapolationMode` | Loop |
|---------|---------------------|------|
| **Combat runtime** | `Hold` | **No** — one shot; `initialTime = 0` on each `Play()` |
| **Editor preview** (context menu / inspector) | `Hold` | **No** by default |
| **Editor loop preview** (optional dev tool only) | `Loop` | Allowed **only** in editor preview API; never set on combat prefab at runtime |

Combat code must not rely on Loop wrap; end detection is always **`stopped`**, not “time wrapped.”

### 7. Flow (locked)

```
Confirm skill (Cinematic | CinematicQTE)
  → CombatPresentationController acquires lock; AGI presentation pause
  → CinematicSkillPlayer.Play(asset)  [Hold, no loop]
  → [QTE only] Markers: Open … Close per prompt
  → PlayableDirector.stopped (natural end or skip chain)
  → Apply damage/status once (tier known)
  → Unlock; resume queue
```

`Fixed` skills **unchanged**: DOTween zoom/VFX + presentation lock per UI beat ([04 — Tech notes § UI reactivity](../docs/04-tech-notes.md#ui-reactivity)); no `PlayableDirector`.

### 8. MVP scope

| Milestone | Rule |
|-----------|------|
| **Launch** | ADR applies to **stub** / pipeline only; no shipping cinematics ([ADR 015](015-mvp1-combat.md)) |
| **Optional** | First `Cinematic` + first `CinematicQTE` **must** use markers + `stopped`; no `at_sec` in locked content |
| **Later** | More skills; hold/mouse QTE types per combat presentation |

### 9. Authoring conventions

- One **PlayableDirector** per `SkillCinematicPrefab`; director references Timeline asset for that skill.
- Marker track named **`Cinematic Beats`**; marker types live under `Assets/Content/Cinematics/Markers/` (game repo).
- Target clip length **3–8 s** per combat presentation; QTE active time ≤ ~2 s — content review, not Core.
- **Timeline** drives camera/actors; **DOTween** only for `Fixed` target zoom and UI tweens — do not duplicate the same beat on both unless Timeline explicitly drives DOTween ([04 — Tech notes § Animation](../docs/04-tech-notes.md#animation-dotween--timeline)).

## Rejected

| Option | Why |
|--------|-----|
| Primary `at_sec` / `durationSec` on `SkillDefinition` | Second clock; desyncs from clip edits |
| One Signal asset per QTE key/prompt | Asset explosion; no per-emitter payload |
| `AnimationEvent`-only on a single clip | Poor fit for multi-track camera + UI + slot actors |
| Core waits `Task.Delay(duration)` | Couples rules to presentation; untestable sim boundary |
| Combat-wide animation speed preset (ADR 018 mirror) | Out of scope; defer unless accessibility requests global combat time scale |
| Partial damage on every marker/Signal by default | Conflicts with single resolve at end |

## Consequences

- **Design:** [combat presentation](../docs/02-systems/combat-presentation.md) authoring updated; deprecated `at_sec` example removed.
- **Content:** Cinematic skills ship as prefab + Timeline + marker types under `Assets/Content/Cinematics/` (game repo).
- **Runtime:** `CinematicSkillPlayer` + `CombatPresentationController`; unsubscribe `stopped` on disable/combat end.
- **Tests:** Core sim unchanged; Edit Mode may mock `ICinematicPlayer` or invoke `stopped` immediately; no batch Timeline in CI while Editor open ([unity-no-cli-tests](../.cursor/rules/unity-no-cli-tests-while-editor-open.mdc)).
- **Skip / a11y:** Skip chain in §5; “Skip all cinematics” bypasses `Play()` entirely.

## Related

- [ADR 012 — Unity 6 stack](012-unity-6-stack.md)
- [ADR 015 — launch combat](015-mvp1-combat.md)
- [ADR 018 — Exploration animation speed](018-exploration-animation-speed.md) (orthogonal — exploration presets only)
- [Combat presentation](../docs/02-systems/combat-presentation.md)
- [04 — Tech notes § Animation](../docs/04-tech-notes.md#animation-dotween--timeline)
- [05 — class design § Skills](../docs/05-class-design.md#skills)
- [Input bindings — cinematic QTE](../docs/02-systems/input-bindings.md#cinematic-qte)
