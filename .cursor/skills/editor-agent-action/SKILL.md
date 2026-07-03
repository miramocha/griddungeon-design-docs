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

Authority: [griddungeon-game tools/README.md](../../../griddungeon-game/tools/README.md), [GridDungeonEditorAgentActionCatalog.cs](../../../griddungeon-game/Assets/Scripts/Editor/AgentActions/GridDungeonEditorAgentActionCatalog.cs).

Complements **editor-agent-test** (Edit Mode tests) and compile checks via `request-compile-status.ps1`.

## When to use

- User says **list agent tools**, **run create-dev-bootstrap**, **regen Dev Bootstrap**, **ensure content database** from agent/CLI
- Agent needs to discover `-ToolName` values before invoking one

## Workflow

```powershell
cd D:\MiraGameDev\griddungeon-game

.\tools\list-agent-tools.ps1
.\tools\request-tool-status.ps1 -ToolName create-dev-bootstrap
.\tools\request-agent.ps1 -Action Invoke -ToolName ensure-content-database
```

Legacy `-ActionId` still works on request scripts.

## Exit codes

| Exit | Meaning |
|------|---------|
| **0** | Success |
| **1** | Handler failure — read `Logs/last-action.json` |
| **2** | Timeout |
| **3** | Editor did not claim request |

## Common ToolNames

| ToolName | Purpose |
|----------|---------|
| `list-agent-actions` | Meta — list all tool names |
| `create-dev-bootstrap` | Regenerate Dev Bootstrap scene |
| `ensure-content-database` | Full ContentDatabase ensure |
| `ensure-dev-slime-battle-prefab` | DevSlimeBattle prefab + enemy refs |

Full table: [griddungeon-game tools/README.md](../../../griddungeon-game/tools/README.md).

## Resources

- Examples: [examples.md](examples.md)
- Package: [com.miraluna.editor-agent/README.md](../../../com.miraluna.editor-agent/README.md)
