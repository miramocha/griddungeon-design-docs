# Editor Agent tools — examples

## List all tool names

```powershell
cd D:\MiraGameDev\griddungeon-game
.\tools\list-agent-tools.ps1
```

## Regenerate Dev Bootstrap (combat arena plane + slot wiring)

After changing `DevSceneWireCombat` or combat spawn wiring:

```powershell
.\tools\request-compile-status.ps1
.\tools\request-tool-status.ps1 -ToolName create-dev-bootstrap
```

Expected: `Assets/Scenes/DevBootstrap.unity` in `createdAssetPaths`.

## Content + battle prefab (post-clone)

```powershell
.\tools\request-tool-status.ps1 -ToolName ensure-content-database
.\tools\request-tool-status.ps1 -ToolName ensure-dev-slime-battle-prefab
```

## Play Mode exploration scene

```powershell
.\tools\request-tool-status.ps1 -ToolName create-play-mode-exploration-scene
```

Updates committed `Assets/PlayModeTests/Scenes/PlayModeExploration.unity`.

## Floor art / transition authoring

```powershell
.\tools\request-tool-status.ps1 -ToolName create-all-dev-floor-art-prefabs
.\tools\request-tool-status.ps1 -ToolName create-stairs-default-beat-prefab
.\tools\request-tool-status.ps1 -ToolName sync-floor-transition-default-beats
```

## Failure triage

Exit **1** — read JSON:

```powershell
.\tools\read-action-status.ps1
```

Exit **3** — Unity not open on project; focus Editor and retry.

Exit **2** — increase timeout:

```powershell
.\tools\request-tool-status.ps1 -ToolName ensure-content-database -TimeoutSeconds 600
```

## Typical agent handoff order

```powershell
.\tools\request-compile-status.ps1
.\tools\request-test-status.ps1 -Category Combat
# optional scene regen when wiring changed:
.\tools\request-tool-status.ps1 -ToolName create-dev-bootstrap
```
