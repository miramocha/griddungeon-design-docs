# ADR 012 — Unity 6 Tech Stack

**Status:** Accepted  
**Date:** 2026-05-20

## Context

Implementation will live in a **Unity** project. Engine version and render pipeline affect tooling, packages, and how systems (Input, URP, Timeline) are documented and built.

## Decision

1. **Engine:** **Unity 6** (6000.x line). Pin exact editor version in the game repo’s `ProjectSettings/ProjectVersion.txt` when the Unity project is created; design docs refer to **Unity 6** unless a breaking upgrade is explicitly decided.
2. **Render pipeline:** **URP** (Universal Render Pipeline) for FPV dungeon, hub UI, and combat presentation.
3. **Input:** **Input System** package (`com.unity.inputsystem`) — not legacy Input Manager.
4. **Platform build target:** **Standalone Windows PC** first ([ADR 008](008-campaign-defaults.md)); other Standalone targets optional later.
5. **Cinematics (combat):** **Timeline** (or Animation-driven clips) per [combat presentation](../docs/02-systems/combat-presentation.md); no custom engine outside Unity.
6. **Shaders:** **Shader Graph** (URP) for **most** materials and VFX — FPV dungeon, battle arena, UI-adjacent fullscreen effects. **HLSL** / custom `.shader` files **only when needed** (e.g. unsupported graph node, performance-critical pass, third-party integration).

## Unity 6 implications (design → implementation)

| Area | Note |
|------|------|
| **Project template** | 3D (URP) or URP Empty; no Built-in RP |
| **Shaders** | URP Shader Graph default; document HLSL exceptions in asset README or comment header |
| **Packages** | Input System, URP, Shader Graph (included with URP), Timeline; Addressables when content scale warrants |
| **Testing** | `CombatSimulator` as pure C# where possible; Unity Test Framework for playmode/integration |
| **Editor tooling** | Custom inspectors for FOE patrol / `stepsPerMove` ([04 — Tech notes](../docs/04-tech-notes.md)) |
| **Version drift** | Upgrade Unity 6 minor releases in a dedicated branch; re-run FPV + map + combat smoke |

## Rejected

| Option | Why |
|--------|-----|
| Unity 2022 LTS as primary | User targets Unity 6 |
| Built-in render pipeline | URP already assumed for shader/workflow |
| Legacy Input Manager | PC rebind + action maps need Input System |
| HLSL-first / handwritten shader library | Shader Graph covers most URP needs; HLSL raises maintenance cost |

## Consequences

- All tech notes and input docs assume **Unity 6 + URP + Input System + Shader Graph-first** shaders.
- New surface shaders start as **Shader Graph**; HLSL requires a short rationale in PR / asset note.
- Third-party assets must support Unity 6 / URP before adoption.
- CI/build machines use the same Unity 6 editor version as developers.

## Related

- [04 — Tech notes](../docs/04-tech-notes.md)
- [02 — Input bindings](../docs/02-systems/input-bindings.md)
- [ADR 008 — Campaign defaults](008-campaign-defaults.md)
- [ADR 009 — Input bindings PC](009-input-bindings-pc.md)
