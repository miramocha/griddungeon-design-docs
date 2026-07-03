# Editor Agent tools — examples

See [griddungeon-game examples](../../../griddungeon-game/.cursor/skills/editor-agent-action/examples.md) for full recipes.

```powershell
cd D:\MiraGameDev\griddungeon-game

.\tools\list-agent-tools.ps1
.\tools\request-tool-status.ps1 -ToolName create-dev-bootstrap
.\tools\request-agent.ps1 -Action Invoke -ToolName ensure-content-database
```
