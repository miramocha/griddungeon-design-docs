# Editor Agent test — examples

## By ticket type (handoff — use `-Category` only)

### Combat simulator change

```powershell
.\tools\request-compile-status.ps1
.\tools\request-test-status.ps1 -Category Combat
```

### UI picker / UITK view

```powershell
.\tools\request-test-status.ps1 -Category UI
```

### Exploration + map (two domains)

```powershell
.\tools\request-test-status.ps1 -Category Exploration
.\tools\request-test-status.ps1 -Category Map
```

### Game flow / save / phase

```powershell
.\tools\request-test-status.ps1 -Category GameFlow
```

### Editor / agent package tests

Package tests live under `Miraluna.Editor.Agent.Tests`. Prefer **Test Runner → Edit Mode** on that assembly, or `-Category Content` if wired — do **not** use `-Fixture AgentActionDtoTests` for agent handoff.

## Failure triage

Exit **1** — script prints failures; also open `Logs/last-test.json`:

```json
{
  "ok": false,
  "failures": [
    {
      "testName": "GridDungeon.Tests.Combat.FooTests.Bar_Expected",
      "message": "Expected: 3\n  But was: 2",
      "stackTrace": "..."
    }
  ]
}
```

- Fix test or production code; re-run the same `-Category`.
- If failure is unrelated flake, note in PR — do not claim full domain green without re-run.

Exit **3** — Unity not claiming:

1. Confirm Editor focused on `griddungeon-game`
2. Check **Package Manager** shows `com.miraluna.editor-agent`
3. Menu smoke: **Tools → Miraluna → Request Test Run**
4. Retry CLI with `-Category`

Exit **2** — timeout on large domain:

```powershell
.\tools\request-test-status.ps1 -Category UI -TimeoutSeconds 900
```

Stay on `-Category` — do not narrow to `-Fixture` / `-Test` for handoff (brittle / can hang).

## Local debug only (not agent handoff)

User explicitly iterating on one class or method:

```powershell
.\tools\list-edit-mode-tests.ps1
.\tools\request-test-status.ps1 -Fixture DamageCalculatorTests
.\tools\request-test-status.ps1 -Test DamageCalculatorTests.ApplyDamage_SubtractsHp
```

Agents skip these unless the user asks.

## Editor closed (exception path)

User confirms Editor **closed**:

```powershell
# Example — adjust UNITY_EDITOR_PATH and version
& $env:UNITY_EDITOR_PATH -batchmode -nographics -projectPath D:\MiraGameDev\griddungeon-game `
  -runTests -testPlatform editmode -testCategory Combat -logFile Logs\editmode-combat.log
```

Do not use while Editor has the project open.

## Play Mode (out of scope for this skill)

```powershell
# Editor must be closed; not Editor Agent
-runTests -testPlatform playmode -testCategory PlayMode
```

Or Test Runner **PlayMode** tab manually.
