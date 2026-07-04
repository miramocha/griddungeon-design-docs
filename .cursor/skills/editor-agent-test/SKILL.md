---
name: editor-agent-test
description: >-
  Runs Grid Dungeon Edit Mode tests via Miraluna Editor Agent while Unity Editor
  stays open (request-test-status.ps1 -Category). Use when verifying tests after
  .cs changes, before ticket handoff, or when the user asks to run tests from CLI.
  Default scope is domain category only — not -Fixture/-Test (brittle). Edit Mode
  only — not Play Mode or batch -runTests.
---

# Editor Agent — run Edit Mode tests

Runs **Edit Mode** tests inside the **open** Unity Editor via [`com.miraluna.editor-agent`](../../../com.miraluna.editor-agent). No second Unity process.

Authority: [tools/README.md](../../../tools/README.md), [unity-no-cli-tests-while-editor-open.mdc](../../rules/unity-no-cli-tests-while-editor-open.mdc), [unity-compile-status-agent.mdc](../../rules/unity-compile-status-agent.mdc).

Complements **test-plan-grid-dungeon** (test plan prose) — this skill owns **execution**. For editor menu actions (scene regen, content ensure), use **editor-agent-action**.

## When to use

- After changing `Assets/Tests/**` or code covered by Edit Mode fixtures
- Before handoff / closing a ticket that lists automated Edit Mode verification
- User says **run tests**, **run Edit Mode tests**, **request-test-status**, or names a domain (`Combat`, `UI`, …)
- Agent needs green tests but Editor is open (do **not** use `Unity.exe -batchmode -runTests`)

## When not to use

| Case | Use instead |
|------|-------------|
| **Play Mode** (`Assets/PlayModeTests/**`) | Test Runner Play Mode tab, or batch `-testPlatform playmode` with **Editor closed** |
| Editor **closed** | `Unity.exe -runTests -testPlatform editmode -testCategory <Domain>` |
| **Compile-only** change with no test touch | `request-compile-status.ps1` only |
| User has Editor **closed** and wants batch | Confirm closed, then batch `-runTests` |
| **Single fixture or method** during handoff | Use **`-Category <Domain>`** — `-Fixture` / `-Test` are brittle and can hang; reserve for user-requested local debug |

## Prerequisites

1. Unity Editor open on **griddungeon-game** with `com.miraluna.editor-agent` resolved (`Packages/manifest.json`).
2. If exit **3** (unclaimed): focus Unity, wait for package import, retry.
3. Do **not** run compile and test requests at the same time — run compile first if `.cs` changed, then tests.

## Workflow (handoff default)

```
- [ ] 1. Pick -Category from diff/ticket (one domain per run)
- [ ] 2. Run request-test-status.ps1 -Category <Domain> only
- [ ] 3. Interpret exit code; on failure read Logs/last-test.json or script output
- [ ] 4. Fix failures; re-run same category until exit 0 or report blockers
- [ ] 5. Do not claim green unless exit 0 or user confirmed Test Runner green
```

Multiple domains touched → run **each `-Category` separately**. Do **not** substitute `-Fixture` or `-Test` for handoff verification.

### Step 1 — Pick `-Category`

Use **one primary domain** per run ([unity-test-categories.mdc](../../rules/unity-test-categories.mdc)). Constants match `TestCategories` in `Assets/Tests/Shared/TestCategories.cs`.

| Diff under | `-Category` |
|------------|-------------|
| `Assets/Tests/Combat/` | `Combat` |
| `Assets/Tests/UI/` | `UI` |
| `Assets/Tests/Exploration/` | `Exploration` |
| `Assets/Tests/Map/`, `Assets/Tests/Editor/FloorEditor/` | `Map` |
| `Assets/Tests/Foe/` | `Foe` |
| `Assets/Tests/GameFlow/` | `GameFlow` |
| `Assets/Tests/Inventory/` | `Inventory` |
| `Assets/Tests/Progression/` | `Progression` |
| `Assets/Tests/Core/` | `Core` |
| `Assets/Tests/Editor/` (content DB) | `Content` |
| `com.miraluna.editor-agent` package tests | `Content` or run **Test Runner** manually on `Miraluna.Editor.Agent.Tests` |

More examples: [examples.md](examples.md).

### Step 2 — Run (category only)

From **griddungeon-game** root:

```powershell
cd D:\MiraGameDev\griddungeon-game

# Handoff default — domain filter
.\tools\request-test-status.ps1 -Category Combat

# Multiple domains from diff
.\tools\request-test-status.ps1 -Category UI
.\tools\request-test-status.ps1 -Category Combat

# Umbrella
.\tools\request-agent.ps1 -Action Test -Category UI

# Long suite — raise timeout (still -Category)
.\tools\request-test-status.ps1 -Category Combat -TimeoutSeconds 600
```

**Do not use for agent handoff:** `-Fixture`, `-Test`, `-TestName` — resolution/async list can hang or report misleading counts. User may request them for local iteration; agents stick to `-Category`.

Discover fixture names (docs / manual Test Runner only): `.\tools\list-edit-mode-tests.ps1`.

Default timeout: **300s**. Poll interval: 500ms (package default).

### Step 3 — Exit codes

| Exit | Meaning | Action |
|------|---------|--------|
| **0** | All tests passed | OK to cite in test plan |
| **1** | Failures or inconclusive | Print `failures[]`; fix and re-run same `-Category` |
| **2** | Timeout | Editor busy or suite too large — increase `-TimeoutSeconds`; do **not** switch to `-Fixture` for handoff |
| **3** | Editor did not claim request | Open project in Unity; confirm package installed |

Read last status without re-running:

```powershell
.\tools\read-test-status.ps1
```

Structured output: `Logs/last-test.json` (`summary`, `failures[]`, `error`).

### Step 4 — After `.cs` handoff (typical order)

```powershell
.\tools\request-compile-status.ps1
.\tools\request-test-status.ps1 -Category <DomainFromDiff>
```

## Reporting

- **Do not invent pass** — exit 0 or user-reported Test Runner green only ([ticket-test-documentation.mdc](../../rules/ticket-test-documentation.mdc)).
- In test plans, cite: `request-test-status.ps1 -Category <Domain>` for agent runs; optional `Tests → <Domain> → <Fixture>` when user ran Test Runner manually.
- On failure, include `testName` + `message` from `failures[]` in issue/PR notes.

## Manual fallback

If Editor Agent unavailable: **Window → General → Test Runner → Edit Mode** → expand `Tests → <Domain>` (full domain) or `Tests → <Domain> → <Fixture>` ([Assets/Tests/README.md](../../../Assets/Tests/README.md)).

## Resources

- Command examples: [examples.md](examples.md)
- Package install / JSON files: [com.miraluna.editor-agent/README.md](../../../com.miraluna.editor-agent/README.md)
