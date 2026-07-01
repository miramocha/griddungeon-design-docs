---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/phase
---
# ADR 017 — Game Phase Controller (C#)

**Status:** Accepted (required slice)  
**Date:** 2026-05-21

## Context

Launch flow alternates between **hub**, **exploration**, and **combat** ([release scope](../docs/00-release-scope.md)). The tech checklist calls for `GameState` hub / explore / combat. We considered **Unity Visual Scripting (UVS) state graphs** for macro phases; combat also has internal sub-phases (AGI turns — Protocol optional on core turn when Synchro is 100% — → end of round).

Requirements:

- **Authoritative** phase transitions (who may enter combat, return to hub, etc.)
- **Testable** combat and exploration rules in `GridDungeon.Core` without Visual Scripting
- **Clear Enter/Exit** hooks for input maps, scene visibility, and event subscriptions
- **Single responsibility** — phase orchestration separate from combat round logic

## Decision

1. **Macro game flow is pure C#** — `GamePhaseController` + three `IPhaseController` implementations. **No UVS state graph** as source of truth at launch.
2. **`GamePhase` enum** lives in `GridDungeon.Core`: `Hub`, `Exploration`, `Combat`.
3. **`GamePhaseController`** (Runtime, plain C# class) owns `Current`, validates transitions via `TryTransitionTo`, raises `PhaseChanged`.
4. **Phase controllers** (Runtime `MonoBehaviour` or plain classes wired by `GameState`):
   - `HubPhaseController` — hub services, inn save entry
   - `ExplorationPhaseController` — `DungeonExplorer`, `MapSystem`, `FoeSystem`, gather, random encounters
   - `CombatPhaseController` — `CombatController`, `CombatScenePresenter`; hides exploration view
5. **`GameState`** (Runtime `MonoBehaviour`) is the **composition root** on a persistent `Game` object: holds subsystem references, owns `GamePhaseController`, delegates transitions; does **not** embed all phase logic inline.
6. **Combat sub-phases** (`TurnPhase`, `EndOfRound`; Protocol via `CombatCommand.Protocol` on a core turn) stay on **`CombatController`** only — not on `GamePhaseController`.
7. **Optional later:** thin UVS graph that **reacts** to `PhaseChanged` for fades/camera only; must not decide transitions or game rules.

## Transition table (macro)

| From | To | Typical trigger |
|------|-----|-----------------|
| Hub | Exploration | `HubController.LeaveHub` — S1: **B1F gate** after Act 2; S2+: warp gate; new game: Act 1 intro spawn ([campaign S1 intro](../docs/03-content/campaign/s1-intro.md)) |
| Exploration | Combat | FOE contact, random encounter roll |
| Combat | Exploration | Victory, successful flee |
| Exploration | Hub | Stairs to surface / retreat item / designer exit |
| Combat | Hub | Party wipe → load last inn save (after GAME OVER flow); **S1 tutorial only:** scripted hub warp after `s1_tutorial_hub_return` ([story events](../docs/02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)) |
| Hub | Hub | Invalid — no-op |
| Combat | Combat | Invalid — no-op |

Invalid transitions return `false` from `TryTransitionTo`; callers log or show UI feedback.

## Rejected at launch

| Option | Why |
|--------|-----|
| UVS state graph as **only** phase owner | Hard to test, review, and grep; duplicates C# combat/explore rules |
| Fat `GameState` with all `OnEnter`/`OnExit` inline | Violates SRP; grows with every subsystem |
| Animator `StateMachineBehaviour` for game phases | Wrong tool — animator is for character animation |
| `GamePhase` in Visual Scripting variables only | No single authoritative enum for UI/input/asmdefs |

## Design goals (summary)

| Goal | Approach |
|------|----------|
| Authoritative macro flow | `GamePhaseController.TryTransitionTo` only |
| Testable rules | Combat/explore math in Core; phases orchestrate, do not calculate |
| Clear lifecycle | `IPhaseController.OnEnter` / `OnExit` per phase |
| Avoid god `GameState` | Composition root holds refs; phase logic in three controllers |

Full goals table, layer stack, and sequence diagrams: [game phase system](../docs/02-systems/game-phase.md).

## Consequences

- Implement under `Assets/Scripts/Runtime/Game/` per [class design](../docs/05-class-design.md).
- `InputRouter` subscribes to `PhaseChanged` (or is called from phase `OnExit`/`OnEnter`).
- Systems request transitions through `GameState` / `GamePhaseController`, not by enabling scenes ad hoc.
- Document flow and APIs in [game phase system](../docs/02-systems/game-phase.md). UVS integration examples: [uvs-phase-presentation](../docs/02-systems/uvs-phase-presentation.md).

## Related

- [Game phase (system doc)](../docs/02-systems/game-phase.md)
- [UVS — phase & presentation hooks](../docs/02-systems/uvs-phase-presentation.md)
- [05 — class design](../docs/05-class-design.md)
- [04 — Tech notes](../docs/04-tech-notes.md)
- [release scope](../docs/00-release-scope.md)
- [Combat](../docs/02-systems/combat.md) — combat round vs game phase terminology
