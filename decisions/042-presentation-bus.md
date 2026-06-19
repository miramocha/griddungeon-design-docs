# ADR 042 — Runtime presentation bus + shell catalog

**Status:** Accepted  
**Date:** 2026-06-18  
**Epic:** Reactive presentation UI + UVS hooks (game)  
**Docs:** [ui-event-contract § Presentation bus](../docs/04-dev/ui-event-contract.md#presentation-bus), [centralized-ui-services § Presentation bus](../docs/04-dev/centralized-ui-services.md#presentation-bus), [presentation shell implementation](../docs/04-dev/presentation-shell-implementation.md), [UVS phase presentation § UI presentation hooks](../docs/02-systems/uvs-phase-presentation.md#ui-presentation-hooks)

## Context

Phase HUDs and shared UITK services today **push layout** directly (`CommandRail.PanelHost`, `Q()`, UXML names). That couples gameplay orchestrators to UITK structure, blocks world-space shell swaps, and makes UVS integration awkward (Runtime `Action<T>` is not graph-friendly).

[ADR 017](017-game-phase-controller.md) keeps macro phase authority in C#. [ADR 037](037-layered-uitk-panels.md) Tier 2 allows world-space UITK rigs. [ADR 038](038-centralized-ui-presentation-lifecycle.md) standardizes overlay show/hide — distinct from **what** those overlays display.

## Decision

### 1. Two channels: gameplay events vs presentation DTOs

| Channel | Owner | Consumers | Authority |
|---------|-------|-----------|-----------|
| **Gameplay events** | Controllers (`GameState`, `CombatController`, …) | Projectors, custom HUDs | Rules, transitions, save |
| **Presentation DTOs** | Projectors in `GridDungeon.Runtime.Presentation` | UITK shells, world rigs, UVS via bridge | Display snapshots only |

Projectors **read** controllers; they do **not** adjudicate combat, hub services, or phase transitions.

### 2. Presentation bus (`UiPresentationBridge`)

- Lives on bootstrap `Game` root (sibling to `GameState`).
- **C#:** `IUiPresentationBus` — `CommandRailChanged`, `CommandRailInfoChanged`, optional beat events.
- **UVS:** `[SerializeField] UnityEvent` mirrors on the same `MonoBehaviour` — listen-only; no gameplay writes.
- **Anti-patterns (UVS):** must not call `CommandRail.SwapPanelContent`, rebuild `PanelHost`, `RequestTransition`, or save APIs from graphs.

### 3. Shell catalog (`UiPresentationCatalog`)

- ScriptableObject registry at `Assets/UI/Settings/UiPresentationCatalog.asset` (bootstrap `Ensure*`).
- Rows: `PresentationShellDefinition` — `GameObject ShellPrefab`, `PresentationSurfaceKind`, optional filters (`GamePhase`, rail context, `ProfileId`), optional anchor kind.
- **Default row** for each surface = current **screen-space UITK fallback** (not a parallel code path).
- `PresentationShellHost` resolves catalog at Play Mode, instantiates prefab, wires shell to bus.
- Swapping art/layout = edit catalog prefab assignment — projectors and HUDs unchanged.

### 4. Shell contracts (Runtime interfaces, UI implementations)

```csharp
// GridDungeon.Runtime.Presentation — DTOs only on interfaces
public interface ICommandRailShell
{
    void Apply(CommandRailPresentationState state);
    void PlayBeat(PresentationBeat beat);
}
```

Prefab components in `GridDungeon.UI` implement Runtime interfaces. Factory: `Instantiate(prefab)` → `GetComponent<ICommandRailShell>()`.

### 5. Command rail pilot (shipped)

- `CommandRailPresentationProjector` subscribes to existing Runtime signals; emits `CommandRailPresentationState`.
- `CommandRailScreenShell` is the only place that knows `command-rail-panel` / BEM classes.
- Phase HUDs publish via `CommandRailPresentationProjector.SetMenuItems` / `SetModalOpen` — **no** `ResolvePanelHost` on phase views ([#321](https://github.com/miramocha/griddungeon-game/pull/321)).

### 6. Item list inventory on bus (shipped)

- `ItemListInventoryPresentationProjector` carries picker row/tab snapshots; `ItemListInventoryPresenter` keeps `ICentralizedUiSurface` Show/Hide ([#322](https://github.com/miramocha/griddungeon-game/pull/322)).
- Hub shop, combat item, and party bag adapters call `TryPublishContent` when `UiPresentationBridge` is present.

### 7. Asmdef placement

| Type | Assembly |
|------|----------|
| DTOs, projectors, catalog, host, bridge | `GridDungeon.Runtime` |
| `ICommandRailShell` implementations, UXML | `GridDungeon.UI` |
| UVS graphs | Reference `GridDungeon.Runtime` only — not `GridDungeon.UI` |

Core stays free of Unity presentation types.

### 8. Out of scope

- Moving `GamePhase` authority to UVS.
- Replacing `InputHints.Publish` with the bus.
- Full reactive migration of every centralized service (follow-up issues).

## Consequences

- New cross-phase chrome: add projector + shell interface + catalog row before embedding `PanelHost` in phase HUDs.
- Dev Bootstrap: `EnsureUiPresentationCatalog()` + `WireUiPresentation()` on `Game`; shells spawn at Play Mode.
- Tests: Edit Mode for catalog resolve, projector snapshots, shell `Apply`; Play Mode for UVS smoke.

## Related

- [ADR 017](017-game-phase-controller.md) — phase authority  
- [ADR 037](037-layered-uitk-panels.md) — screen vs world UITK  
- [ADR 038](038-centralized-ui-presentation-lifecycle.md) — overlay show/hide  
- [ui-event-contract.md](../docs/04-dev/ui-event-contract.md)  
- [uvs-phase-presentation.md](../docs/02-systems/uvs-phase-presentation.md)
