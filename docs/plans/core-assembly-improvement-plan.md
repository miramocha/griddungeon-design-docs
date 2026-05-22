# Core assembly — improvement plan (Unity-only)

**Status:** Draft  
**Last updated:** 2026-05-22  
**Scope:** `GridDungeon.Core` boundaries inside `griddungeon-game`; no non-Unity extraction, no second-repo split unless a second Unity project appears.

**Related:** [05-class-design MVP1](../05-class-design-mvp1.md), [04-tech-notes](../04-tech-notes.md), [game-phase](../02-systems/game-phase.md), [architecture principles](../../.cursor/rules/architecture-design-principles.mdc), game repo [Assets/Scripts/README](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/README.md), [Assets/Tests/README](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Tests/README.md).

---

## Goals

| Goal | How this plan supports it |
|------|---------------------------|
| **One formula, one owner** | Keep combat/map/save *rules* in Core; Unity presentation in Runtime/UI |
| **Fast Edit Mode feedback** | Core-only tests for simulators; Runtime only when wiring requires it |
| **Low ceremony for MVP1** | Stay monolithic in one Unity project until reuse is real |
| **Optional second Unity title later** | Clear trigger + folder layout for embedded UPM, without doing it early |

---

## Current state (baseline)

**Strengths**

- `GridDungeon.Core.asmdef` uses `noEngineReferences: true`; no `UnityEngine` in Core sources.
- Dependency direction is correct: Tests/UI/Runtime → Core, not the reverse.
- Domain-organized tests (`Combat/`, `Map/`, `GameFlow/`, …) match namespaces.
- Content crosses layers as DTOs (`SkillData`, `StatusData`, …); ScriptableObjects stay in Runtime.

**Friction (acceptable today, costly if ignored)**

- **Game-specific campaign logic** lives in Core (`Campaign/S1CampaignResolver`, `S1FloorKeys`, S1 flags on `CampaignSaveData`).
- **Class design** mentions “CI without headless Unity,” but tests still run **only** via Unity Test Runner; there is no standalone test project (fine for Unity-only).
- Some tests reference **Runtime** for layout/codec/phase wiring — correct for integration, but blurs “rules vs glue” when auditing coverage.
- Save shapes use `[Serializable]` + list-encoded dictionaries for **Unity `JsonUtility`** — correct for this game; not a portable wire format (not a goal here).

---

## Principles (locked for this plan)

1. **Unity-only** — No `.csproj` / `dotnet test` extraction unless team explicitly revisits (out of scope).
2. **YAGNI on packaging** — No UPM package until a **second Unity project** needs shared Core.
3. **SRP per assembly** — Core = rules + DTOs; Runtime = Unity lifecycle + content assets; UI = Toolkit views.
4. **Campaign is content, not engine** — S1-specific constants and gates stay grouped and named so they can move to `GridDungeon.Campaign.S1` later without a repo-wide rename.
5. **Fix boundaries in the area you touch** — No drive-by “extract everything” passes during unrelated tickets.

---

## Phase 0 — Now (MVP1, single project)

**Intent:** Strengthen boundaries in place; zero new repos or packages.

### 0.1 Core hygiene (ongoing)

| Task | Owner / when | Done when |
|------|----------------|-----------|
| New **pure rules** → `Assets/Scripts/Core/` (simulator or model), not Runtime | Any combat/map/save ticket | PR has no new `UnityEngine` in Core |
| New **Unity-only** behaviour → Runtime or UI | Scene, SO, presenter, input | No `MonoBehaviour` in Core |
| Map content IDs through **DTOs** at Core boundaries | Content/features | Runtime calls `ContentDatabase.To*Data()`; Core methods take structs/DTOs |
| Avoid duplicating formulas in Runtime “for UI” | Combat HUD, map, etc. | UI reads state; Core already computed values |

### 0.2 Folder semantics (document + enforce lightly)

| Core area | Responsibility | Not responsible for |
|-----------|----------------|---------------------|
| `Core/Simulators/` | Deterministic rules (damage, AGI, reveal, retreat, protocol math) | Animation, input, scene objects |
| `Core/Models/`, `Core/Content/` | Battle/exploration models and data shapes | ScriptableObject assets |
| `Core/Campaign/` | S1 story gates, floor keys, spawn constants | Generic reusable campaign framework |
| `Core/SaveData/` | Save DTOs + mappers used by both layers | File I/O paths (Runtime `SaveSystem`) |

