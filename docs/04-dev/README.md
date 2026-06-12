# Dev / integrator docs

Forward-facing references for tooling, external HUD authors, and forks — **not** player-facing spec.

| Doc | Purpose |
|-----|---------|
| [UI event contract](ui-event-contract.md) | Runtime `public event` + command APIs for custom UI; **edit when game repo APIs change** |
| [Custom skill picker UI](custom-skill-picker-ui.md) | Replace combat skill modal (`ISkillUsePickerView`, host wiring, UITK hooks, tests) |
| [Shared menu & picker UI](shared-menu-picker-ui.md) | Rail menu, `ItemListPickerView`, skill picker — shared UITK components, diagrams, extension guide |
| [Centralized UI services](centralized-ui-services.md) | Cross-phase overlays — `InputHintPresenter`, `CommandRail` + `CommandPanelModalSupport`, `PartyFormationFloater`, sort stack, bootstrap, add-new checklist; [ADR 038](../../decisions/038-centralized-ui-presentation-lifecycle.md) + [ADR 039](../../decisions/039-uitk-dotween-show-hide.md) |
| [UITK BEM transition guide](uitk-bem-transition-guide.md) | `BemMotionCompletion` + `VisualPresentationSync` API, recipes for `*Transition` helpers and presenter sync, steady-class registry, tests |
| [Centralized UI gotchas](centralized-ui-gotchas.md) | Implementation traps — pop-in exit races, `IsSettling`, context-switch hide, marker fade vs step motion, map panel fade vs screen fade, detached-host tests |
| [Custom party UI](custom-party-ui.md) | Replace exploration strip / combat party roster / map marker (`CombatRosterView`, events, UITK hooks) |
| [Authoring floor transition beats](authoring-floor-transition-beats.md) | `stairs_default` vignette prefab, catalog, Cinemachine, Unity menu workflow |
| [Layered UITK panels](layered-uitk-panels.md) | Split HUD into panel `UIDocument` components — [ADR 037](../../decisions/037-layered-uitk-panels.md) (draft) |

Gameplay rules and phase authority stay in [02 — Systems](../02-systems/) and [05 — Class design MVP1](../05-class-design.md).
