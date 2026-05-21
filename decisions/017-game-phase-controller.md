# ADR 017 — Game Phase Controller (C#)

**Status:** Accepted (MVP1)  
**Date:** 2026-05-21

## Context

MVP1 alternates between **hub**, **exploration**, and **combat** ([mvp1-spec](../docs/mvp1-spec.md)). The tech checklist calls for `GameState` hub / explore / combat. We considered **Unity Visual Scripting (UVS) state graphs** for macro phases; combat also has internal sub-phases (AGI turns — Protocol optional on core turn when Synchro is 100% — → end of round).

Requirements:

- **Authoritative** phase transitions (who may enter combat, return to hub, etc.)
- **Testable** combat and exploration rules in `GridDungeon.Core` without Visual Scripting
- **Clear Enter/Exit** hooks for input maps, scene visibility, and event subscriptions
- **Single responsibility** — phase orchestration separate from combat round logic

## Decision (MVP1)

1. **Macro game flow is pure C#** — `GamePhaseController` + three `IPhaseController` implementations. **No UVS state graph** as source of truth in MVP1.
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
| Hub | Exploration | `HubController.LeaveHub` — S1: **B1F mouth** after Act 2; S2+: warp gate; new game: Act 1 intro spawn ([campaign S1 intro](../docs/03-content/campaign/s1-intro.md)) |
| Exploration | Combat | FOE contact, random encounter roll |
| Combat | Exploration | Victory, successful flee |
| Exploration | Hub | Stairs to surface / retreat item / designer exit |
| Combat | Hub | Party wipe → load last inn save (after GAME OVER flow) |
| Hub | Hub | Invalid — no-op |
| Combat | Combat | Invalid — no-op |

Invalid transitions return `false` from `TryTransitionTo`; callers log or show UI feedback.

## Rejected for MVP1

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

- Implement under `Assets/Scripts/Runtime/Game/` per [class design MVP1](../docs/05-class-design-mvp1.md).
- `InputRouter` subscribes to `PhaseChanged` (or is called from phase `OnExit`/`OnEnter`).
- Systems request transitions through `GameState` / `GamePhaseController`, not by enabling scenes ad hoc.
- Document flow and APIs in [game phase system](../docs/02-systems/game-phase.md).

## Related

- [Game phase (system doc)](../docs/02-systems/game-phase.md)
- [05 — Class design MVP1](../docs/05-class-design-mvp1.md)
- [04 — Tech notes](../docs/04-tech-notes.md)
- [MVP1 spec](../docs/mvp1-spec.md)
- [Combat](../docs/02-systems/combat.md) — combat round vs game phase terminology