**Action:** When adding S2+ campaign code, use `Core/Campaign/S2/` (or similar) rather than expanding `S1CampaignResolver` with unrelated acts. Target shape for neutral spawn DTO + per-stratum policy: [ADR 025](../decisions/025-campaign-exploration-target.md) (proposed stub).

### 0.3 Tests (Unity Edit Mode)

| Task | Priority | Done when |
|------|----------|-----------|
| Prefer **Core-only usings** for new simulator tests | High | Fixture under `Tests/<Domain>/` references only `GridDungeon.Core.*` |
| Tag Runtime-dependent tests clearly (name or comment) | Medium | e.g. `MapSystemRevealTests`, `GamePhaseControllerTests` — reader knows why Runtime is required |
| Run domain suites before closing Core-touching issues | Per ticket | Test plan lists `Tests → <Domain> → <Fixture>` ([Tests README](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Tests/README.md)) |
| Do **not** add CLI batch tests while Editor is open | Always | Per team rule; user runs Test Runner |

### 0.4 Documentation alignment

| Task | Priority |
|------|----------|
| Treat class design “CI without headless Unity” as **aspirational** until a second harness exists | Low |
| Link this plan from [05-class-design](../05-class-design-mvp1.md) assembly table | Done in same PR as this file |
| Game repo Scripts README points here for assembly strategy | Done in same PR |

### Phase 0 exit criteria

- [ ] No new upward references (Core → Runtime/UI).
- [ ] New simulator tests added in the matching `Tests/<Domain>/` folder with domain category.
- [ ] Campaign-specific edits stay under `Core/Campaign/` (or new campaign subfolder).

---

## Phase 1 — Hardening (before MVP1 ship or during combat/map polish)

**Intent:** Make Core easier to audit and split later, without packaging.

### 1.1 Audit: Core vs game-specific

Run a one-time pass (can be a single doc issue or spike):

| Bucket | Examples today | Recommendation |
|--------|----------------|----------------|
| **Reusable simulators** | `DamageCalculator`, `TurnQueueBuilder`, `MapRevealCalculator` | Keep in Core root / `Simulators/` |
| **Grid primitives** | `GridPosition`, `GridMovement`, `FacingDirection` | Keep in Core |
| **S1 campaign** | `S1CampaignResolver`, `S1FloorKeys`, B1F spawn constants | Keep grouped; document “optional package slice” |
| **Save schema** | `SaveGame`, `CampaignSaveData` | Keep in Core for MVP1; version fields if schema changes |

**Deliverable:** Short table in this doc’s appendix (or a GitHub issue checklist) listing each `Core/` top-level folder and “generic vs S1 vs save schema.”

### 1.2 Reduce accidental Runtime leakage into Core

| Check | Action if violated |
|-------|-------------------|
| Core `.cs` files import `GridDungeon.Runtime` | Remove; move type or introduce DTO |
| Core calls `ScriptableObject` or `FindObjectOfType` | Move to Runtime adapter |
| Duplicate combat math in Runtime | Delete duplicate; call Core simulator |

### 1.3 Test coverage gaps (suggested priorities)

| Area | Suggested fixture focus |
|------|-------------------------|
| Combat round pipeline | `CombatSimulatorTests`, `ActionResolverTests` as features land |
| Protocol / Synchro edge cases | `ProtocolResolverTests` |
| Save round-trip | `SaveGameMapperTests`, `SaveGameJsonSerializerTests` (Runtime serializer OK) |
| Map reveal | `MapRevealCalculatorTests` (Core); `MapSystemRevealTests` (Runtime integration) |

### 1.4 Optional: Tests asmdef split (defer unless pain)

**Only if** Edit Mode recompiles become painful or you need “Core tests only” filter:

- `GridDungeon.Tests.Core.asmdef` → references **Core only**
- `GridDungeon.Tests.Integration.asmdef` → references Core + Runtime

Default: **keep single `GridDungeon.Tests`** for MVP1 (KISS).

### Phase 1 exit criteria

