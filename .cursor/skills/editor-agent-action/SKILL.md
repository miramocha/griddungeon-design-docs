---
name: editor-agent-action
description: >-
  Lists and runs Grid Dungeon batch-safe editor menu tools via Miraluna Editor
  Agent (list-agent-tools.ps1, request-tool-status.ps1). Use when the user
  asks to run create-dev-bootstrap, ensure-content-database, list agent tools,
  or regenerate scenes/content from CLI while Unity Editor stays open.
---

# Editor Agent — list / invoke editor tools

Runs **registered GridDungeon editor tools** inside the **open** Unity Editor via [`com.miraluna.editor-agent`](../../../com.miraluna.editor-agent) + `GridDungeonEditorAgentActionCatalog`.

Authority: [tools/README.md](../../../tools/README.md), [GridDungeonEditorAgentActionCatalog.cs](../../../Assets/Scripts/Editor/AgentActions/GridDungeonEditorAgentActionCatalog.cs).

Complements **editor-agent-test** (Edit Mode tests) and **request-compile-status** (compile).

## When to use

- User says **list agent tools**, **run create-dev-bootstrap**, **regen Dev Bootstrap**, **ensure content database** from agent/CLI
- After changing `DevSceneWireCombat`, scene wiring, or content ensure menus — run matching tool instead of asking user to click menu
- Agent needs fresh `DevBootstrap.unity` or Play Mode exploration scene (local, gitignored)
- Discover which `-ToolName` values exist before calling one

## When not to use

| Case | Use instead |
|------|-------------|
| **Compile check** | `request-compile-status.ps1` |
| **Edit Mode tests** | **editor-agent-test** skill → `request-test-status.ps1` |
| **Editor closed** | Unity batch `-executeMethod` entries in [tools/README.md](../../../tools/README.md) (separate Unity process) |
| Menu opens **window** or **modal dialog** | Not in catalog — run manually in Editor or add batch-safe entry to catalog first |
| **Play Mode** QA (F3 combat) | Manual Play Mode — not an agent tool |

## Prerequisites

1. Unity Editor open on **griddungeon-game** with `com.miraluna.editor-agent` resolved.
2. If exit **3** (unclaimed): focus Unity, wait for import, retry.
3. Do **not** run compile, test, and tool requests in parallel — one at a time.

## Workflow

```
- [ ] 1. (Optional) list-agent-tools — pick ToolName
- [ ] 2. request-tool-status.ps1 -ToolName <name>
- [ ] 3. Exit 0 → read message / createdAssetPaths in Logs/last-action.json
- [ ] 4. Exit 1 → read error; fix and retry
```

### Step 1 — List registered tools

From **griddungeon-game** root:

```powershell
cd D:\MiraGameDev\griddungeon-game

.\tools\list-agent-tools.ps1

# equivalent
.\tools\request-action-status.ps1 -ToolName list-agent-actions
.\tools\request-agent.ps1 -Action Invoke -ToolName list-agent-actions
```

Success message body: tab-separated `toolName` + menu path per line.

### Step 2 — Invoke a tool

```powershell
.\tools\request-tool-status.ps1 -ToolName create-dev-bootstrap

# umbrella
.\tools\request-agent.ps1 -Action Invoke -ToolName ensure-content-database

# slow ensure — raise timeout (default 120s)
.\tools\request-tool-status.ps1 -ToolName ensure-content-database -TimeoutSeconds 300
```

### Step 3 — Exit codes

| Exit | Meaning | Action |
|------|---------|--------|
| **0** | Tool succeeded | OK — cite in handoff if user asked for regen |
| **1** | Handler returned failure or exception | Read `error` / `message` in `Logs/last-action.json` |
| **2** | Timeout | Editor busy — increase `-TimeoutSeconds`, retry |
| **3** | Editor did not claim request | Open project in Unity |

Read last result without re-running:

```powershell
.\tools\read-action-status.ps1
```

Structured output: `Logs/last-action.json` (`ok`, `toolName`, `message`, `createdAssetPaths`, `error`).

## Common ToolNames

| ToolName | Purpose |
|----------|---------|
| `list-agent-actions` | Meta — list all tool names |
| `create-dev-bootstrap` | Regenerate `Assets/Scenes/DevBootstrap.unity` |
| `create-play-mode-exploration-scene` | Regenerate Play Mode exploration scene |
| `ensure-content-database` | Full ContentDatabase ensure |
| `ensure-dev-slime-battle-prefab` | DevSlimeBattle prefab + enemy refs |
| `ensure-story-events` | S1 story event assets |
| `ensure-campaign-flag-registry` | Campaign flag registry asset |

Full table: [tools/README.md § request-action-status](../../../tools/README.md).

## Add a new tool

1. Ensure menu/batch entry is **batch-safe** (no `DisplayDialog`, no `GetWindow`).
2. Add one row in `GridDungeonEditorAgentActionCatalog.cs` (`DelegateGridDungeonEditorAgentAction` or `GridDungeonEditorAgentActionBase` subclass).
3. Run `list-agent-tools` to verify registration.
4. Append row to [tools/README.md](../../../tools/README.md) tool table.

## Reporting

- **Do not claim success** unless exit **0** or user confirmed menu run.
- Scene regen (`create-dev-bootstrap`) overwrites **local** gitignored scene — expected.

## Resources

- Examples: [examples.md](examples.md)
- Package: [com.miraluna.editor-agent/README.md](../../../com.miraluna.editor-agent/README.md)