- [ ] Audit table completed (folder → generic / S1 / save).
- [ ] Zero Core → Runtime references.
- [ ] Known integration tests documented in [Tests README](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Tests/README.md) (optional “Runtime required” column).

---

## Phase 2 — Second Unity project (triggered, not scheduled)

**Trigger:** A second Unity repo needs the same combat/map rules (sequel, shared prototype, tools project).

**Do not start Phase 2** for “maybe someday” — packaging cost (versioning, breaking changes, two manifests) only pays off with two consumers.

### 2.1 Package layout (embedded UPM)

```
Packages/
  com.miramocha.griddungeon-core/
    package.json
    Runtime/                    # Unity convention; still pure C#
      GridDungeon.Core.asmdef
      (today's Core/*.cs)
```

Optional sibling package:

```
  com.miramocha.griddungeon-campaign-s1/
    (Core/Campaign/* + S1 save bootstrap if shared)
```

### 2.2 Consumer project

```
YourGame.Runtime.asmdef  →  references GridDungeon.Core
YourGame.UI.asmdef       →  references YourGame.Runtime
```

- Copy **patterns**, not Runtime/UI, from `griddungeon-game`.
- Per-game: `ContentDatabase`, scenes, campaign package choice.

### 2.3 Versioning

| Rule | Rationale |
|------|-----------|
| Semver on package | Breaking DTO/simulator signature = major bump |
| Changelog in package | Consumers know save/combat migrations |
| Pin git URL or local path in `manifest.json` | Until API stable |

### Phase 2 exit criteria

- [ ] Second project compiles against package without copying `Assets/Scripts/Core/`.
- [ ] Shared Edit Mode tests run in **both** projects OR shared test package referenced once.

---

## Explicit non-goals

| Non-goal | Reason |
|----------|--------|
| Extract Core to non-Unity .NET | User scope: Unity-only |
| Publish to Unity Asset Store / npm | No consumer yet |
| Generic “grid dungeon engine” API | Domain model is Grid Dungeon–specific |
| Move simulators to Runtime for Inspector convenience | Breaks testability and SRP |
| Headless `dotnet test` for Core in MVP1 | Duplicates harness; team uses Editor Test Runner |

---

## Decision log (when to revisit)

| Question | Revisit when |
|----------|----------------|
| Split `GridDungeon.Tests` asmdef? | Edit Mode compile time > ~30s routinely, or need Core-only CI job **with Unity closed** |
| Extract `GridDungeon.Campaign.S1` package? | Second project shares S1; otherwise keep in game Core |
| Change save wire format? | Cross-game save sharing or non-JsonUtility serializer — new ADR |
| Update “CI without Unity” wording in class design? | Phase 2 package + optional second test harness exists |

---

## Suggested ticket breakdown (GitHub)

Copy into issues as needed:

1. **Spike:** Core folder audit table (Phase 1.1) — 1–2h  
2. **Chore:** Add “Runtime required” notes to Tests README for integration fixtures  
3. **Rule:** PR checklist — “Core change? Test plan lists `Tests → <Domain>`”  
4. **Future:** Embedded UPM package (Phase 2) — only after second project confirmed  

---

## Appendix — Quick reference

### Assembly dependency (target)

```
GridDungeon.Tests  →  Core, Runtime (integration only where needed)
GridDungeon.UI     →  Runtime
GridDungeon.Runtime →  Core
GridDungeon.Core   →  (none)
```

### Where new code goes

| You are implementing… | Put it in… |
|-------------------------|------------|
| Damage / hit / status tick | `Core/Simulators/` |
| AGI order, action resolve | `Core/Simulators/` |
| Hub shop UI | `UI/` + Runtime service |
| FOE patrol step on grid | `Runtime/Exploration/`; retreat *cell math* in Core |
| B1F tutorial blocker cell | `Core/Campaign/` |
| ScriptableObject skill | `Runtime/Content/` + DTO in Core |

### Links

- Implementation tree: [05-class-design MVP1 § MVP1 folder tree](../05-class-design-mvp1.md)
- Phase ownership: [game-phase.md](../02-systems/game-phase.md)
- ADR 017 (phase controller): [017-game-phase-controller](../../decisions/017-game-phase-controller.md)
